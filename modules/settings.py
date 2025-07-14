"""
Enhanced Settings Module for LightBerry OS
Professional settings with WiFi, Bluetooth, and account management
Fixed black screen issues and improved functionality
"""

import pygame
import threading
import time
import sys
import os

# Add the parent directory to the path to find config module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.constants import *
except ImportError:
    # Fallback constants if import fails
    SCREEN_WIDTH = 400
    SCREEN_HEIGHT = 240
    ACCENT_COLOR = (0, 150, 255)
    TEXT_COLOR = (255, 255, 255)
    SELECTED_COLOR = (50, 50, 50)
    BUTTON_COLOR = (30, 30, 30)
    BUTTON_BORDER_COLOR = (100, 100, 100)
    SUCCESS_COLOR = (0, 255, 0)
    ERROR_COLOR = (255, 0, 0)
    WARNING_COLOR = (255, 255, 0)
    HIGHLIGHT_COLOR = (200, 200, 200)

class Settings:
    def __init__(self, os_instance):
        self.os = os_instance
        self.init_settings()
    
    def init_settings(self):
        """Initialize settings state"""
        self.settings_categories = [
            "WiFi", "Bluetooth", "Mail Accounts"
        ]
        
        self.selected_category = 0
        self.selected_item = 0
        self.mode = "categories"  # "categories", "wifi", "bluetooth", "mail", "system"
        self.scroll_offset = 0
        
        # WiFi settings
        self.wifi_networks = []
        self.wifi_scanning = False
        self.wifi_selected = 0
        self.wifi_password = ""
        self.wifi_input_mode = False
        self.wifi_connection_status = "Ready"
        self.wifi_current_network = None
        
        # Bluetooth settings
        self.bluetooth_devices = []
        self.bluetooth_scanning = False
        self.bluetooth_selected = 0
        self.bluetooth_enabled = False
        self.bluetooth_connection_status = "Disabled"
        
        # Mail accounts
        self.mail_accounts = []
        self.mail_editing_account = None
        self.mail_input_mode = False
        self.mail_input_field = "name"
        self.mail_input_fields = ["name", "email", "password", "imap_server", "imap_port", "smtp_server", "smtp_port"]
        self.mail_field_index = 0
        self.mail_temp_account = {}
        
        # System settings
        self.system_settings = {
            "screen_timeout": 30,
            "auto_update": True,
            "debug_mode": False
        }
        
        # Text input
        self.text_cursor_visible = True
        self.text_cursor_timer = 0
        
        # Load existing settings
        self.load_settings()
        
        # Check current WiFi status
        self.check_wifi_status()
    
    def load_settings(self):
        """Load settings from data manager"""
        try:
            if hasattr(self.os, 'data_manager'):
                data = self.os.data_manager.get_module_data("Settings")
                self.mail_accounts = data.get("mail_accounts", [])
                self.system_settings.update(data.get("system_settings", {}))
                self.bluetooth_enabled = data.get("bluetooth_enabled", False)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to data manager"""
        try:
            if hasattr(self.os, 'data_manager'):
                data = {
                    "mail_accounts": self.mail_accounts,
                    "system_settings": self.system_settings,
                    "bluetooth_enabled": self.bluetooth_enabled
                }
                self.os.data_manager.set_module_data("Settings", data)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def check_wifi_status(self):
        """Check current WiFi connection status"""
        try:
            if hasattr(self.os, 'hardware_manager'):
                status = self.os.hardware_manager.get_wifi_status()
                if status.get('connected', False):
                    self.wifi_connection_status = f"Connected to {status.get('ssid', 'Unknown')}"
                    self.wifi_current_network = status.get('ssid', 'Unknown')
                else:
                    self.wifi_connection_status = "Disconnected"
                    self.wifi_current_network = None
        except Exception as e:
            print(f"Error checking WiFi status: {e}")
            self.wifi_connection_status = "Status unknown"
    
    def handle_events(self, event):
        """Handle settings events"""
        try:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return self.exit_mode()
                
                elif self.mode == "categories":
                    self.handle_category_events(event)
                
                elif self.mode == "wifi":
                    self.handle_wifi_events(event)
                
                elif self.mode == "bluetooth":
                    self.handle_bluetooth_events(event)
                
                elif self.mode == "mail":
                    self.handle_mail_events(event)
                
                elif self.mode == "system":
                    self.handle_system_events(event)
        except Exception as e:
            print(f"Error handling events: {e}")
        
        return None
    
    def exit_mode(self):
        """Exit current mode or operation"""
        if self.mode == "categories":
            return "back"
        elif self.wifi_input_mode:
            self.wifi_input_mode = False
            self.wifi_password = ""
            return None
        elif self.mail_input_mode:
            self.cancel_mail_edit()
            return None
        else:
            self.mode = "categories"
            self.selected_item = 0
            self.scroll_offset = 0
            return None
    
    def handle_category_events(self, event):
        """Handle category selection events"""
        if event.key == pygame.K_UP:
            self.selected_category = max(0, self.selected_category - 1)
        
        elif event.key == pygame.K_DOWN:
            self.selected_category = min(len(self.settings_categories) - 1, self.selected_category + 1)
        
        elif event.key == pygame.K_RETURN:
            category = self.settings_categories[self.selected_category]
            if category == "WiFi":
                self.enter_wifi_mode()
            elif category == "Bluetooth":
                self.enter_bluetooth_mode()
            elif category == "Mail Accounts":
                self.mode = "mail"
                self.selected_item = 0
            elif category == "System":
                self.mode = "system"
                self.selected_item = 0
    
    def enter_wifi_mode(self):
        """Enter WiFi settings mode"""
        self.mode = "wifi"
        self.selected_item = 0
        self.wifi_selected = 0
        self.check_wifi_status()
        # Auto-scan when entering WiFi mode
        self.start_wifi_scan()
    
    def enter_bluetooth_mode(self):
        """Enter Bluetooth settings mode"""
        self.mode = "bluetooth"
        self.selected_item = 0
        self.bluetooth_selected = 0
        # Check if Bluetooth is enabled
        self.check_bluetooth_status()
        if self.bluetooth_enabled:
            self.start_bluetooth_scan()
    
    def check_bluetooth_status(self):
        """Check Bluetooth status"""
        try:
            if hasattr(self.os, 'hardware_manager'):
                # Try to enable Bluetooth to check status
                self.bluetooth_enabled = self.os.hardware_manager.enable_bluetooth()
                if self.bluetooth_enabled:
                    self.bluetooth_connection_status = "Enabled"
                else:
                    self.bluetooth_connection_status = "Disabled"
        except Exception as e:
            print(f"Error checking Bluetooth status: {e}")
            self.bluetooth_connection_status = "Error"
    
    def handle_wifi_events(self, event):
        """Handle WiFi settings events"""
        if self.wifi_input_mode:
            self.handle_wifi_password_input(event)
        else:
            if event.key == pygame.K_UP:
                self.wifi_selected = max(0, self.wifi_selected - 1)
            
            elif event.key == pygame.K_DOWN:
                max_selection = max(0, len(self.wifi_networks) - 1)
                self.wifi_selected = min(max_selection, self.wifi_selected + 1)
            
            elif event.key == pygame.K_RETURN:
                self.connect_to_selected_wifi()
            
            elif event.key == pygame.K_r:
                self.start_wifi_scan()
            
            elif event.key == pygame.K_d:
                self.disconnect_wifi()
    
    def handle_wifi_password_input(self, event):
        """Handle password input for WiFi"""
        if event.key == pygame.K_RETURN:
            self.connect_to_wifi()
        elif event.key == pygame.K_BACKSPACE:
            self.wifi_password = self.wifi_password[:-1]
        elif event.key == pygame.K_ESCAPE:
            self.wifi_input_mode = False
            self.wifi_password = ""
        else:
            char = event.unicode
            if char.isprintable() and len(self.wifi_password) < 50:
                self.wifi_password += char
    
    def connect_to_selected_wifi(self):
        """Connect to the selected WiFi network"""
        if self.wifi_networks and self.wifi_selected < len(self.wifi_networks):
            network = self.wifi_networks[self.wifi_selected]
            if network.get("encrypted", False):
                self.wifi_input_mode = True
                self.wifi_password = ""
            else:
                self.connect_to_wifi()
    
    def handle_bluetooth_events(self, event):
        """Handle Bluetooth settings events"""
        if event.key == pygame.K_UP:
            self.bluetooth_selected = max(0, self.bluetooth_selected - 1)
        
        elif event.key == pygame.K_DOWN:
            max_selection = max(0, len(self.bluetooth_devices) - 1)
            self.bluetooth_selected = min(max_selection, self.bluetooth_selected + 1)
        
        elif event.key == pygame.K_RETURN:
            self.connect_to_selected_bluetooth()
        
        elif event.key == pygame.K_r:
            if self.bluetooth_enabled:
                self.start_bluetooth_scan()
            else:
                self.bluetooth_connection_status = "Bluetooth is disabled"
        
        elif event.key == pygame.K_t:
            self.toggle_bluetooth()
    
    def toggle_bluetooth(self):
        """Toggle Bluetooth on or off"""
        try:
            if hasattr(self.os, 'hardware_manager'):
                if self.bluetooth_enabled:
                    self.os.hardware_manager.disable_bluetooth()
                    self.bluetooth_enabled = False
                    self.bluetooth_connection_status = "Disabled"
                    self.bluetooth_devices = []
                else:
                    self.bluetooth_enabled = self.os.hardware_manager.enable_bluetooth()
                    if self.bluetooth_enabled:
                        self.bluetooth_connection_status = "Enabled"
                        self.start_bluetooth_scan()
                    else:
                        self.bluetooth_connection_status = "Failed to enable"
                
                self.save_settings()
        except Exception as e:
            print(f"Error toggling Bluetooth: {e}")
            self.bluetooth_connection_status = f"Error: {e}"
    
    def start_wifi_scan(self):
        """Start WiFi network scan"""
        if not self.wifi_scanning:
            self.wifi_scanning = True
            self.wifi_networks = []
            self.wifi_connection_status = "Scanning..."
            
            def scan_thread():
                try:
                    if hasattr(self.os, 'hardware_manager'):
                        networks = self.os.hardware_manager.scan_wifi_networks()
                        self.wifi_networks = networks if networks else []
                        if self.wifi_networks:
                            self.wifi_connection_status = f"Found {len(self.wifi_networks)} networks"
                        else:
                            self.wifi_connection_status = "No networks found"
                    else:
                        self.wifi_connection_status = "Hardware manager not available"
                except Exception as e:
                    print(f"WiFi scan error: {e}")
                    self.wifi_connection_status = f"Scan failed: {str(e)[:30]}"
                finally:
                    self.wifi_scanning = False
            
            thread = threading.Thread(target=scan_thread)
            thread.daemon = True
            thread.start()
    
    def connect_to_wifi(self):
        """Connect to selected WiFi network"""
        if self.wifi_networks and self.wifi_selected < len(self.wifi_networks):
            network = self.wifi_networks[self.wifi_selected]
            ssid = network.get("name", "")
            password = self.wifi_password
            
            self.wifi_connection_status = f"Connecting to {ssid}..."
            
            def connect_thread():
                try:
                    if hasattr(self.os, 'hardware_manager'):
                        success = self.os.hardware_manager.connect_wifi(ssid, password)
                        if success:
                            self.wifi_connection_status = f"Connected to {ssid}"
                            self.wifi_current_network = ssid
                        else:
                            self.wifi_connection_status = f"Failed to connect to {ssid}"
                    else:
                        self.wifi_connection_status = "Hardware manager not available"
                except Exception as e:
                    print(f"WiFi connection error: {e}")
                    self.wifi_connection_status = f"Connection error: {str(e)[:30]}"
                finally:
                    self.wifi_input_mode = False
                    self.wifi_password = ""
            
            thread = threading.Thread(target=connect_thread)
            thread.daemon = True
            thread.start()
    
    def disconnect_wifi(self):
        """Disconnect from WiFi"""
        try:
            if hasattr(self.os, 'hardware_manager'):
                self.os.hardware_manager.disconnect_wifi()
                self.wifi_connection_status = "Disconnected"
                self.wifi_current_network = None
            else:
                self.wifi_connection_status = "Hardware manager not available"
        except Exception as e:
            print(f"WiFi disconnect error: {e}")
            self.wifi_connection_status = f"Disconnect failed: {str(e)[:30]}"
    
    def start_bluetooth_scan(self):
        """Start Bluetooth device scan"""
        if not self.bluetooth_scanning and self.bluetooth_enabled:
            self.bluetooth_scanning = True
            self.bluetooth_devices = []
            self.bluetooth_connection_status = "Scanning..."
            
            def scan_thread():
                try:
                    if hasattr(self.os, 'hardware_manager'):
                        devices = self.os.hardware_manager.scan_bluetooth_devices()
                        self.bluetooth_devices = devices if devices else []
                        if self.bluetooth_devices:
                            self.bluetooth_connection_status = f"Found {len(self.bluetooth_devices)} devices"
                        else:
                            self.bluetooth_connection_status = "No devices found"
                    else:
                        self.bluetooth_connection_status = "Hardware manager not available"
                except Exception as e:
                    print(f"Bluetooth scan error: {e}")
                    self.bluetooth_connection_status = f"Scan failed: {str(e)[:30]}"
                finally:
                    self.bluetooth_scanning = False
            
            thread = threading.Thread(target=scan_thread)
            thread.daemon = True
            thread.start()
        elif not self.bluetooth_enabled:
            self.bluetooth_connection_status = "Bluetooth is disabled"
    
    def connect_to_selected_bluetooth(self):
        """Connect to the selected Bluetooth device"""
        if self.bluetooth_devices and self.bluetooth_selected < len(self.bluetooth_devices):
            device = self.bluetooth_devices[self.bluetooth_selected]
            address = device.get("address", "")
            name = device.get("name", "Unknown")
            
            self.bluetooth_connection_status = f"Connecting to {name}..."
            
            def connect_thread():
                try:
                    if hasattr(self.os, 'hardware_manager'):
                        success = self.os.hardware_manager.connect_bluetooth_device(address)
                        if success:
                            self.bluetooth_connection_status = f"Connected to {name}"
                        else:
                            self.bluetooth_connection_status = f"Failed to connect to {name}"
                    else:
                        self.bluetooth_connection_status = "Hardware manager not available"
                except Exception as e:
                    print(f"Bluetooth connection error: {e}")
                    self.bluetooth_connection_status = f"Connection error: {str(e)[:30]}"
            
            thread = threading.Thread(target=connect_thread)
            thread.daemon = True
            thread.start()
    
    def handle_mail_events(self, event):
        """Handle mail account events"""
        if self.mail_input_mode:
            if event.key == pygame.K_TAB:
                self.mail_field_index = (self.mail_field_index + 1) % len(self.mail_input_fields)
                self.mail_input_field = self.mail_input_fields[self.mail_field_index]
            
            elif event.key == pygame.K_UP:
                self.mail_field_index = max(0, self.mail_field_index - 1)
                self.mail_input_field = self.mail_input_fields[self.mail_field_index]
            
            elif event.key == pygame.K_DOWN:
                self.mail_field_index = min(len(self.mail_input_fields) - 1, self.mail_field_index + 1)
                self.mail_input_field = self.mail_input_fields[self.mail_field_index]
            
            elif event.key == pygame.K_RETURN:
                self.save_mail_account()
            
            elif event.key == pygame.K_BACKSPACE:
                current_value = self.mail_temp_account.get(self.mail_input_field, "")
                self.mail_temp_account[self.mail_input_field] = current_value[:-1]
            
            else:
                char = event.unicode
                if char.isprintable():
                    current_value = self.mail_temp_account.get(self.mail_input_field, "")
                    if len(current_value) < 100:
                        self.mail_temp_account[self.mail_input_field] = current_value + char
        else:
            if event.key == pygame.K_UP:
                self.selected_item = max(0, self.selected_item - 1)
            
            elif event.key == pygame.K_DOWN:
                self.selected_item = min(len(self.mail_accounts), self.selected_item + 1)
            
            elif event.key == pygame.K_RETURN:
                if self.selected_item < len(self.mail_accounts):
                    self.edit_mail_account(self.selected_item)
                else:
                    self.add_mail_account()
            
            elif event.key == pygame.K_a:
                self.add_mail_account()
            
            elif event.key == pygame.K_d:
                if self.selected_item < len(self.mail_accounts):
                    del self.mail_accounts[self.selected_item]
                    self.selected_item = min(self.selected_item, len(self.mail_accounts) - 1)
                    self.save_settings()
    
    def handle_system_events(self, event):
        """Handle system settings events"""
        if event.key == pygame.K_UP:
            self.selected_item = max(0, self.selected_item - 1)
        
        elif event.key == pygame.K_DOWN:
            system_items = list(self.system_settings.keys())
            self.selected_item = min(len(system_items) - 1, self.selected_item + 1)
        
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self.toggle_system_setting()
        
        elif event.key == pygame.K_LEFT:
            self.adjust_system_setting(-1)
        
        elif event.key == pygame.K_RIGHT:
            self.adjust_system_setting(1)
    
    def add_mail_account(self):
        """Add new mail account"""
        self.mail_input_mode = True
        self.mail_editing_account = None
        self.mail_field_index = 0
        self.mail_input_field = self.mail_input_fields[0]
        self.mail_temp_account = {
            "name": "",
            "email": "",
            "password": "",
            "imap_server": "",
            "imap_port": "993",
            "smtp_server": "",
            "smtp_port": "587",
            "use_ssl": True
        }
    
    def edit_mail_account(self, index):
        """Edit existing mail account"""
        if index < len(self.mail_accounts):
            self.mail_input_mode = True
            self.mail_editing_account = index
            self.mail_field_index = 0
            self.mail_input_field = self.mail_input_fields[0]
            self.mail_temp_account = self.mail_accounts[index].copy()
    
    def save_mail_account(self):
        """Save mail account"""
        if self.mail_temp_account.get("name") and self.mail_temp_account.get("email"):
            if self.mail_editing_account is not None:
                self.mail_accounts[self.mail_editing_account] = self.mail_temp_account.copy()
            else:
                self.mail_accounts.append(self.mail_temp_account.copy())
            
            self.save_settings()
            self.cancel_mail_edit()
    
    def cancel_mail_edit(self):
        """Cancel mail account editing"""
        self.mail_input_mode = False
        self.mail_editing_account = None
        self.mail_temp_account = {}
        self.mail_field_index = 0
    
    def toggle_system_setting(self):
        """Toggle boolean system setting"""
        settings_keys = list(self.system_settings.keys())
        if self.selected_item < len(settings_keys):
            key = settings_keys[self.selected_item]
            value = self.system_settings[key]
            
            if isinstance(value, bool):
                self.system_settings[key] = not value
                self.save_settings()
    
    def adjust_system_setting(self, direction):
        """Adjust numeric system setting"""
        settings_keys = list(self.system_settings.keys())
        if self.selected_item < len(settings_keys):
            key = settings_keys[self.selected_item]
            value = self.system_settings[key]
            
            if isinstance(value, int):
                if key == "screen_timeout":
                    self.system_settings[key] = max(5, min(300, value + direction * 5))
                
                self.save_settings()
    
    def update(self):
        """Update settings state"""
        # Update text cursor
        self.text_cursor_timer += 1
        if self.text_cursor_timer >= 30:
            self.text_cursor_visible = not self.text_cursor_visible
            self.text_cursor_timer = 0
    
    def draw(self, screen):
        """Draw settings interface"""
        try:
            # Clear screen
            screen.fill((0, 0, 0))
            
            if self.mode == "categories":
                self.draw_categories(screen)
            elif self.mode == "wifi":
                self.draw_wifi_settings(screen)
            elif self.mode == "bluetooth":
                self.draw_bluetooth_settings(screen)
            elif self.mode == "mail":
                self.draw_mail_settings(screen)
            elif self.mode == "system":
                self.draw_system_settings(screen)
        except Exception as e:
            print(f"Error drawing settings: {e}")
            # Draw error message
            if hasattr(self.os, 'font_m'):
                error_surface = self.os.font_m.render(f"Error: {e}", True, ERROR_COLOR)
                screen.blit(error_surface, (10, 10))
    
    def draw_categories(self, screen):
        """Draw settings categories"""
        # Header
        header_text = "Settings"
        if hasattr(self.os, 'font_l'):
            header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        else:
            header_surface = pygame.font.Font(None, 24).render(header_text, True, ACCENT_COLOR)
        
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Categories
        start_y = 40
        font = self.os.font_m if hasattr(self.os, 'font_m') else pygame.font.Font(None, 20)
        
        for i, category in enumerate(self.settings_categories):
            y_pos = start_y + i * 25
            
            # Selection background
            if i == self.selected_category:
                cat_rect = pygame.Rect(10, y_pos - 2, SCREEN_WIDTH - 20, 22)
                pygame.draw.rect(screen, SELECTED_COLOR, cat_rect)
                pygame.draw.rect(screen, ACCENT_COLOR, cat_rect, 2)
            
            # Category text
            cat_surface = font.render(category, True, TEXT_COLOR)
            screen.blit(cat_surface, (20, y_pos))
            
            # Status indicator
            status_color = SUCCESS_COLOR
            if category == "WiFi":
                status_color = SUCCESS_COLOR if self.wifi_current_network else ERROR_COLOR
            elif category == "Bluetooth":
                status_color = SUCCESS_COLOR if self.bluetooth_enabled else ERROR_COLOR
            elif category == "Mail Accounts":
                status_color = SUCCESS_COLOR if self.mail_accounts else WARNING_COLOR
            
            pygame.draw.circle(screen, status_color, (SCREEN_WIDTH - 20, y_pos + 10), 4)
        
        # Controls
        controls = [
            "↑↓: Navigate",
            "Enter: Select",
            "ESC: Back"
        ]
        
        control_font = self.os.font_tiny if hasattr(self.os, 'font_tiny') else pygame.font.Font(None, 16)
        control_y = SCREEN_HEIGHT - 30
        for i, control in enumerate(controls):
            control_surface = control_font.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + i * 120
            screen.blit(control_surface, (control_x, control_y))
    
    def draw_wifi_settings(self, screen):
        """Draw WiFi settings"""
        # Header
        header_text = "WiFi Settings"
        font_l = self.os.font_l if hasattr(self.os, 'font_l') else pygame.font.Font(None, 24)
        header_surface = font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        font_m = self.os.font_m if hasattr(self.os, 'font_m') else pygame.font.Font(None, 20)
        font_s = self.os.font_s if hasattr(self.os, 'font_s') else pygame.font.Font(None, 16)
        
        # Status
        status_color = SUCCESS_COLOR if "Connected" in self.wifi_connection_status else HIGHLIGHT_COLOR
        status_surface = font_m.render(self.wifi_connection_status, True, status_color)
        screen.blit(status_surface, (10, 30))
        
        # Networks
        if self.wifi_scanning:
            scan_text = "Scanning for networks..."
            scan_surface = font_m.render(scan_text, True, WARNING_COLOR)
            screen.blit(scan_surface, (10, 55))
        elif not self.wifi_networks:
            no_networks_text = "No networks found - Press R to scan"
            no_networks_surface = font_m.render(no_networks_text, True, ERROR_COLOR)
            screen.blit(no_networks_surface, (10, 55))
        else:
            # Network list
            for i, network in enumerate(self.wifi_networks[:6]):  # Show max 6 networks
                y_pos = 55 + i * 25
                
                # Selection background
                if i == self.wifi_selected:
                    net_rect = pygame.Rect(10, y_pos - 2, SCREEN_WIDTH - 20, 22)
                    pygame.draw.rect(screen, SELECTED_COLOR, net_rect)
                
                # Network name
                net_name = network.get("name", "Unknown")
                net_surface = font_m.render(net_name, True, TEXT_COLOR)
                screen.blit(net_surface, (15, y_pos))
                
                # Security indicator
                if network.get("encrypted", False):
                    lock_surface = font_s.render("[LOCK]", True, WARNING_COLOR)
                    screen.blit(lock_surface, (SCREEN_WIDTH - 40, y_pos))
                
                # Signal strength
                quality = network.get("quality", "Unknown")
                quality_surface = font_s.render(str(quality), True, HIGHLIGHT_COLOR)
                screen.blit(quality_surface, (SCREEN_WIDTH - 80, y_pos + 5))
        
        # Password input
        if self.wifi_input_mode:
            input_y = SCREEN_HEIGHT - 80
            input_label = "Password:"
            input_surface = font_m.render(input_label, True, TEXT_COLOR)
            screen.blit(input_surface, (10, input_y))
            
            input_rect = pygame.Rect(10, input_y + 20, SCREEN_WIDTH - 20, 25)
            pygame.draw.rect(screen, BUTTON_COLOR, input_rect)
            pygame.draw.rect(screen, BUTTON_BORDER_COLOR, input_rect, 2)
            
            password_display = "*" * len(self.wifi_password)
            if self.text_cursor_visible:
                password_display += "|"
            
            password_surface = font_m.render(password_display, True, TEXT_COLOR)
            screen.blit(password_surface, (15, input_y + 23))
        
        # Controls
        controls = [
            "↑↓: Navigate",
            "Enter: Connect",
            "R: Refresh",
            "D: Disconnect",
            "ESC: Back"
        ]
        
        control_font = self.os.font_tiny if hasattr(self.os, 'font_tiny') else pygame.font.Font(None, 16)
        control_y = SCREEN_HEIGHT - 40
        for i, control in enumerate(controls):
            control_surface = control_font.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 3) * 125
            control_y_pos = control_y + (i // 3) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def draw_bluetooth_settings(self, screen):
        """Draw Bluetooth settings"""
        # Header
        header_text = "Bluetooth Settings"
        font_l = self.os.font_l if hasattr(self.os, 'font_l') else pygame.font.Font(None, 24)
        header_surface = font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        font_m = self.os.font_m if hasattr(self.os, 'font_m') else pygame.font.Font(None, 20)
        font_s = self.os.font_s if hasattr(self.os, 'font_s') else pygame.font.Font(None, 16)
        
        # Status
        status_text = "Enabled" if self.bluetooth_enabled else "Disabled"
        status_color = SUCCESS_COLOR if self.bluetooth_enabled else ERROR_COLOR
        status_surface = font_m.render(status_text, True, status_color)
        screen.blit(status_surface, (10, 30))
        
        # Connection status
        if self.bluetooth_connection_status:
            conn_surface = font_s.render(self.bluetooth_connection_status, True, HIGHLIGHT_COLOR)
            screen.blit(conn_surface, (10, 50))
        
        # Devices
        if not self.bluetooth_enabled:
            disabled_text = "Bluetooth is disabled - Press T to enable"
            disabled_surface = font_m.render(disabled_text, True, WARNING_COLOR)
            screen.blit(disabled_surface, (10, 80))
        elif self.bluetooth_scanning:
            scan_text = "Scanning for devices..."
            scan_surface = font_m.render(scan_text, True, WARNING_COLOR)
            screen.blit(scan_surface, (10, 80))
        elif not self.bluetooth_devices:
            no_devices_text = "No devices found - Press R to scan"
            no_devices_surface = font_m.render(no_devices_text, True, ERROR_COLOR)
            screen.blit(no_devices_surface, (10, 80))
        else:
            # Device list
            for i, device in enumerate(self.bluetooth_devices[:5]):  # Show max 5 devices
                y_pos = 80 + i * 25
                
                # Selection background
                if i == self.bluetooth_selected:
                    dev_rect = pygame.Rect(10, y_pos - 2, SCREEN_WIDTH - 20, 22)
                    pygame.draw.rect(screen, SELECTED_COLOR, dev_rect)
                
                # Device name
                dev_name = device.get("name", "Unknown Device")
                dev_surface = font_m.render(dev_name, True, TEXT_COLOR)
                screen.blit(dev_surface, (15, y_pos))
                
                # Device address
                addr = device.get("address", "Unknown")
                addr_surface = font_s.render(addr, True, HIGHLIGHT_COLOR)
                screen.blit(addr_surface, (15, y_pos + 12))
        
        # Controls
        controls = [
            "↑↓: Navigate",
            "Enter: Connect",
            "R: Scan",
            "T: Toggle BT",
            "ESC: Back"
        ]
        
        control_font = self.os.font_tiny if hasattr(self.os, 'font_tiny') else pygame.font.Font(None, 16)
        control_y = SCREEN_HEIGHT - 30
        for i, control in enumerate(controls):
            control_surface = control_font.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 3) * 125
            control_y_pos = control_y + (i // 3) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def draw_mail_settings(self, screen):
        """Draw mail account settings"""
        # Header
        header_text = "Mail Accounts"
        font_l = self.os.font_l if hasattr(self.os, 'font_l') else pygame.font.Font(None, 24)
        header_surface = font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        font_m = self.os.font_m if hasattr(self.os, 'font_m') else pygame.font.Font(None, 20)
        font_s = self.os.font_s if hasattr(self.os, 'font_s') else pygame.font.Font(None, 16)
        
        if self.mail_input_mode:
            # Account editing mode
            edit_title = "Edit Account" if self.mail_editing_account is not None else "Add Account"
            edit_surface = font_m.render(edit_title, True, ACCENT_COLOR)
            screen.blit(edit_surface, (10, 30))
            
            # Input fields
            y_offset = 55
            for i, field in enumerate(self.mail_input_fields):
                field_y = y_offset + i * 25
                
                # Field label
                field_label = field.replace("_", " ").title() + ":"
                label_surface = font_s.render(field_label, True, TEXT_COLOR)
                screen.blit(label_surface, (10, field_y))
                
                # Input field
                field_rect = pygame.Rect(80, field_y, SCREEN_WIDTH - 90, 20)
                field_color = SELECTED_COLOR if i == self.mail_field_index else BUTTON_COLOR
                pygame.draw.rect(screen, field_color, field_rect)
                pygame.draw.rect(screen, BUTTON_BORDER_COLOR, field_rect, 2)
                
                # Field value
                field_value = str(self.mail_temp_account.get(field, ""))
                if field == "password" and field_value:
                    field_value = "*" * len(field_value)
                
                if i == self.mail_field_index and self.text_cursor_visible:
                    field_value += "|"
                
                if len(field_value) > 30:
                    field_value = field_value[:30] + "..."
                
                value_surface = font_s.render(field_value, True, TEXT_COLOR)
                screen.blit(value_surface, (85, field_y + 2))
        else:
            # Account list mode
            if not self.mail_accounts:
                no_accounts_text = "No mail accounts configured"
                no_accounts_surface = font_m.render(no_accounts_text, True, WARNING_COLOR)
                screen.blit(no_accounts_surface, (10, 60))
            else:
                # Account list
                for i, account in enumerate(self.mail_accounts):
                    y_pos = 55 + i * 30
                    
                    # Selection background
                    if i == self.selected_item:
                        acc_rect = pygame.Rect(10, y_pos - 2, SCREEN_WIDTH - 20, 28)
                        pygame.draw.rect(screen, SELECTED_COLOR, acc_rect)
                    
                    # Account name
                    name_surface = font_m.render(account.get("name", "Unnamed"), True, TEXT_COLOR)
                    screen.blit(name_surface, (15, y_pos))
                    
                    # Account email
                    email_surface = font_s.render(account.get("email", ""), True, HIGHLIGHT_COLOR)
                    screen.blit(email_surface, (15, y_pos + 15))
            
            # Add new account option
            add_y = 55 + len(self.mail_accounts) * 30
            if self.selected_item == len(self.mail_accounts):
                add_rect = pygame.Rect(10, add_y - 2, SCREEN_WIDTH - 20, 22)
                pygame.draw.rect(screen, SELECTED_COLOR, add_rect)
            
            add_surface = font_m.render("+ Add New Account", True, SUCCESS_COLOR)
            screen.blit(add_surface, (15, add_y))
        
        # Controls
        if self.mail_input_mode:
            controls = [
                "Tab/↑↓: Navigate fields",
                "Enter: Save",
                "ESC: Cancel"
            ]
        else:
            controls = [
                "↑↓: Navigate",
                "Enter: Edit/Add",
                "A: Add account",
                "D: Delete",
                "ESC: Back"
            ]
        
        control_font = self.os.font_tiny if hasattr(self.os, 'font_tiny') else pygame.font.Font(None, 16)
        control_y = SCREEN_HEIGHT - 30
        for i, control in enumerate(controls):
            control_surface = control_font.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 2) * 180
            control_y_pos = control_y + (i // 2) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def draw_system_settings(self, screen):
        """Draw system settings"""
        # Header
        header_text = "System Settings"
        font_l = self.os.font_l if hasattr(self.os, 'font_l') else pygame.font.Font(None, 24)
        header_surface = font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        font_m = self.os.font_m if hasattr(self.os, 'font_m') else pygame.font.Font(None, 20)
        
        # Settings list
        settings_items = [
            ("Screen Timeout", f"{self.system_settings['screen_timeout']}s"),
            ("Auto Update", self.system_settings["auto_update"]),
            ("Debug Mode", self.system_settings["debug_mode"])
        ]
        
        for i, (label, value) in enumerate(settings_items):
            y_pos = 40 + i * 30
            
            # Selection background
            if i == self.selected_item:
                setting_rect = pygame.Rect(10, y_pos - 2, SCREEN_WIDTH - 20, 26)
                pygame.draw.rect(screen, SELECTED_COLOR, setting_rect)
            
            # Setting label
            label_surface = font_m.render(label, True, TEXT_COLOR)
            screen.blit(label_surface, (15, y_pos))
            
            # Setting value
            if isinstance(value, bool):
                value_text = "On" if value else "Off"
                value_color = SUCCESS_COLOR if value else ERROR_COLOR
            else:
                value_text = str(value)
                value_color = TEXT_COLOR
            
            value_surface = font_m.render(value_text, True, value_color)
            value_x = SCREEN_WIDTH - value_surface.get_width() - 15
            screen.blit(value_surface, (value_x, y_pos))
        
        # Controls
        controls = [
            "↑↓: Navigate",
            "Enter/Space: Toggle",
            "←→: Adjust",
            "ESC: Back"
        ]
        
        control_font = self.os.font_tiny if hasattr(self.os, 'font_tiny') else pygame.font.Font(None, 16)
        control_y = SCREEN_HEIGHT - 30
        for i, control in enumerate(controls):
            control_surface = control_font.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 2) * 180
            control_y_pos = control_y + (i // 2) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def save_data(self):
        """Save settings data"""
        return {
            "mail_accounts": self.mail_accounts,
            "system_settings": self.system_settings,
            "bluetooth_enabled": self.bluetooth_enabled
        }
    
    def load_data(self, data):
        """Load settings data"""
        self.mail_accounts = data.get("mail_accounts", [])
        self.system_settings.update(data.get("system_settings", {}))
        self.bluetooth_enabled = data.get("bluetooth_enabled", False)
