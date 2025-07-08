"""
Hardware integration manager for LightBerry OS
Real hardware control for WiFi, Bluetooth, and system operations
"""

import subprocess
import os
import re
import json
from datetime import datetime

class HardwareManager:
    def __init__(self):
        self.wifi_interface = "wlan0"
        self.bluetooth_enabled = False
        self.wifi_networks = []
        self.bluetooth_devices = []
    
    def scan_wifi_networks(self):
        """Scan for available WiFi networks"""
        try:
            # Use iwlist to scan for networks
            result = subprocess.run(['iwlist', self.wifi_interface, 'scan'], 
                                  capture_output=True, text=True)
            
            networks = []
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                current_network = {}
                
                for line in lines:
                    line = line.strip()
                    
                    if 'ESSID:' in line:
                        essid = line.split('ESSID:')[1].strip('"')
                        if essid and essid != '<hidden>':
                            current_network['name'] = essid
                    
                    elif 'Quality=' in line:
                        quality_match = re.search(r'Quality=(\d+/\d+)', line)
                        if quality_match:
                            quality = quality_match.group(1)
                            current_network['quality'] = quality
                    
                    elif 'Encryption key:' in line:
                        encrypted = 'on' in line
                        current_network['encrypted'] = encrypted
                    
                    elif 'IE: WPA' in line:
                        current_network['security'] = 'WPA'
                    
                    elif 'IE: WPA2' in line:
                        current_network['security'] = 'WPA2'
                    
                    elif line.startswith('Cell') and current_network:
                        if 'name' in current_network:
                            networks.append(current_network)
                        current_network = {}
                
                # Add last network
                if current_network and 'name' in current_network:
                    networks.append(current_network)
            
            self.wifi_networks = networks
            return networks
            
        except Exception as e:
            print(f"Error scanning WiFi: {e}")
            return []
    
    def connect_wifi(self, ssid, password, security='WPA2'):
        """Connect to WiFi network"""
        try:
            # Create wpa_supplicant configuration
            config_content = f"""
network={{
    ssid="{ssid}"
    psk="{password}"
    key_mgmt=WPA-PSK
}}
"""
            
            # Write temporary config
            with open('/tmp/wpa_temp.conf', 'w') as f:
                f.write(config_content)
            
            # Connect using wpa_supplicant
            result = subprocess.run([
                'wpa_supplicant', '-B', '-i', self.wifi_interface,
                '-c', '/tmp/wpa_temp.conf'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Get IP address
                dhcp_result = subprocess.run(['dhclient', self.wifi_interface], 
                                           capture_output=True, text=True)
                
                # Clean up
                os.remove('/tmp/wpa_temp.conf')
                
                return dhcp_result.returncode == 0
            
            return False
            
        except Exception as e:
            print(f"Error connecting to WiFi: {e}")
            return False
    
    def disconnect_wifi(self):
        """Disconnect from WiFi"""
        try:
            subprocess.run(['killall', 'wpa_supplicant'], 
                         capture_output=True, text=True)
            subprocess.run(['ip', 'addr', 'flush', 'dev', self.wifi_interface], 
                         capture_output=True, text=True)
            return True
        except Exception as e:
            print(f"Error disconnecting WiFi: {e}")
            return False
    
    def get_wifi_status(self):
        """Get current WiFi status"""
        try:
            result = subprocess.run(['iwconfig', self.wifi_interface], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout
                if 'ESSID:' in output:
                    essid_match = re.search(r'ESSID:"([^"]*)"', output)
                    if essid_match:
                        return {
                            'connected': True,
                            'ssid': essid_match.group(1),
                            'interface': self.wifi_interface
                        }
            
            return {'connected': False}
            
        except Exception as e:
            print(f"Error getting WiFi status: {e}")
            return {'connected': False}
    
    def enable_bluetooth(self):
        """Enable Bluetooth"""
        try:
            result = subprocess.run(['bluetoothctl', 'power', 'on'], 
                                  capture_output=True, text=True)
            self.bluetooth_enabled = result.returncode == 0
            return self.bluetooth_enabled
        except Exception as e:
            print(f"Error enabling Bluetooth: {e}")
            return False
    
    def disable_bluetooth(self):
        """Disable Bluetooth"""
        try:
            result = subprocess.run(['bluetoothctl', 'power', 'off'], 
                                  capture_output=True, text=True)
            self.bluetooth_enabled = result.returncode != 0
            return not self.bluetooth_enabled
        except Exception as e:
            print(f"Error disabling Bluetooth: {e}")
            return False
    
    def scan_bluetooth_devices(self):
        """Scan for Bluetooth devices"""
        try:
            # Start scan
            subprocess.run(['bluetoothctl', 'scan', 'on'], 
                         capture_output=True, text=True)
            
            # Wait a moment for scan
            import time
            time.sleep(3)
            
            # Get devices
            result = subprocess.run(['bluetoothctl', 'devices'], 
                                  capture_output=True, text=True)
            
            devices = []
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.startswith('Device'):
                        parts = line.split(' ', 2)
                        if len(parts) >= 3:
                            devices.append({
                                'address': parts[1],
                                'name': parts[2]
                            })
            
            # Stop scan
            subprocess.run(['bluetoothctl', 'scan', 'off'], 
                         capture_output=True, text=True)
            
            self.bluetooth_devices = devices
            return devices
            
        except Exception as e:
            print(f"Error scanning Bluetooth: {e}")
            return []
    
    def connect_bluetooth_device(self, address):
        """Connect to Bluetooth device"""
        try:
            # Pair first
            pair_result = subprocess.run(['bluetoothctl', 'pair', address], 
                                       capture_output=True, text=True)
            
            if pair_result.returncode == 0:
                # Trust device
                subprocess.run(['bluetoothctl', 'trust', address], 
                             capture_output=True, text=True)
                
                # Connect
                connect_result = subprocess.run(['bluetoothctl', 'connect', address], 
                                              capture_output=True, text=True)
                
                return connect_result.returncode == 0
            
            return False
            
        except Exception as e:
            print(f"Error connecting Bluetooth device: {e}")
            return False
    
    def get_system_info(self):
        """Get system information"""
        try:
            info = {}
            
            # CPU info
            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = f.read()
                model_match = re.search(r'model name\s*:\s*(.+)', cpu_info)
                if model_match:
                    info['cpu'] = model_match.group(1).strip()
            
            # Memory info
            with open('/proc/meminfo', 'r') as f:
                mem_info = f.read()
                total_match = re.search(r'MemTotal:\s*(\d+)\s*kB', mem_info)
                if total_match:
                    total_mb = int(total_match.group(1)) // 1024
                    info['memory'] = f"{total_mb} MB"
            
            # Storage info
            result = subprocess.run(['df', '-h', '/'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 4:
                        info['storage_total'] = parts[1]
                        info['storage_used'] = parts[2]
                        info['storage_free'] = parts[3]
            
            # OS info
            try:
                with open('/etc/os-release', 'r') as f:
                    os_info = f.read()
                    name_match = re.search(r'PRETTY_NAME="([^"]*)"', os_info)
                    if name_match:
                        info['os'] = name_match.group(1)
            except:
                info['os'] = 'Linux'
            
            # Uptime
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
                uptime_hours = int(uptime_seconds // 3600)
                uptime_minutes = int((uptime_seconds % 3600) // 60)
                info['uptime'] = f"{uptime_hours}h {uptime_minutes}m"
            
            return info
            
        except Exception as e:
            print(f"Error getting system info: {e}")
            return {}
    
    def restart_system(self):
        """Restart the system"""
        try:
            subprocess.run(['sudo', 'reboot'], capture_output=True, text=True)
            return True
        except Exception as e:
            print(f"Error restarting system: {e}")
            return False
    
    def shutdown_system(self):
        """Shutdown the system"""
        try:
            subprocess.run(['sudo', 'shutdown', '-h', 'now'], 
                         capture_output=True, text=True)
            return True
        except Exception as e:
            print(f"Error shutting down system: {e}")
            return False
    
    def get_network_info(self):
        """Get network information"""
        try:
            info = {}
            
            # Get IP address
            result = subprocess.run(['ip', 'addr', 'show', self.wifi_interface], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', result.stdout)
                if ip_match:
                    info['ip'] = ip_match.group(1)
            
            # Get gateway
            result = subprocess.run(['ip', 'route', 'show', 'default'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                gateway_match = re.search(r'default via (\d+\.\d+\.\d+\.\d+)', result.stdout)
                if gateway_match:
                    info['gateway'] = gateway_match.group(1)
            
            return info
            
        except Exception as e:
            print(f"Error getting network info: {e}")
            return {}
