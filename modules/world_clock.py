"""
Enhanced World Clock Module for LightBerry OS
Professional world clock with capital cities and timezone management
"""

import pygame
import math
from datetime import datetime, timedelta
from config.constants import *
from config.world_cities import WORLD_CAPITALS

class WorldClock:
    def __init__(self, os_instance):
        self.os = os_instance
        self.init_world_clock()
    
    def init_world_clock(self):
        """Initialize world clock state"""
        self.world_clocks = [
            {"name": "Madrid", "timezone": 1, "color": TIME_ZONE_COLORS[0]},
            {"name": "New York", "timezone": -5, "color": TIME_ZONE_COLORS[1]},
            {"name": "Tokyo", "timezone": 9, "color": TIME_ZONE_COLORS[2]},
        ]
        
        self.mode = "view"
        self.selected_clock = 0
        self.input_text = ""
        self.search_results = []
        self.search_selected = 0
        self.max_clocks = 3
        
        # Animation
        self.animation_offset = 0
        self.animation_time = 0
        
        # Text input
        self.text_cursor_visible = True
        self.text_cursor_timer = 0
    
    def handle_events(self, event):
        """Handle world clock events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.mode == "add":
                    self.mode = "view"
                    self.input_text = ""
                    self.search_results = []
                else:
                    return "back"
            
            elif self.mode == "view":
                self.handle_view_events(event)
            
            elif self.mode == "add":
                self.handle_add_events(event)
        
        return None
    
    def handle_view_events(self, event):
        """Handle view mode events"""
        if event.key == pygame.K_UP:
            self.selected_clock = max(0, self.selected_clock - 1)
        
        elif event.key == pygame.K_DOWN:
            self.selected_clock = min(len(self.world_clocks) - 1, self.selected_clock + 1)
        
        elif event.key == pygame.K_a:
            if len(self.world_clocks) < self.max_clocks:
                self.mode = "add"
                self.input_text = ""
                self.search_results = []
                self.search_selected = 0
        
        elif event.key == pygame.K_d:
            if self.world_clocks and len(self.world_clocks) > 1:
                del self.world_clocks[self.selected_clock]
                self.selected_clock = min(self.selected_clock, len(self.world_clocks) - 1)
        
        elif event.key == pygame.K_r:
            self.world_clocks = [
                {"name": "Madrid", "timezone": 1, "color": TIME_ZONE_COLORS[0]},
                {"name": "New York", "timezone": -5, "color": TIME_ZONE_COLORS[1]},
                {"name": "Tokyo", "timezone": 9, "color": TIME_ZONE_COLORS[2]},
            ]
            self.selected_clock = 0
    
    def handle_add_events(self, event):
        """Handle add mode events"""
        if event.key == pygame.K_UP:
            self.search_selected = max(0, self.search_selected - 1)
        
        elif event.key == pygame.K_DOWN:
            self.search_selected = min(len(self.search_results) - 1, self.search_selected + 1)
        
        elif event.key == pygame.K_RETURN:
            if self.search_results and self.search_selected < len(self.search_results):
                self.add_clock(self.search_results[self.search_selected])
                self.mode = "view"
                self.input_text = ""
                self.search_results = []
        
        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
            self.update_search()
        
        else:
            char = event.unicode
            if char.isprintable() and len(self.input_text) < 20:
                self.input_text += char
                self.update_search()
    
    def update_search(self):
        """Update search results"""
        if not self.input_text:
            self.search_results = []
            return
        
        search_term = self.input_text.lower()
        self.search_results = []
        
        for city, info in WORLD_CAPITALS.items():
            if search_term in city.lower():
                # Check if already added
                already_added = any(clock["name"] == city for clock in self.world_clocks)
                if not already_added:
                    self.search_results.append(city)
        
        self.search_results = sorted(self.search_results)[:10]  # Limit to 10 results
        self.search_selected = 0
    
    def add_clock(self, city_name):
        """Add a new clock"""
        if len(self.world_clocks) >= self.max_clocks:
            return
        
        if city_name in WORLD_CAPITALS:
            city_info = WORLD_CAPITALS[city_name]
            color_index = len(self.world_clocks) % len(TIME_ZONE_COLORS)
            
            new_clock = {
                "name": city_name,
                "timezone": city_info["timezone"],
                "color": TIME_ZONE_COLORS[color_index]
            }
            
            self.world_clocks.append(new_clock)
    
    def get_time_for_timezone(self, timezone_offset):
        """Get current time for timezone"""
        utc_time = datetime.utcnow()
        local_time = utc_time + timedelta(hours=timezone_offset)
        return local_time
    
    def draw_analog_clock(self, screen, x, y, radius, time_obj, color):
        """Draw analog clock"""
        # Clock face
        pygame.draw.circle(screen, CLOCK_FACE_COLOR, (x, y), radius)
        pygame.draw.circle(screen, color, (x, y), radius, 3)
        
        # Hour markers
        for i in range(12):
            angle = i * 30 - 90  # -90 to start at 12 o'clock
            angle_rad = math.radians(angle)
            
            # Outer point
            outer_x = x + (radius - 10) * math.cos(angle_rad)
            outer_y = y + (radius - 10) * math.sin(angle_rad)
            
            # Inner point
            inner_x = x + (radius - 20) * math.cos(angle_rad)
            inner_y = y + (radius - 20) * math.sin(angle_rad)
            
            pygame.draw.line(screen, CLOCK_BORDER_COLOR, 
                           (outer_x, outer_y), (inner_x, inner_y), 2)
        
        # Hour hand
        hour_angle = (time_obj.hour % 12) * 30 + time_obj.minute * 0.5 - 90
        hour_angle_rad = math.radians(hour_angle)
        hour_x = x + (radius - 35) * math.cos(hour_angle_rad)
        hour_y = y + (radius - 35) * math.sin(hour_angle_rad)
        pygame.draw.line(screen, CLOCK_HOUR_HAND_COLOR, (x, y), (hour_x, hour_y), 4)
        
        # Minute hand
        minute_angle = time_obj.minute * 6 - 90
        minute_angle_rad = math.radians(minute_angle)
        minute_x = x + (radius - 25) * math.cos(minute_angle_rad)
        minute_y = y + (radius - 25) * math.sin(minute_angle_rad)
        pygame.draw.line(screen, CLOCK_MINUTE_HAND_COLOR, (x, y), (minute_x, minute_y), 3)
        
        # Second hand
        second_angle = time_obj.second * 6 - 90
        second_angle_rad = math.radians(second_angle)
        second_x = x + (radius - 15) * math.cos(second_angle_rad)
        second_y = y + (radius - 15) * math.sin(second_angle_rad)
        pygame.draw.line(screen, CLOCK_SECOND_HAND_COLOR, (x, y), (second_x, second_y), 1)
        
        # Center dot
        pygame.draw.circle(screen, TEXT_COLOR, (x, y), 3)
    
    def update(self):
        """Update world clock state"""
        self.animation_time += 1
        self.animation_offset = math.sin(self.animation_time * 0.05) * 2
        
        # Update text cursor
        self.text_cursor_timer += 1
        if self.text_cursor_timer >= 30:
            self.text_cursor_visible = not self.text_cursor_visible
            self.text_cursor_timer = 0
    
    def draw(self, screen):
        """Draw world clock interface"""
        if self.mode == "add":
            self.draw_add_mode(screen)
        else:
            self.draw_view_mode(screen)
    
    def draw_view_mode(self, screen):
        """Draw view mode"""
        # Header
        header_text = "World Clock"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Clock display
        if len(self.world_clocks) == 1:
            # Single large clock
            clock = self.world_clocks[0]
            time_obj = self.get_time_for_timezone(clock["timezone"])
            
            # Analog clock
            clock_x = SCREEN_WIDTH // 2
            clock_y = 80
            clock_radius = 35
            
            self.draw_analog_clock(screen, clock_x, clock_y, clock_radius, time_obj, clock["color"])
            
            # City name
            city_surface = self.os.font_l.render(clock["name"], True, clock["color"])
            city_x = SCREEN_WIDTH // 2 - city_surface.get_width() // 2
            screen.blit(city_surface, (city_x, 125))
            
            # Digital time
            time_str = time_obj.strftime("%H:%M:%S")
            time_surface = self.os.font_l.render(time_str, True, TEXT_COLOR)
            time_x = SCREEN_WIDTH // 2 - time_surface.get_width() // 2
            screen.blit(time_surface, (time_x, 145))
            
            # Date
            date_str = time_obj.strftime("%A, %B %d")
            date_surface = self.os.font_m.render(date_str, True, HIGHLIGHT_COLOR)
            date_x = SCREEN_WIDTH // 2 - date_surface.get_width() // 2
            screen.blit(date_surface, (date_x, 165))
        
        else:
            # Multiple clocks in grid
            clock_width = SCREEN_WIDTH // min(len(self.world_clocks), 3)
            
            for i, clock in enumerate(self.world_clocks):
                time_obj = self.get_time_for_timezone(clock["timezone"])
                
                # Position
                x = 10 + i * (clock_width - 10)
                y = 40
                
                # Selection indicator
                if i == self.selected_clock:
                    selection_rect = pygame.Rect(x - 5, y - 5, clock_width - 10, 120)
                    pygame.draw.rect(screen, SELECTED_COLOR, selection_rect)
                    pygame.draw.rect(screen, clock["color"], selection_rect, 2)
                
                # Small analog clock
                clock_x = x + (clock_width - 20) // 2
                clock_y = y + 25
                clock_radius = 20
                
                self.draw_analog_clock(screen, clock_x, clock_y, clock_radius, time_obj, clock["color"])
                
                # City name
                city_text = clock["name"]
                if len(city_text) > 8:
                    city_text = city_text[:8] + "..."
                
                city_surface = self.os.font_m.render(city_text, True, clock["color"])
                city_x = x + (clock_width - 20 - city_surface.get_width()) // 2
                screen.blit(city_surface, (city_x, y + 50))
                
                # Digital time
                time_str = time_obj.strftime("%H:%M")
                time_surface = self.os.font_m.render(time_str, True, TEXT_COLOR)
                time_x = x + (clock_width - 20 - time_surface.get_width()) // 2
                screen.blit(time_surface, (time_x, y + 70))
                
                # Date (abbreviated)
                date_str = time_obj.strftime("%m/%d")
                date_surface = self.os.font_s.render(date_str, True, HIGHLIGHT_COLOR)
                date_x = x + (clock_width - 20 - date_surface.get_width()) // 2
                screen.blit(date_surface, (date_x, y + 90))
        
        # Controls
        controls = [
            "↑↓: Navigate",
            "A: Add city",
            "D: Delete city",
            "R: Reset"
        ]
        
        if len(self.world_clocks) < self.max_clocks:
            status_text = f"Cities: {len(self.world_clocks)}/{self.max_clocks}"
        else:
            status_text = "Maximum cities reached"
        
        status_surface = self.os.font_s.render(status_text, True, WARNING_COLOR)
        status_x = SCREEN_WIDTH // 2 - status_surface.get_width() // 2
        screen.blit(status_surface, (status_x, 180))
        
        control_y = SCREEN_HEIGHT - 40
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 2) * 180
            control_y_pos = control_y + (i // 2) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def draw_add_mode(self, screen):
        """Draw add mode"""
        # Header
        header_text = "Add World Clock"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Search input
        search_label = "Search capital cities:"
        search_surface = self.os.font_m.render(search_label, True, TEXT_COLOR)
        screen.blit(search_surface, (10, 35))
        
        # Input field
        input_rect = pygame.Rect(10, 55, SCREEN_WIDTH - 20, 25)
        pygame.draw.rect(screen, BUTTON_COLOR, input_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, input_rect, 2)
        
        input_text = self.input_text
        if self.text_cursor_visible:
            input_text += "|"
        
        input_surface = self.os.font_m.render(input_text, True, TEXT_COLOR)
        screen.blit(input_surface, (15, 58))
        
        # Search results
        if self.search_results:
            results_label = "Select a city:"
            results_surface = self.os.font_m.render(results_label, True, TEXT_COLOR)
            screen.blit(results_surface, (10, 90))
            
            for i, city in enumerate(self.search_results[:6]):  # Show max 6 results
                result_y = 110 + i * 20
                
                # Selection background
                if i == self.search_selected:
                    result_rect = pygame.Rect(10, result_y - 2, SCREEN_WIDTH - 20, 18)
                    pygame.draw.rect(screen, SELECTED_COLOR, result_rect)
                
                # City name and country
                city_info = WORLD_CAPITALS.get(city, {})
                city_text = f"{city}, {city_info.get('country', 'Unknown')}"
                
                city_surface = self.os.font_m.render(city_text, True, TEXT_COLOR)
                screen.blit(city_surface, (15, result_y))
                
                # Timezone info
                timezone = city_info.get('timezone', 0)
                tz_text = f"UTC{timezone:+.1f}" if timezone != int(timezone) else f"UTC{int(timezone):+d}"
                tz_surface = self.os.font_s.render(tz_text, True, HIGHLIGHT_COLOR)
                tz_x = SCREEN_WIDTH - tz_surface.get_width() - 15
                screen.blit(tz_surface, (tz_x, result_y + 2))
        
        elif self.input_text:
            no_results_text = "No matching cities found"
            no_results_surface = self.os.font_m.render(no_results_text, True, ERROR_COLOR)
            no_results_x = SCREEN_WIDTH // 2 - no_results_surface.get_width() // 2
            screen.blit(no_results_surface, (no_results_x, 100))
        
        # Controls
        controls = [
            "Type: Search cities",
            "↑↓: Navigate results",
            "Enter: Add city",
            "ESC: Cancel"
        ]
        
        control_y = SCREEN_HEIGHT - 40
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 2) * 180
            control_y_pos = control_y + (i // 2) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def save_data(self):
        """Save world clock data"""
        return {
            "world_clocks": self.world_clocks
        }
    
    def load_data(self, data):
        """Load world clock data"""
        self.world_clocks = data.get("world_clocks", self.world_clocks)
        self.selected_clock = 0
