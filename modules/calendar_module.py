"""
Calendar Module for LightBerry OS with 24-Hour Time Wheel
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
        """Initialize calendar state with 24-hour time wheel"""
        self.current_date = date.today()
        self.view_date = date.today().replace(day=1)
        self.selected_day = self.current_date
        self.events = {}
        self.mode = "month_view"

        # Enhanced Navigation
        self.selected_row = 0
        self.selected_col = 0
        self.scroll_offset = 0
        self.max_visible_rows = 5
        
        # Calendar navigation modes
        self.nav_mode = "day"  # "day", "month", "year"
        self.month_selected = self.view_date.month
        self.year_selected = self.view_date.year

        # Event management
        self.adding_event = False
        self.editing_event = False
        self.event_index = 0
        self.input_mode = "title"
        self.event_title = ""
        self.event_time = "12:00"
        self.event_description = ""

        # 24-Hour Time Wheel
        self.time_wheel_hour = 12
        self.time_wheel_minute = 0
        self.time_wheel_mode = "hour"

        # Text cursor blinking
        self.text_cursor_visible = True
        self.last_cursor_blink = pygame.time.get_ticks()
        
        # Enhanced color scheme
        self.selected_day_color = CALENDAR_SELECTED_COLOR
        self.today_color = CALENDAR_TODAY_COLOR
        self.event_color = CALENDAR_EVENT_COLOR
        self.hover_color = BUTTON_HOVER_COLOR
        self.weekend_color = (80, 80, 120)
        
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
            
            if event.key == pygame.K_TAB:
                # Switch navigation mode
                if self.nav_mode == "day":
                    self.nav_mode = "month"
                elif self.nav_mode == "month":
                    self.nav_mode = "year"
                else:
                    self.nav_mode = "day"
                return None
            
            if self.adding_event or self.editing_event:
                self.handle_event_input(event)
            else:
                self.handle_navigation(event)
        
        return None

    def handle_navigation(self, event):
        """Handle navigation in calendar view"""
        if self.nav_mode == "day":
            self.handle_day_navigation(event)
        elif self.nav_mode == "month":
            self.handle_month_navigation(event)
        elif self.nav_mode == "year":
            self.handle_year_navigation(event)

    def handle_day_navigation(self, event):
        """Handle day-level navigation"""
        if event.key == pygame.K_UP:
            if self.selected_row > 0:
                self.selected_row -= 1
            elif self.scroll_offset > 0:
                self.scroll_offset -= 1
                
        elif event.key == pygame.K_DOWN:
            if self.selected_row < min(len(self.calendar_grid) - 1, self.max_visible_rows - 1):
                self.selected_row += 1
            elif self.selected_row + self.scroll_offset < len(self.calendar_grid) - 1:
                self.scroll_offset += 1
                
        elif event.key == pygame.K_LEFT:
            if event.mod & pygame.KMOD_SHIFT:
                self.previous_month()
            else:
                self.selected_col = max(0, self.selected_col - 1)
                
        elif event.key == pygame.K_RIGHT:
            if event.mod & pygame.KMOD_SHIFT:
                self.next_month()
            else:
                self.selected_col = min(6, self.selected_col + 1)
                
        elif event.key == pygame.K_RETURN:
            # Update selected_day based on current position
            actual_row = self.selected_row + self.scroll_offset
            if (0 <= actual_row < len(self.calendar_grid) and
                0 <= self.selected_col < len(self.calendar_grid[actual_row])):
                day_num = self.calendar_grid[actual_row][self.selected_col]
                if day_num > 0:
                    self.selected_day = self.view_date.replace(day=day_num)
                    self.start_add_event()

    def handle_month_navigation(self, event):
        """Handle month selection navigation"""
        if event.key == pygame.K_UP:
            self.month_selected = max(1, self.month_selected - 1)
        elif event.key == pygame.K_DOWN:
            self.month_selected = min(12, self.month_selected + 1)
        elif event.key == pygame.K_RETURN:
            self.view_date = self.view_date.replace(month=self.month_selected)
            self.generate_calendar_grid()
            self.nav_mode = "day"
            self.selected_row = 0
            self.selected_col = 0

    def handle_year_navigation(self, event):
        """Handle year selection navigation"""
        if event.key == pygame.K_UP:
            self.year_selected = max(2000, self.year_selected - 1)
        elif event.key == pygame.K_DOWN:
            self.year_selected = min(2100, self.year_selected + 1)
        elif event.key == pygame.K_RETURN:
            self.view_date = self.view_date.replace(year=self.year_selected)
            self.generate_calendar_grid()
            self.nav_mode = "day"
            self.selected_row = 0
            self.selected_col = 0

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
        
        elif event.key == pygame.K_BACKSPACE:
            if self.input_mode == "title":
                self.event_title = self.event_title[:-1]
        
        else:
            char = event.unicode
            if char.isprintable():
                if self.input_mode == "title" and len(self.event_title) < 30:
                    self.event_title += char

    def handle_time_wheel_up(self):
        """Handle time wheel up for 24-hour format"""
        if self.time_wheel_mode == "hour":
            self.time_wheel_hour = (self.time_wheel_hour + 1) % 24
        else:  # minute
            self.time_wheel_minute = (self.time_wheel_minute + 5) % 60
        self.update_event_time()

    def handle_time_wheel_down(self):
        """Handle time wheel down for 24-hour format"""
        if self.time_wheel_mode == "hour":
            self.time_wheel_hour = (self.time_wheel_hour - 1) % 24
        else:  # minute
            self.time_wheel_minute = (self.time_wheel_minute - 5) % 60
        self.update_event_time()

    def update_event_time(self):
        """Update event time string from 24-hour wheel values"""
        self.event_time = f"{self.time_wheel_hour:02d}:{self.time_wheel_minute:02d}"

    def start_add_event(self):
        """Start adding a new event"""
        self.adding_event = True
        self.input_mode = "title"
        self.event_title = ""
        self.event_time = "12:00"
        self.event_description = ""
        self.time_wheel_hour = 12
        self.time_wheel_minute = 0

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
        current_time_str = now.strftime("%H:%M")
        
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
        self.month_selected = self.view_date.month
        self.year_selected = self.view_date.year
        self.generate_calendar_grid()
        self.selected_row = 0
        self.selected_col = 0
        self.scroll_offset = 0

    def previous_month(self):
        """Navigate to previous month"""
        if self.view_date.month == 1:
            self.view_date = self.view_date.replace(year=self.view_date.year - 1, month=12)
        else:
            self.view_date = self.view_date.replace(month=self.view_date.month - 1)
        self.month_selected = self.view_date.month
        self.year_selected = self.view_date.year
        self.generate_calendar_grid()
        self.selected_row = 0
        self.selected_col = 0
        self.scroll_offset = 0

    def draw(self, screen):
        """Draw the calendar interface"""
        # Clear screen
        screen.fill(BACKGROUND_COLOR)
        
        if self.adding_event or self.editing_event:
            self.draw_event_input(screen)
        elif self.nav_mode == "month":
            self.draw_month_selector(screen)
        elif self.nav_mode == "year":
            self.draw_year_selector(screen)
        else:
            self.draw_calendar_grid(screen)

    def draw_calendar_grid(self, screen):
        """Draw the calendar grid with enhanced colors"""
        # Header with navigation mode indicator
        header_text = f"Calendar - {self.view_date.strftime('%B %Y')} [{self.nav_mode.upper()}]"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            day_color = WARNING_COLOR if i >= 5 else HIGHLIGHT_COLOR  # Weekend colors
            day_surface = self.os.font_s.render(day, True, day_color)
            day_x = 10 + i * 55
            screen.blit(day_surface, (day_x, 30))
        
        # Calendar grid with scrolling
        visible_rows = min(len(self.calendar_grid), self.max_visible_rows)
        for display_row in range(visible_rows):
            actual_row = display_row + self.scroll_offset
            if actual_row >= len(self.calendar_grid):
                break
                
            week = self.calendar_grid[actual_row]
            for col_idx, day in enumerate(week):
                if day == 0:
                    continue
                
                x = 10 + col_idx * 55
                y = 50 + display_row * 30
                
                # Day background
                day_rect = pygame.Rect(x, y, 50, 25)
                
                # Check if this day has events
                day_date = self.view_date.replace(day=day)
                day_key = day_date.strftime("%Y-%m-%d")
                has_events = day_key in self.events and len(self.events[day_key]) > 0
                
                # Check if this is today
                is_today = day_date == self.current_date
                
                # Check if this is selected
                is_selected = (display_row == self.selected_row and col_idx == self.selected_col)
                
                # Check if weekend
                is_weekend = col_idx >= 5
                
                # Color coding with priority
                if is_selected:
                    pygame.draw.rect(screen, self.selected_day_color, day_rect)
                elif is_today:
                    pygame.draw.rect(screen, self.today_color, day_rect)
                elif has_events:
                    pygame.draw.rect(screen, self.event_color, day_rect)
                elif is_weekend:
                    pygame.draw.rect(screen, self.weekend_color, day_rect)
                
                # Border
                border_color = BUTTON_SELECTED_BORDER if is_selected else BUTTON_BORDER_COLOR
                pygame.draw.rect(screen, border_color, day_rect, 2 if is_selected else 1)
                
                # Day number
                day_text = str(day)
                text_color = TEXT_COLOR
                if is_today or has_events:
                    text_color = (0, 0, 0)  # Black text for better contrast
                elif is_weekend:
                    text_color = WARNING_COLOR
                    
                day_surface = self.os.font_s.render(day_text, True, text_color)
                day_text_x = x + 5
                day_text_y = y + 5
                screen.blit(day_surface, (day_text_x, day_text_y))
                
                # Event indicator
                if has_events:
                    event_count = len(self.events[day_key])
                    if event_count > 0:
                        indicator_rect = pygame.Rect(x + 35, y + 2, 12, 8)
                        pygame.draw.rect(screen, SUCCESS_COLOR, indicator_rect)
                        count_surface = self.os.font_tiny.render(str(event_count), True, (0, 0, 0))
                        screen.blit(count_surface, (x + 37, y + 2))
        
        # Scroll indicators
        if self.scroll_offset > 0:
            up_arrow = self.os.font_s.render("▲", True, ACCENT_COLOR)
            screen.blit(up_arrow, (SCREEN_WIDTH - 30, 45))
            
        if self.scroll_offset + visible_rows < len(self.calendar_grid):
            down_arrow = self.os.font_s.render("▼", True, ACCENT_COLOR)
            screen.blit(down_arrow, (SCREEN_WIDTH - 30, 180))
        
        # Instructions
        instructions = [
            f"Mode: {self.nav_mode.upper()} | Tab: Switch mode",
            "Arrows: Navigate | Shift+←→: Month | Enter: Add event | ESC: Back"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.os.font_tiny.render(instruction, True, HIGHLIGHT_COLOR)
            screen.blit(inst_surface, (10, SCREEN_HEIGHT - 40 + i * 12))

    def draw_month_selector(self, screen):
        """Draw month selection interface"""
        # Header
        header_text = f"Select Month - {self.year_selected}"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Month grid
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        
        for i, month in enumerate(months):
            row = i // 3
            col = i % 3
            
            x = 20 + col * 120
            y = 40 + row * 30
            
            month_rect = pygame.Rect(x, y, 110, 25)
            
            # Highlight current month
            if i + 1 == self.month_selected:
                pygame.draw.rect(screen, SELECTED_COLOR, month_rect)
            elif i + 1 == self.view_date.month:
                pygame.draw.rect(screen, self.today_color, month_rect)
            
            pygame.draw.rect(screen, BUTTON_BORDER_COLOR, month_rect, 1)
            
            text_color = TEXT_COLOR
            if i + 1 == self.month_selected:
                text_color = (255, 255, 255)
            elif i + 1 == self.view_date.month:
                text_color = (0, 0, 0)
            
            month_surface = self.os.font_s.render(month, True, text_color)
            month_text_x = x + 5
            month_text_y = y + 5
            screen.blit(month_surface, (month_text_x, month_text_y))
        
        # Instructions
        instructions = [
            "Up/Down: Navigate | Enter: Select | Tab: Switch mode | ESC: Back"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.os.font_tiny.render(instruction, True, HIGHLIGHT_COLOR)
            screen.blit(inst_surface, (10, SCREEN_HEIGHT - 25 + i * 12))

    def draw_year_selector(self, screen):
        """Draw year selection interface"""
        # Header
        header_text = f"Select Year"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Year display
        year_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, 60, 100, 40)
        pygame.draw.rect(screen, SELECTED_COLOR, year_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, year_rect, 2)
        
        year_text = str(self.year_selected)
        year_surface = self.os.font_l.render(year_text, True, TEXT_COLOR)
        year_text_x = SCREEN_WIDTH // 2 - year_surface.get_width() // 2
        year_text_y = 75
        screen.blit(year_surface, (year_text_x, year_text_y))
        
        # Current year indicator
        current_year = date.today().year
        if self.year_selected == current_year:
            current_text = "(Current Year)"
            current_surface = self.os.font_s.render(current_text, True, SUCCESS_COLOR)
            current_x = SCREEN_WIDTH // 2 - current_surface.get_width() // 2
            screen.blit(current_surface, (current_x, 110))
        
        # Instructions
        instructions = [
            "Up/Down: Change year | Enter: Select | Tab: Switch mode | ESC: Back"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.os.font_tiny.render(instruction, True, HIGHLIGHT_COLOR)
            screen.blit(inst_surface, (10, SCREEN_HEIGHT - 25 + i * 12))

    def draw_event_input(self, screen):
        """Draw event input interface with 24-hour time wheel"""
        # Header
        header_text = f"Add Event - {self.selected_day.strftime('%B %d, %Y')}"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        y_offset = 35
        
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
        
        # Time field with 24-hour wheel
        y_offset += 60
        time_label = "Time (24H):"
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
            
            # Instructions
            inst_text = "↑↓: Change | ←→: Hour/Min"
            inst_surface = self.os.font_tiny.render(inst_text, True, HIGHLIGHT_COLOR)
            screen.blit(inst_surface, (20, y_offset + 55))
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
            "Enter: Save event | Tab: Switch field | ESC: Cancel"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.os.font_tiny.render(instruction, True, HIGHLIGHT_COLOR)
            screen.blit(inst_surface, (10, SCREEN_HEIGHT - 25 + i * 12))

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
