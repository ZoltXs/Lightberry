"""
Enhanced System Info Module for LightBerry OS
Professional system information display with real hardware data
"""

import pygame
import os
import platform
import psutil
import subprocess
from datetime import datetime, timedelta
from config.constants import *

class SystemInfo:
    def __init__(self, os_instance):
        self.os = os_instance
        self.init_system_info()
    
    def init_system_info(self):
        """Initialize system info state"""
        self.selected_item = 0
        self.scroll_offset = 0
        self.visible_items = 8
        self.system_data = {}
        self.refresh_interval = 5  # seconds
        self.last_refresh = 0
        
        # Get initial system data
        self.refresh_system_data()
    
    def refresh_system_data(self):
        """Refresh system information"""
        try:
            # Basic system info
            self.system_data = {
                "os_name": self.get_os_info(),
                "hostname": platform.node(),
                "architecture": platform.machine(),
                "cpu_info": self.get_cpu_info(),
                "memory_info": self.get_memory_info(),
                "storage_info": self.get_storage_info(),
                "uptime": self.get_uptime(),
                "network_info": self.get_network_info(),
                "temperature": self.get_temperature(),
                "load_average": self.get_load_average(),
                "processes": self.get_process_count(),
                "author": "Light Berry: N@xs",
                "version": "LightBerry OS v1.0",
                "build_date": datetime.now().strftime("%Y-%m-%d"),
                "kernel": self.get_kernel_version()
            }
            
            self.last_refresh = pygame.time.get_ticks() / 1000
            
        except Exception as e:
            print(f"Error refreshing system data: {e}")
    
    def get_os_info(self):
        """Get operating system information"""
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        return line.split('=')[1].strip('"')
        except:
            pass
        return f"{platform.system()} {platform.release()}"
    
    def get_cpu_info(self):
        """Get CPU information"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('model name'):
                        cpu_name = line.split(':')[1].strip()
                        break
                else:
                    cpu_name = "Unknown CPU"
            
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            freq_info = ""
            if cpu_freq:
                freq_info = f" @ {cpu_freq.current:.0f}MHz"
            
            return {
                "name": cpu_name,
                "cores": cpu_count,
                "usage": cpu_usage,
                "frequency": freq_info
            }
        except:
            return {
                "name": "Unknown CPU",
                "cores": 1,
                "usage": 0,
                "frequency": ""
            }
    
    def get_memory_info(self):
        """Get memory information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "total": self.format_bytes(memory.total),
                "available": self.format_bytes(memory.available),
                "used": self.format_bytes(memory.used),
                "percent": memory.percent,
                "swap_total": self.format_bytes(swap.total),
                "swap_used": self.format_bytes(swap.used),
                "swap_percent": swap.percent
            }
        except:
            return {
                "total": "Unknown",
                "available": "Unknown",
                "used": "Unknown",
                "percent": 0,
                "swap_total": "0 B",
                "swap_used": "0 B",
                "swap_percent": 0
            }
    
    def get_storage_info(self):
        """Get real storage information"""
        try:
            disk_usage = psutil.disk_usage('/')
            
            return {
                "total": self.format_bytes(disk_usage.total),
                "used": self.format_bytes(disk_usage.used),
                "free": self.format_bytes(disk_usage.free),
                "percent": (disk_usage.used / disk_usage.total) * 100
            }
        except:
            return {
                "total": "Unknown",
                "used": "Unknown",
                "free": "Unknown",
                "percent": 0
            }
    
    def get_uptime(self):
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
            
            uptime_delta = timedelta(seconds=uptime_seconds)
            days = uptime_delta.days
            hours, remainder = divmod(uptime_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "Unknown"
    
    def get_network_info(self):
        """Get network information"""
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_io_counters()
            
            active_interfaces = []
            for interface, addrs in interfaces.items():
                if interface != 'lo':  # Skip loopback
                    for addr in addrs:
                        if addr.family == 2:  # IPv4
                            active_interfaces.append({
                                "name": interface,
                                "ip": addr.address
                            })
            
            return {
                "interfaces": active_interfaces,
                "bytes_sent": self.format_bytes(stats.bytes_sent),
                "bytes_recv": self.format_bytes(stats.bytes_recv)
            }
        except:
            return {
                "interfaces": [],
                "bytes_sent": "0 B",
                "bytes_recv": "0 B"
            }
    
    def get_temperature(self):
        """Get system temperature"""
        try:
            # Try to read CPU temperature from common locations
            temp_paths = [
                '/sys/class/thermal/thermal_zone0/temp',
                '/sys/class/hwmon/hwmon0/temp1_input',
                '/sys/class/hwmon/hwmon1/temp1_input'
            ]
            
            for path in temp_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        temp = int(f.read().strip())
                        # Convert from millidegrees to degrees
                        if temp > 1000:
                            temp = temp / 1000
                        return f"{temp:.1f}°C"
            
            return "N/A"
        except:
            return "N/A"
    
    def get_load_average(self):
        """Get system load average"""
        try:
            load1, load5, load15 = os.getloadavg()
            return f"{load1:.2f}, {load5:.2f}, {load15:.2f}"
        except:
            return "N/A"
    
    def get_process_count(self):
        """Get number of running processes"""
        try:
            return len(psutil.pids())
        except:
            return 0
    
    def get_kernel_version(self):
        """Get kernel version"""
        try:
            return platform.release()
        except:
            return "Unknown"
    
    def format_bytes(self, bytes_value):
        """Format bytes to human readable format"""
        if bytes_value == 0:
            return "0 B"
        
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(bytes_value)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def handle_events(self, event):
        """Handle system info events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            
            elif event.key == pygame.K_UP:
                self.selected_item = max(0, self.selected_item - 1)
                if self.selected_item < self.scroll_offset:
                    self.scroll_offset = max(0, self.scroll_offset - 1)
            
            elif event.key == pygame.K_DOWN:
                max_items = len(self.get_info_items())
                self.selected_item = min(max_items - 1, self.selected_item + 1)
                if self.selected_item >= self.scroll_offset + self.visible_items:
                    self.scroll_offset = min(max_items - self.visible_items, self.scroll_offset + 1)
            
            elif event.key == pygame.K_r:
                self.refresh_system_data()
        
        return None
    
    def get_info_items(self):
        """Get formatted info items for display"""
        items = []
        
        # System Information
        items.append(("System", ""))
        items.append(("  OS", self.system_data.get("os_name", "Unknown")))
        items.append(("  Hostname", self.system_data.get("hostname", "Unknown")))
        items.append(("  Architecture", self.system_data.get("architecture", "Unknown")))
        items.append(("  Kernel", self.system_data.get("kernel", "Unknown")))
        items.append(("  Uptime", self.system_data.get("uptime", "Unknown")))
        items.append(("", ""))
        
        # CPU Information
        cpu_info = self.system_data.get("cpu_info", {})
        items.append(("CPU", ""))
        items.append(("  Model", cpu_info.get("name", "Unknown")))
        items.append(("  Cores", str(cpu_info.get("cores", 1))))
        items.append(("  Usage", f"{cpu_info.get('usage', 0):.1f}%"))
        items.append(("  Frequency", cpu_info.get("frequency", "")))
        items.append(("", ""))
        
        # Memory Information
        memory_info = self.system_data.get("memory_info", {})
        items.append(("Memory", ""))
        items.append(("  Total", memory_info.get("total", "Unknown")))
        items.append(("  Used", memory_info.get("used", "Unknown")))
        items.append(("  Available", memory_info.get("available", "Unknown")))
        items.append(("  Usage", f"{memory_info.get('percent', 0):.1f}%"))
        items.append(("", ""))
        
        # Storage Information
        storage_info = self.system_data.get("storage_info", {})
        items.append(("Storage", ""))
        items.append(("  Total", storage_info.get("total", "Unknown")))
        items.append(("  Used", storage_info.get("used", "Unknown")))
        items.append(("  Free", storage_info.get("free", "Unknown")))
        items.append(("  Usage", f"{storage_info.get('percent', 0):.1f}%"))
        items.append(("", ""))
        
        # Network Information
        network_info = self.system_data.get("network_info", {})
        items.append(("Network", ""))
        for interface in network_info.get("interfaces", []):
            items.append(("  " + interface["name"], interface["ip"]))
        items.append(("  Sent", network_info.get("bytes_sent", "0 B")))
        items.append(("  Received", network_info.get("bytes_recv", "0 B")))
        items.append(("", ""))
        
        # System Status
        items.append(("Status", ""))
        items.append(("  Temperature", self.system_data.get("temperature", "N/A")))
        items.append(("  Load Avg", self.system_data.get("load_average", "N/A")))
        items.append(("  Processes", str(self.system_data.get("processes", 0))))
        items.append(("", ""))
        
        # About
        items.append(("About", ""))
        items.append(("  Version", self.system_data.get("version", "Unknown")))
        items.append(("  Author", self.system_data.get("author", "Unknown")))
        items.append(("  Build Date", self.system_data.get("build_date", "Unknown")))
        
        return items
    
    def update(self):
        """Update system info state"""
        current_time = pygame.time.get_ticks() / 1000
        if current_time - self.last_refresh > self.refresh_interval:
            self.refresh_system_data()
    
    def draw(self, screen):
        """Draw system info interface"""
        # Header
        header_text = "System Information"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Last updated
        last_update_text = f"Updated: {datetime.now().strftime('%H:%M:%S')}"
        last_update_surface = self.os.font_s.render(last_update_text, True, HIGHLIGHT_COLOR)
        last_update_x = SCREEN_WIDTH - last_update_surface.get_width() - 10
        screen.blit(last_update_surface, (last_update_x, 25))
        
        # Info items
        items = self.get_info_items()
        visible_items = items[self.scroll_offset:self.scroll_offset + self.visible_items]
        
        start_y = 45
        line_height = 20
        
        for i, (label, value) in enumerate(visible_items):
            item_index = self.scroll_offset + i
            y_pos = start_y + i * line_height
            
            # Selection background
            if item_index == self.selected_item and label:
                selection_rect = pygame.Rect(5, y_pos - 2, SCREEN_WIDTH - 10, line_height)
                pygame.draw.rect(screen, SELECTED_COLOR, selection_rect)
            
            # Category headers (bold)
            if label and not label.startswith("  ") and value == "":
                label_surface = self.os.font_m.render(label, True, ACCENT_COLOR)
                screen.blit(label_surface, (10, y_pos))
            
            # Info items
            elif label and value:
                # Label
                label_surface = self.os.font_m.render(label, True, TEXT_COLOR)
                screen.blit(label_surface, (10, y_pos))
                
                # Value
                value_text = str(value)
                if len(value_text) > 25:
                    value_text = value_text[:25] + "..."
                
                # Color coding for certain values
                if "%" in value_text:
                    try:
                        percent = float(value_text.replace("%", ""))
                        if percent > 80:
                            value_color = ERROR_COLOR
                        elif percent > 60:
                            value_color = WARNING_COLOR
                        else:
                            value_color = SUCCESS_COLOR
                    except:
                        value_color = TEXT_COLOR
                else:
                    value_color = TEXT_COLOR
                
                value_surface = self.os.font_m.render(value_text, True, value_color)
                value_x = SCREEN_WIDTH - value_surface.get_width() - 10
                screen.blit(value_surface, (value_x, y_pos))
        
        # Scroll indicators
        if self.scroll_offset > 0:
            up_text = "↑ More info above"
            up_surface = self.os.font_tiny.render(up_text, True, HIGHLIGHT_COLOR)
            screen.blit(up_surface, (10, 40))
        
        if self.scroll_offset + self.visible_items < len(items):
            down_text = "↓ More info below"
            down_surface = self.os.font_tiny.render(down_text, True, HIGHLIGHT_COLOR)
            screen.blit(down_surface, (10, start_y + self.visible_items * line_height))
        
        # Controls
        controls = [
            "↑↓: Navigate",
            "R: Refresh",
            "ESC: Back"
        ]
        
        control_y = SCREEN_HEIGHT - 25
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + i * 120
            screen.blit(control_surface, (control_x, control_y))
        
        # Progress bars for usage
        self.draw_usage_bars(screen)
    
    def draw_usage_bars(self, screen):
        """Draw usage bars for CPU, memory, and storage"""
        bar_width = 100
        bar_height = 8
        bar_x = SCREEN_WIDTH - bar_width - 10
        
        # CPU usage bar
        cpu_info = self.system_data.get("cpu_info", {})
        cpu_usage = cpu_info.get("usage", 0)
        if cpu_usage > 0:
            cpu_y = 60
            self.draw_progress_bar(screen, bar_x, cpu_y, bar_width, bar_height, cpu_usage)
        
        # Memory usage bar
        memory_info = self.system_data.get("memory_info", {})
        memory_usage = memory_info.get("percent", 0)
        if memory_usage > 0:
            memory_y = 140
            self.draw_progress_bar(screen, bar_x, memory_y, bar_width, bar_height, memory_usage)
        
        # Storage usage bar
        storage_info = self.system_data.get("storage_info", {})
        storage_usage = storage_info.get("percent", 0)
        if storage_usage > 0:
            storage_y = 180
            self.draw_progress_bar(screen, bar_x, storage_y, bar_width, bar_height, storage_usage)
    
    def draw_progress_bar(self, screen, x, y, width, height, percentage):
        """Draw a progress bar"""
        # Background
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, (x, y, width, height))
        
        # Progress
        progress_width = int((percentage / 100) * width)
        
        # Color based on usage
        if percentage > 80:
            progress_color = ERROR_COLOR
        elif percentage > 60:
            progress_color = WARNING_COLOR
        else:
            progress_color = SUCCESS_COLOR
        
        pygame.draw.rect(screen, progress_color, (x, y, progress_width, height))
        
        # Border
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, (x, y, width, height), 1)
    
    def save_data(self):
        """Save system info data"""
        return {
            "refresh_interval": self.refresh_interval
        }
    
    def load_data(self, data):
        """Load system info data"""
        self.refresh_interval = data.get("refresh_interval", 5)
