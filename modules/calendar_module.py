"""
Calendar Module for LightBerry OS
"""

import pygame
import calendar
from datetime import datetime, date, timedelta
from config.constants import *

class CalendarModule:
    def __init__(self, os_instance):
        self.os = os_instance
        self.init_calendar()

    def init_calendar(self):
        """Initialize calendar state"""
        self.current_date = date.today()
        self.view_date = date.today().replace(day=1)
        self.selected_day = self.current_date
        self.events = {}
        self.mode = "month_view"

        # Navigation
        self.selected_row = 0
        self.selected_col = 0

        # Event management
        self.adding_event = False
        self.editing_event = False
        self.event_index = 0
        self.input_mode = "title"
        self.event_title = ""
        self.event_time = "12:00 AM"
        self.event_description = ""

        # Time wheel for event time input
        self.time_wheel_hour = 12
        self.time_wheel_minute = 0
        self.time_wheel_mode = "hour"
        self.time_wheel_am_pm = "AM"

        # Text cursor blinking
        self.text_cursor_visible = True
        self.last_cursor_blink = pygame.time.get_ticks()
        
        # Generate calendar grid
        self.generate_calendar_grid()

    def generate_calendar_grid(self):
        """Generate calendar grid for current month"""
        self.calendar_grid = calendar.monthcalendar(self.view_date.year, self.view_date.month)

    def handle_events(self, event):
        """Handle calendar events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.adding_event or self.editing_event:
                    self.adding_event = False
                    self.editing_event = False
                    return None
                else:
                    return "back"
            
            if self.adding_event or self.editing_event:
                self.handle_event_input(event)
            else:
                self.handle_navigation(event)
        
        return None

    def handle_navigation(self, event):
        """Handle navigation in calendar view"""
        if event.key == pygame.K_UP:
            self.selected_row = max(0, self.selected_row - 1)
        elif event.key == pygame.K_DOWN:
            self.selected_row = min(len(self.calendar_grid) - 1, self.selected_row + 1)
        elif event.key == pygame.K_LEFT:
            if event.mod & pygame.KMOD_CTRL:
                # Previous year
                self.view_date = self.view_date.replace(year=self.view_date.year - 1)
                self.generate_calendar_grid()
                self.selected_row = 0
                self.selected_col = 0
            elif event.mod & pygame.KMOD_SHIFT:
                # Previous month
                self.previous_month()
            else:
                self.selected_col = max(0, self.selected_col - 1)
        elif event.key == pygame.K_RIGHT:
            if event.mod & pygame.KMOD_CTRL:
                # Next year
                self.view_date = self.view_date.replace(year=self.view_date.year + 1)
                self.generate_calendar_grid()
                self.selected_row = 0
                self.selected_col = 0
            elif event.mod & pygame.KMOD_SHIFT:
                # Next month
                self.next_month()
            else:
                self.selected_col = min(6, self.selected_col + 1)
        elif event.key == pygame.K_RETURN:
            # Update selected_day based on current position
            if (0 <= self.selected_row < len(self.calendar_grid) and
                0 <= self.selected_col < len(self.calendar_grid[self.selected_row])):
                day_num = self.calendar_grid[self.selected_row][self.selected_col]
                if day_num > 0:
                    self.selected_day = self.view_date.replace(day=day_num)
                    self.start_add_event()

    def handle_event_input(self, event):
        """Handle input for adding/editing events"""
        if event.key == pygame.K_RETURN:
            if self.input_mode == "title":
                self.input_mode = "time"
            elif self.input_mode == "time":
                self.save_event()
        
        elif event.key == pygame.K_TAB:
            if self.input_mode == "title":
                self.input_mode = "time"
            elif self.input_mode == "time":
                self.input_mode = "title"
        
        elif event.key == pygame.K_UP:
            if self.input_mode == "time":
                self.handle_time_wheel_up()
        
        elif event.key == pygame.K_DOWN:
            if self.input_mode == "time":
                self.handle_time_wheel_down()
        
        elif event.key == pygame.K_LEFT:
            if self.input_mode == "time":
                self.time_wheel_mode = "hour"
        
        elif event.key == pygame.K_RIGHT:
            if self.input_mode == "time":
                self.time_wheel_mode = "minute"
        
        elif event.key == pygame.K_SPACE:
            if self.input_mode == "time":
                self.time_wheel_am_pm = "PM" if self.time_wheel_am_pm == "AM" else "AM"
                self.update_event_time()
        
        elif event.key == pygame.K_BACKSPACE:
            if self.input_mode == "title":
                self.event_title = self.event_title[:-1]
        
        else:
            char = event.unicode
            if char.isprintable():
                if self.input_mode == "title" and len(self.event_title) < 30:
                    self.event_title += char

    def handle_time_wheel_up(self):
        """Handle time wheel up navigation"""
        if self.time_wheel_mode == "hour":
            self.time_wheel_hour = self.time_wheel_hour + 1
            if self.time_wheel_hour > 12:
                self.time_wheel_hour = 1
        else:  # minute
            self.time_wheel_minute = (self.time_wheel_minute + 5) % 60
        self.update_event_time()

    def handle_time_wheel_down(self):
        """Handle time wheel down navigation"""
        if self.time_wheel_mode == "hour":
            self.time_wheel_hour = self.time_wheel_hour - 1
            if self.time_wheel_hour < 1:
                self.time_wheel_hour = 12
        else:  # minute
            self.time_wheel_minute = (self.time_wheel_minute - 5) % 60
        self.update_event_time()

    def update_event_time(self):
        """Update event time string from wheel values"""
        self.event_time = f"{self.time_wheel_hour:02d}:{self.time_wheel_minute:02d} {self.time_wheel_am_pm}"

    def start_add_event(self):
        """Start adding a new event"""
        self.adding_event = True
        self.input_mode = "title"
        self.event_title = ""
        self.event_time = "12:00 AM"
        self.event_description = ""
        self.time_wheel_hour = 12
        self.time_wheel_minute = 0
        self.time_wheel_am_pm = "AM"

    def save_event(self):
        """Save the current event"""
        if not self.event_title:
            return
        
        event = {
            "title": self.event_title,
            "time": self.event_time,
            "description": self.event_description
        }
        
        day_key = self.selected_day.strftime("%Y-%m-%d")
        
        if day_key not in self.events:
            self.events[day_key] = []
        
        self.events[day_key].append(event)
        
        # Check if event time matches current time and send notification
        now = datetime.now()
        am_pm = "AM" if now.hour < 12 else "PM"
        hour = now.hour % 12 or 12
        minute = now.minute
        current_time_str = f"{hour:02d}:{minute:02d} {am_pm}"
        
        # If event is for today and time matches current time, create notification
        today_key = date.today().strftime("%Y-%m-%d")
        if (day_key == today_key and 
            self.event_time == current_time_str and 
            hasattr(self.os, 'notification_manager')):
            self.os.notification_manager.add_event_notification(self.event_title, self.event_time)
        
        self.adding_event = False
        self.editing_event = False

    def next_month(self):
        """Navigate to next month"""
        if self.view_date.month == 12:
            self.view_date = self.view_date.replace(year=self.view_date.year + 1, month=1)
        else:
            self.view_date = self.view_date.replace(month=self.view_date.month + 1)
        self.generate_calendar_grid()
        self.selected_row = 0
        self.selected_col = 0

    def previous_month(self):
        """Navigate to previous month"""
        if self.view_date.month == 1:
            self.view_date = self.view_date.replace(year=self.view_date.year - 1, month=12)
        else:
            self.view_date = self.view_date.replace(month=self.view_date.month - 1)
        self.generate_calendar_grid()
        self.selected_row = 0
        self.selected_col = 0

        def draw(self, screen):
            """Draw the calendar interface"""
            # Clear screen
            screen.fill(BACKGROUND_COLOR)
        
        # Header
        header_text = f"Calendar - {self.view_date.strftime('%B %Y')}"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        if self.adding_event or self.editing_event:
            self.draw_event_input(screen)
        else:
            self.draw_calendar_grid(screen)

    def draw_calendar_grid(self, screen):
        """Draw the calendar grid"""
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            day_surface = self.os.font_s.render(day, True, HIGHLIGHT_COLOR)
            day_x = 10 + i * 55
            screen.blit(day_surface, (day_x, 30))
        
        # Calendar grid
        for row_idx, week in enumerate(self.calendar_grid):
            for col_idx, day in enumerate(week):
                if day == 0:
                    continue
                
                x = 10 + col_idx * 55
                y = 50 + row_idx * 30
                
                # Day background
                day_rect = pygame.Rect(x, y, 50, 25)
                
                # Check if this day has events
                day_date = self.view_date.replace(day=day)
                day_key = day_date.strftime("%Y-%m-%d")
                has_events = day_key in self.events and len(self.events[day_key]) > 0
                
                # Check if this is today
                is_today = day_date == self.current_date
                
                # Color coding
                if row_idx == self.selected_row and col_idx == self.selected_col:
                    pygame.draw.rect(screen, SELECTED_COLOR, day_rect)
                elif is_today:
                    pygame.draw.rect(screen, CALENDAR_TODAY_COLOR, day_rect)
                elif has_events:
                    pygame.draw.rect(screen, CALENDAR_EVENT_COLOR, day_rect)
                
                pygame.draw.rect(screen, BUTTON_BORDER_COLOR, day_rect, 1)
                
                # Day number
                day_text = str(day)
                text_color = TEXT_COLOR
                if is_today:
                    text_color = (0, 0, 0)  # Black text on today's color
                elif has_events:
                    text_color = (0, 0, 0)  # Black text on event color
                    
                day_surface = self.os.font_s.render(day_text, True, text_color)
                day_text_x = x + 5
                day_text_y = y + 5
                screen.blit(day_surface, (day_text_x, day_text_y))
        
        # Instructions
        instructions = [
            "Arrows: Navigate  Shift+←→: Month  Ctrl+←→: Year",
            "Enter: Add event  ESC: Back"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.os.font_tiny.render(instruction, True, HIGHLIGHT_COLOR)
            screen.blit(inst_surface, (10, SCREEN_HEIGHT - 40 + i * 12))

    def draw_event_input(self, screen):
        """Draw event input interface"""
        # Start without title
        y_offset = 20
        
        # Event title field
        title_label = "Title:"
        title_label_surface = self.os.font_s.render(title_label, True, TEXT_COLOR)
        screen.blit(title_label_surface, (10, y_offset))
        
        title_rect = pygame.Rect(10, y_offset + 20, SCREEN_WIDTH - 20, 25)
        title_color = SELECTED_COLOR if self.input_mode == "title" else BUTTON_COLOR
        pygame.draw.rect(screen, title_color, title_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, title_rect, 2)
        
        title_text = self.event_title
        title_text_surface = self.os.font_s.render(title_text, True, TEXT_COLOR)
        screen.blit(title_text_surface, (15, y_offset + 25))
        
        # Time field with wheel
        y_offset += 60
        time_label = "Time:"
        time_label_surface = self.os.font_s.render(time_label, True, TEXT_COLOR)
        screen.blit(time_label_surface, (10, y_offset))
        
        if self.input_mode == "time":
            # Time wheel display
            time_rect = pygame.Rect(10, y_offset + 20, SCREEN_WIDTH - 20, 40)
            pygame.draw.rect(screen, SELECTED_COLOR, time_rect)
            pygame.draw.rect(screen, BUTTON_BORDER_COLOR, time_rect, 2)
            
            # Hour
            hour_text = f"{self.time_wheel_hour:02d}"
            hour_color = ACCENT_COLOR if self.time_wheel_mode == "hour" else TEXT_COLOR
            hour_surface = self.os.font_m.render(hour_text, True, hour_color)
            screen.blit(hour_surface, (20, y_offset + 30))
            
            # Colon
            colon_surface = self.os.font_m.render(":", True, TEXT_COLOR)
            screen.blit(colon_surface, (50, y_offset + 30))
            
            # Minute
            minute_text = f"{self.time_wheel_minute:02d}"
            minute_color = ACCENT_COLOR if self.time_wheel_mode == "minute" else TEXT_COLOR
            minute_surface = self.os.font_m.render(minute_text, True, minute_color)
            screen.blit(minute_surface, (65, y_offset + 30))
            
            # AM/PM
            ampm_surface = self.os.font_s.render(self.time_wheel_am_pm, True, TEXT_COLOR)
            screen.blit(ampm_surface, (110, y_offset + 30))
            
            # Instructions
            inst_text = "↑↓: Change  ←→: Hour/Min  Space: AM/PM"
            inst_surface = self.os.font_tiny.render(inst_text, True, HIGHLIGHT_COLOR)
            screen.blit(inst_surface, (20, y_offset + 50))
        else:
            # Just display the time
            time_rect = pygame.Rect(10, y_offset + 20, SCREEN_WIDTH - 20, 25)
            pygame.draw.rect(screen, BUTTON_COLOR, time_rect)
            pygame.draw.rect(screen, BUTTON_BORDER_COLOR, time_rect, 2)
            
            time_text = self.event_time
            time_text_surface = self.os.font_s.render(time_text, True, TEXT_COLOR)
            screen.blit(time_text_surface, (15, y_offset + 25))
        
        # Instructions
        instructions = [
            "Enter: Save event  Tab: Switch field",
            "ESC: Cancel"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.os.font_tiny.render(instruction, True, HIGHLIGHT_COLOR)
            screen.blit(inst_surface, (10, SCREEN_HEIGHT - 40 + i * 12))

    def update(self):
        """Update calendar state"""
        # Update cursor blink for text input
        current_time = pygame.time.get_ticks()
        if current_time - self.last_cursor_blink > 500:
            self.text_cursor_visible = not self.text_cursor_visible
            self.last_cursor_blink = current_time

    def save_data(self):
        """Save calendar data"""
        return {
            "events": self.events,
            "view_date": self.view_date.isoformat()
        }

    def load_data(self, data):
        """Load calendar data"""
        self.events = data.get("events", {})
        if "view_date" in data:
            self.view_date = datetime.fromisoformat(data["view_date"]).date()
        self.generate_calendar_grid()
