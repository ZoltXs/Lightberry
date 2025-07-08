"""
Enhanced Timer Module for LightBerry OS
Professional timer with stopwatch, countdown, and lap tracking
"""

import pygame
import time
from datetime import datetime, timedelta
from config.constants import *

class Timer:
    def __init__(self, os_instance):
        self.os = os_instance
        self.init_timer()
    
    def init_timer(self):
        """Initialize timer state"""
        self.mode = "stopwatch"
        self.selected_button = 0
        self.input_mode = "minutes"
        
        # Stopwatch
        self.stopwatch_start_time = 0
        self.stopwatch_running = False
        self.stopwatch_elapsed = 0
        self.stopwatch_laps = []
        self.max_laps = 20
        self.laps_per_column = 4
        self.max_columns = 5
        
        # Countdown
        self.countdown_hours = 0
        self.countdown_minutes = 5
        self.countdown_seconds = 0
        self.countdown_start_time = 0
        self.countdown_running = False
        self.countdown_elapsed = 0
        self.countdown_finished = False
        
        # UI
        self.buttons = ["Start/Stop", "Reset", "Lap", "Mode"]
        self.countdown_fields = ["hours", "minutes", "seconds"]
        self.countdown_field_index = 0
        
        # Animation
        self.flash_timer = 0
        self.flash_visible = True
    
    def handle_events(self, event):
        """Handle timer events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            
            elif event.key == pygame.K_UP:
                if self.mode == "countdown" and not self.countdown_running:
                    self.handle_countdown_input(1)
                else:
                    self.selected_button = max(0, self.selected_button - 1)
            
            elif event.key == pygame.K_DOWN:
                if self.mode == "countdown" and not self.countdown_running:
                    self.handle_countdown_input(-1)
                else:
                    self.selected_button = min(len(self.buttons) - 1, self.selected_button + 1)
            
            elif event.key == pygame.K_LEFT:
                if self.mode == "countdown" and not self.countdown_running:
                    self.countdown_field_index = max(0, self.countdown_field_index - 1)
            
            elif event.key == pygame.K_RIGHT:
                if self.mode == "countdown" and not self.countdown_running:
                    self.countdown_field_index = min(len(self.countdown_fields) - 1, self.countdown_field_index + 1)
            
            elif event.key == pygame.K_RETURN:
                self.handle_button_press()
            
            elif event.key == pygame.K_SPACE:
                self.toggle_timer()
            
            elif event.key == pygame.K_l:
                if self.mode == "stopwatch" and self.stopwatch_running:
                    self.add_lap()
            
            elif event.key == pygame.K_r:
                self.reset_timer()
            
            elif event.key == pygame.K_q:
                self.mode = "countdown" if self.mode == "stopwatch" else "stopwatch"
                self.selected_button = 0
        
        return None
    
    def handle_countdown_input(self, direction):
        """Handle countdown time input"""
        field = self.countdown_fields[self.countdown_field_index]
        
        if field == "hours":
            self.countdown_hours = max(0, min(23, self.countdown_hours + direction))
        elif field == "minutes":
            self.countdown_minutes = max(0, min(59, self.countdown_minutes + direction))
        elif field == "seconds":
            self.countdown_seconds = max(0, min(59, self.countdown_seconds + direction))
    
    def handle_button_press(self):
        """Handle button press"""
        if self.selected_button == 0:  # Start/Stop
            self.toggle_timer()
        elif self.selected_button == 1:  # Reset
            self.reset_timer()
        elif self.selected_button == 2:  # Lap
            if self.mode == "stopwatch" and self.stopwatch_running:
                self.add_lap()
        elif self.selected_button == 3:  # Mode
            self.mode = "countdown" if self.mode == "stopwatch" else "stopwatch"
    
    def toggle_timer(self):
        """Toggle timer start/stop"""
        if self.mode == "stopwatch":
            if self.stopwatch_running:
                self.stopwatch_elapsed += time.time() - self.stopwatch_start_time
                self.stopwatch_running = False
            else:
                self.stopwatch_start_time = time.time()
                self.stopwatch_running = True
        
        elif self.mode == "countdown":
            if self.countdown_running:
                self.countdown_elapsed += time.time() - self.countdown_start_time
                self.countdown_running = False
            else:
                if not self.countdown_finished:
                    self.countdown_start_time = time.time()
                    self.countdown_running = True
                    self.countdown_finished = False
    
    def reset_timer(self):
        """Reset timer"""
        if self.mode == "stopwatch":
            self.stopwatch_running = False
            self.stopwatch_elapsed = 0
            self.stopwatch_laps = []
        
        elif self.mode == "countdown":
            self.countdown_running = False
            self.countdown_elapsed = 0
            self.countdown_finished = False
    
    def add_lap(self):
        """Add lap time"""
        if len(self.stopwatch_laps) < self.max_laps:
            current_time = self.get_current_stopwatch_time()
            lap_time = current_time - (self.stopwatch_laps[-1] if self.stopwatch_laps else 0)
            self.stopwatch_laps.append(current_time)
    
    def get_current_stopwatch_time(self):
        """Get current stopwatch time"""
        if self.stopwatch_running:
            return self.stopwatch_elapsed + (time.time() - self.stopwatch_start_time)
        return self.stopwatch_elapsed
    
    def get_current_countdown_time(self):
        """Get current countdown time"""
        total_seconds = self.countdown_hours * 3600 + self.countdown_minutes * 60 + self.countdown_seconds
        
        if self.countdown_running:
            elapsed = self.countdown_elapsed + (time.time() - self.countdown_start_time)
            remaining = max(0, total_seconds - elapsed)
            
            if remaining == 0 and not self.countdown_finished:
                self.countdown_finished = True
                self.countdown_running = False
                # Could add notification here
            
            return remaining
        
        return max(0, total_seconds - self.countdown_elapsed)
    
    def format_time(self, seconds):
        """Format time as HH:MM:SS.ss"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"
        else:
            return f"{minutes:02d}:{secs:05.2f}"
    
    def format_lap_time(self, seconds):
        """Format lap time"""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes:02d}:{secs:05.2f}"
    
    def update(self):
        """Update timer state"""
        # Flash animation for countdown finish
        if self.countdown_finished:
            self.flash_timer += 1
            if self.flash_timer >= 15:
                self.flash_visible = not self.flash_visible
                self.flash_timer = 0
    
    def draw(self, screen):
        """Draw timer interface"""
        if self.mode == "stopwatch":
            self.draw_stopwatch(screen)
        else:
            self.draw_countdown(screen)
    
    def draw_stopwatch(self, screen):
        """Draw stopwatch interface"""
        # Header
        header_text = "Stopwatch"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Time display
        current_time = self.get_current_stopwatch_time()
        time_text = self.format_time(current_time)
        time_surface = self.os.font_xl.render(time_text, True, TEXT_COLOR)
        time_x = SCREEN_WIDTH // 2 - time_surface.get_width() // 2
        screen.blit(time_surface, (time_x, 30))
        
        # Status
        status_text = "Running" if self.stopwatch_running else "Stopped"
        status_color = SUCCESS_COLOR if self.stopwatch_running else WARNING_COLOR
        status_surface = self.os.font_m.render(status_text, True, status_color)
        status_x = SCREEN_WIDTH // 2 - status_surface.get_width() // 2
        screen.blit(status_surface, (status_x, 70))
        
        # Buttons
        button_y = 90
        button_width = (SCREEN_WIDTH - 40) // 4
        
        for i, button_text in enumerate(self.buttons):
            button_x = 10 + i * (button_width + 5)
            button_rect = pygame.Rect(button_x, button_y, button_width, 25)
            
            # Button color
            if i == self.selected_button:
                button_color = BUTTON_HOVER_COLOR
            else:
                button_color = BUTTON_COLOR
            
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, BUTTON_BORDER_COLOR, button_rect, 2)
            
            # Button text
            text_surface = self.os.font_s.render(button_text, True, TEXT_COLOR)
            text_x = button_rect.centerx - text_surface.get_width() // 2
            text_y = button_rect.centery - text_surface.get_height() // 2
            screen.blit(text_surface, (text_x, text_y))
        
        # Lap times
        if self.stopwatch_laps:
            lap_header = f"Laps ({len(self.stopwatch_laps)}/{self.max_laps})"
            lap_header_surface = self.os.font_m.render(lap_header, True, ACCENT_COLOR)
            screen.blit(lap_header_surface, (10, 125))
            
            # Display laps in columns
            lap_start_y = 145
            lap_height = 18
            
            for i, lap_time in enumerate(self.stopwatch_laps):
                col = i // self.laps_per_column
                row = i % self.laps_per_column
                
                if col >= self.max_columns:
                    break
                
                lap_x = 10 + col * 75
                lap_y = lap_start_y + row * lap_height
                
                # Lap number
                lap_num_text = f"{i+1:2d}:"
                lap_num_surface = self.os.font_s.render(lap_num_text, True, HIGHLIGHT_COLOR)
                screen.blit(lap_num_surface, (lap_x, lap_y))
                
                # Lap time
                if i == 0:
                    lap_display_time = lap_time
                else:
                    lap_display_time = lap_time - self.stopwatch_laps[i-1]
                
                lap_time_text = self.format_lap_time(lap_display_time)
                lap_time_surface = self.os.font_s.render(lap_time_text, True, TEXT_COLOR)
                screen.blit(lap_time_surface, (lap_x + 25, lap_y))
        
        # Controls
        controls = [
            "Space: Start/Stop",
            "L: Lap",
            "R: Reset",
            "Q: Countdown mode"
        ]
        
        control_y = SCREEN_HEIGHT - 35
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 2) * 180
            control_y_pos = control_y + (i // 2) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def draw_countdown(self, screen):
        """Draw countdown interface"""
        # Header
        header_text = "Countdown Timer"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Time display
        current_time = self.get_current_countdown_time()
        time_text = self.format_time(current_time)
        
        # Flash effect when finished
        time_color = TEXT_COLOR
        if self.countdown_finished and self.flash_visible:
            time_color = ERROR_COLOR
        
        time_surface = self.os.font_xl.render(time_text, True, time_color)
        time_x = SCREEN_WIDTH // 2 - time_surface.get_width() // 2
        screen.blit(time_surface, (time_x, 30))
        
        # Status
        if self.countdown_finished:
            status_text = "FINISHED!"
            status_color = ERROR_COLOR
        elif self.countdown_running:
            status_text = "Running"
            status_color = SUCCESS_COLOR
        else:
            status_text = "Stopped"
            status_color = WARNING_COLOR
        
        status_surface = self.os.font_m.render(status_text, True, status_color)
        status_x = SCREEN_WIDTH // 2 - status_surface.get_width() // 2
        screen.blit(status_surface, (status_x, 70))
        
        # Time input (when not running)
        if not self.countdown_running and not self.countdown_finished:
            input_label = "Set Time:"
            input_surface = self.os.font_m.render(input_label, True, TEXT_COLOR)
            screen.blit(input_surface, (10, 95))
            
            # Input fields
            field_y = 115
            field_width = (SCREEN_WIDTH - 60) // 3
            
            for i, (field, value) in enumerate([
                ("H", self.countdown_hours),
                ("M", self.countdown_minutes),
                ("S", self.countdown_seconds)
            ]):
                field_x = 10 + i * (field_width + 10)
                field_rect = pygame.Rect(field_x, field_y, field_width, 25)
                
                # Field color
                if i == self.countdown_field_index:
                    field_color = SELECTED_COLOR
                else:
                    field_color = BUTTON_COLOR
                
                pygame.draw.rect(screen, field_color, field_rect)
                pygame.draw.rect(screen, BUTTON_BORDER_COLOR, field_rect, 2)
                
                # Field label
                label_surface = self.os.font_s.render(field, True, HIGHLIGHT_COLOR)
                label_x = field_rect.centerx - label_surface.get_width() // 2
                screen.blit(label_surface, (label_x, field_y - 15))
                
                # Field value
                value_surface = self.os.font_m.render(f"{value:02d}", True, TEXT_COLOR)
                value_x = field_rect.centerx - value_surface.get_width() // 2
                value_y = field_rect.centery - value_surface.get_height() // 2
                screen.blit(value_surface, (value_x, value_y))
        
        # Buttons
        button_y = 150
        button_width = (SCREEN_WIDTH - 40) // 4
        
        for i, button_text in enumerate(self.buttons):
            if button_text == "Lap":
                continue  # Skip lap button in countdown mode
            
            button_x = 10 + i * (button_width + 5)
            button_rect = pygame.Rect(button_x, button_y, button_width, 25)
            
            # Button color
            if i == self.selected_button:
                button_color = BUTTON_HOVER_COLOR
            else:
                button_color = BUTTON_COLOR
            
            pygame.draw.rect(screen, button_color, button_rect)
            pygame.draw.rect(screen, BUTTON_BORDER_COLOR, button_rect, 2)
            
            # Button text
            text_surface = self.os.font_s.render(button_text, True, TEXT_COLOR)
            text_x = button_rect.centerx - text_surface.get_width() // 2
            text_y = button_rect.centery - text_surface.get_height() // 2
            screen.blit(text_surface, (text_x, text_y))
        
        # Controls
        controls = [
            "↑↓: Adjust time",
            "←→: Change field",
            "Space: Start/Stop",
            "R: Reset",
            "Q: Stopwatch mode"
        ]
        
        control_y = SCREEN_HEIGHT - 45
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 2) * 180
            control_y_pos = control_y + (i // 2) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def save_data(self):
        """Save timer data"""
        return {
            "mode": self.mode,
            "countdown_hours": self.countdown_hours,
            "countdown_minutes": self.countdown_minutes,
            "countdown_seconds": self.countdown_seconds
        }
    
    def load_data(self, data):
        """Load timer data"""
        self.mode = data.get("mode", "stopwatch")
        self.countdown_hours = data.get("countdown_hours", 0)
        self.countdown_minutes = data.get("countdown_minutes", 5)
        self.countdown_seconds = data.get("countdown_seconds", 0)
