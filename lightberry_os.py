#!/usr/bin/env python3
"""
LightBerry OS - Complete Professional Operating System
Enhanced with modern UI, real hardware integration, and comprehensive functionality
Author: Light Berry N@xs
"""

import pygame
import sys
import os
import json
import subprocess
import threading
import time
import math
from datetime import datetime, date, timedelta
from config.constants import *
from utils.data_manager import DataManager
from utils.hardware_manager import HardwareManager
from utils.notification_manager import NotificationManager
from modules.calculator import Calculator
from modules.calendar_module import CalendarModule
from modules.notes import Notes
from modules.world_clock import WorldClock
from modules.weather import Weather
from modules.timer import Timer
from modules.terminal import Terminal
from modules.converter import Converter
from modules.mail import Mail
from modules.system_info import SystemInfo
from modules.settings import Settings
from modules.quit import Quit

class LightBerryOS:
    def __init__(self):
        try:
            # Initialize pygame
            pygame.init()
            
            # Configure display
            os.environ['DISPLAY'] = ':0'
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("LightBerry OS")
            
            # Configure clock
            self.clock = pygame.time.Clock()
            
            # Load fonts with better error handling
            self.load_fonts()
            
            # Initialize managers
            self.data_manager = DataManager()
            self.hardware_manager = HardwareManager()
            self.notification_manager = NotificationManager()
            
            # System state
            self.running = True
            self.current_screen = "main_menu"
            self.previous_screen = None
            
            # Screensaver
            self.last_activity = time.time()
            self.screensaver_active = False
            self.screensaver_timeout = 30
            self.screensaver_animation_time = 0
            
            # Main menu with pagination
            self.menu_items = [
                "Calculator", "Calendar", "Notes", "World Clock", 
                "Weather", "Timer", "Terminal", "Converter",
                "Mail", "System Info", "Settings", "Quit"
            ]
            
            self.selected_item_index = 0
            self.menu_page = 0
            self.items_per_page = 5
            self.total_pages = math.ceil(len(self.menu_items) / self.items_per_page)
            
            # Initialize modules
            self.init_modules()
            
            # Load persistent data
            self.load_data()
            
            # Start background threads
            self.start_background_threads()
            
            print("LightBerry OS initialized successfully")
            
        except Exception as e:
            print(f"Error initializing LightBerry OS: {e}")
            sys.exit(1)
    
    def load_fonts(self):
        """Load fonts with fallback options"""
        try:
            self.font_xl = pygame.font.Font(None, FONT_SIZE_XLARGE)
            self.font_l = pygame.font.Font(None, FONT_SIZE_LARGE)
            self.font_m = pygame.font.Font(None, FONT_SIZE_MEDIUM)
            self.font_s = pygame.font.Font(None, FONT_SIZE_SMALL)
            self.font_tiny = pygame.font.Font(None, FONT_SIZE_TINY)
        except:
            # Fallback to system fonts
            self.font_xl = pygame.font.SysFont('arial', FONT_SIZE_XLARGE, bold=True)
            self.font_l = pygame.font.SysFont('arial', FONT_SIZE_LARGE, bold=True)
            self.font_m = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM)
            self.font_s = pygame.font.SysFont('arial', FONT_SIZE_SMALL)
            self.font_tiny = pygame.font.SysFont('arial', FONT_SIZE_TINY)
    
    def init_modules(self):
        """Initialize all application modules"""
        self.modules = {
            "Calculator": Calculator(self),
            "Calendar": CalendarModule(self),
            "Notes": Notes(self),
            "World Clock": WorldClock(self),
            "Weather": Weather(self),
            "Timer": Timer(self),
            "Terminal": Terminal(self),
            "Converter": Converter(self),
            "Mail": Mail(self),
            "System Info": SystemInfo(self),
            "Settings": Settings(self),
            "Quit": Quit(self)
        }
    
    def load_data(self):
        """Load persistent data for all modules"""
        try:
            data = self.data_manager.load_data()
            for module_name, module in self.modules.items():
                if hasattr(module, 'load_data'):
                    module.load_data(data.get(module_name, {}))
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def save_data(self):
        """Save persistent data for all modules"""
        try:
            data = {}
            for module_name, module in self.modules.items():
                if hasattr(module, 'save_data'):
                    data[module_name] = module.save_data()
            self.data_manager.save_data(data)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def start_background_threads(self):
        """Start background threads for notifications and updates"""
        def notification_thread():
            while self.running:
                try:
                    # Check for calendar notifications
                    if "Calendar" in self.modules:
                        self.modules["Calendar"].check_notifications()
                    
                    # Update weather data
                    if "Weather" in self.modules:
                        self.modules["Weather"].update_weather_data()
                    
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    print(f"Background thread error: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=notification_thread, daemon=True)
        thread.start()
    
    def update_activity(self):
        """Update last activity time"""
        self.last_activity = time.time()
        if self.screensaver_active:
            self.screensaver_active = False
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # Update activity on any event
            self.update_activity()
            
            if self.screensaver_active:
                continue
            
            # Handle events based on current screen
            if self.current_screen == "main_menu":
                self.handle_main_menu_events(event)
            else:
                # Pass events to current module
                module_name = self.current_screen.replace("_", " ").title()
                if module_name in self.modules:
                    result = self.modules[module_name].handle_events(event)
                    if result == "back":
                        self.current_screen = "main_menu"
                        self.save_data()
    
    def handle_main_menu_events(self, event):
        """Handle main menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item_index = max(0, self.selected_item_index - 1)
                if self.selected_item_index < self.menu_page * self.items_per_page:
                    self.menu_page = max(0, self.menu_page - 1)
            
            elif event.key == pygame.K_DOWN:
                self.selected_item_index = min(len(self.menu_items) - 1, self.selected_item_index + 1)
                if self.selected_item_index >= (self.menu_page + 1) * self.items_per_page:
                    self.menu_page = min(self.total_pages - 1, self.menu_page + 1)
            
            elif event.key == pygame.K_LEFT:
                if self.menu_page > 0:
                    self.menu_page -= 1
                    self.selected_item_index = self.menu_page * self.items_per_page
            
            elif event.key == pygame.K_RIGHT:
                if self.menu_page < self.total_pages - 1:
                    self.menu_page += 1
                    self.selected_item_index = self.menu_page * self.items_per_page
            
            elif event.key == pygame.K_RETURN:
                selected_item = self.menu_items[self.selected_item_index]
                self.current_screen = selected_item.lower().replace(" ", "_")
                
                # Initialize module if needed
                if selected_item in self.modules:
                    if hasattr(self.modules[selected_item], 'on_enter'):
                        self.modules[selected_item].on_enter()
    
    def update(self):
        """Update system state"""
        # Check for screensaver
        if time.time() - self.last_activity > self.screensaver_timeout:
            self.screensaver_active = True
            self.screensaver_animation_time += 1
        
        # Update current module
        if not self.screensaver_active and self.current_screen != "main_menu":
            module_name = self.current_screen.replace("_", " ").title()
            if module_name in self.modules:
                if hasattr(self.modules[module_name], 'update'):
                    self.modules[module_name].update()
        
        # Update notifications
        self.notification_manager.update()
    
    def draw(self):
        """Draw current screen"""
        self.screen.fill(BACKGROUND_COLOR)
        
        if self.screensaver_active:
            self.draw_screensaver()
        elif self.current_screen == "main_menu":
            self.draw_main_menu()
        else:
            # Draw current module
            module_name = self.current_screen.replace("_", " ").title()
            if module_name in self.modules:
                self.modules[module_name].draw(self.screen)
        
        # Draw notifications
        self.notification_manager.draw(self.screen, self.font_s)
        
        pygame.display.flip()
    
    def draw_screensaver(self):
        """Draw enhanced screensaver with animations"""
        # Animated background
        time_factor = self.screensaver_animation_time * 0.1
        
        # Draw animated circles
        for i in range(3):
            radius = 30 + math.sin(time_factor + i * 2) * 15
            alpha = 100 + math.sin(time_factor + i * 1.5) * 50
            color = [int(c * (alpha / 255)) for c in ACCENT_COLOR]
            
            # Create surface for alpha blending
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, int(alpha)), (radius, radius), radius)
            
            x = SCREEN_WIDTH // 2 + math.cos(time_factor + i * 2.1) * 80
            y = SCREEN_HEIGHT // 2 + math.sin(time_factor + i * 1.8) * 60
            
            self.screen.blit(surf, (x - radius, y - radius))
        
        # Draw main title with glow effect
        title_text = "LightBerry OS"
        title_surface = self.font_xl.render(title_text, True, TEXT_COLOR)
        
        # Glow effect
        glow_surface = self.font_xl.render(title_text, True, ACCENT_COLOR)
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx != 0 or dy != 0:
                    x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2 + dx
                    y = SCREEN_HEIGHT // 2 - 40 + dy
                    self.screen.blit(glow_surface, (x, y))
        
        # Main title
        title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2
        title_y = SCREEN_HEIGHT // 2 - 40
        self.screen.blit(title_surface, (title_x, title_y))
        
        # Animated subtitle
        subtitle_alpha = 150 + math.sin(time_factor * 2) * 100
        subtitle_text = "Professional Operating System"
        subtitle_surface = self.font_m.render(subtitle_text, True, 
                                            (*ACCENT_COLOR, int(subtitle_alpha)))
        subtitle_x = SCREEN_WIDTH // 2 - subtitle_surface.get_width() // 2
        subtitle_y = title_y + 50
        self.screen.blit(subtitle_surface, (subtitle_x, subtitle_y))
        
        # Current time
        current_time = datetime.now().strftime("%H:%M:%S")
        time_surface = self.font_l.render(current_time, True, TEXT_COLOR)
        time_x = SCREEN_WIDTH // 2 - time_surface.get_width() // 2
        time_y = subtitle_y + 60
        self.screen.blit(time_surface, (time_x, time_y))
        
        # Date
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        date_surface = self.font_s.render(current_date, True, HIGHLIGHT_COLOR)
        date_x = SCREEN_WIDTH // 2 - date_surface.get_width() // 2
        date_y = time_y + 35
        self.screen.blit(date_surface, (date_x, date_y))
    
    def draw_main_menu(self):
        """Draw enhanced main menu with pagination"""
        # Draw header
        header_text = "LightBerry OS"
        header_surface = self.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        self.screen.blit(header_surface, (header_x, 10))
        
        # Draw separator line
        pygame.draw.line(self.screen, HIGHLIGHT_COLOR, (20, 45), (SCREEN_WIDTH - 20, 45), 2)
        
        # Draw menu items for current page
        start_index = self.menu_page * self.items_per_page
        end_index = min(start_index + self.items_per_page, len(self.menu_items))
        
        y_offset = 60
        item_height = 25
        
        for i, item_index in enumerate(range(start_index, end_index)):
            item = self.menu_items[item_index]
            y = y_offset + i * item_height
            
            # Draw selection background
            if item_index == self.selected_item_index:
                pygame.draw.rect(self.screen, SELECTED_COLOR, 
                               (10, y - 5, SCREEN_WIDTH - 20, item_height))
                pygame.draw.rect(self.screen, ACCENT_COLOR, 
                               (10, y - 5, SCREEN_WIDTH - 20, item_height), 2)
            
            # Draw item text
            text_color = TEXT_COLOR if item_index == self.selected_item_index else HIGHLIGHT_COLOR
            text_surface = self.font_m.render(item, True, text_color)
            self.screen.blit(text_surface, (20, y))
            
            # Draw module status indicator
            status_color = SUCCESS_COLOR if item in self.modules else ERROR_COLOR
            pygame.draw.circle(self.screen, status_color, (SCREEN_WIDTH - 30, y + 10), 5)
        
        # Draw pagination info
        if self.total_pages > 1:
            page_text = f"Page {self.menu_page + 1} of {self.total_pages}"
            page_surface = self.font_tiny.render(page_text, True, HIGHLIGHT_COLOR)
            page_x = SCREEN_WIDTH // 2 - page_surface.get_width() // 2
            self.screen.blit(page_surface, (page_x, SCREEN_HEIGHT - 30))
            
            # Draw navigation hints
            if self.menu_page > 0:
                left_hint = self.font_tiny.render("← Previous", True, HIGHLIGHT_COLOR)
                self.screen.blit(left_hint, (10, SCREEN_HEIGHT - 30))
            
            if self.menu_page < self.total_pages - 1:
                right_hint = self.font_tiny.render("Next →", True, HIGHLIGHT_COLOR)
                right_x = SCREEN_WIDTH - right_hint.get_width() - 10
                self.screen.blit(right_hint, (right_x, SCREEN_HEIGHT - 30))
        
        # Draw control hints
        hints = [
            "↑↓ Navigate",
            "←→ Change Page",
            "Enter Select"
        ]
        
        hint_y = SCREEN_HEIGHT - 15
        for i, hint in enumerate(hints):
            hint_surface = self.font_tiny.render(hint, True, HIGHLIGHT_COLOR)
            hint_x = 10 + i * 120
            self.screen.blit(hint_surface, (hint_x, hint_y))
    
    def run(self):
        """Main game loop"""
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)
        except KeyboardInterrupt:
            print("\nShutting down LightBerry OS...")
        finally:
            self.save_data()
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    os = LightBerryOS()
    os.run()
