"""
Enhanced Calendar Module for LightBerry OS
Professional calendar with events, notifications, and scrolling
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
        self.selected_day = date.today()
        self.events = {}
        self.mode = "month_view"
        
        # Navigation
        self.selected_row = 0
        self.selected_col = 0
        self.grid_start_row = 0
        self.scroll_offset = 0
        
        # Event management
        self.adding_event = False
        self.editing_event = False
        self.event_index = 0
        self.input_mode = "title"
        self.event_title = ""
        self.event_time = ""
        self.event_description = ""
        self.selected_event = 0
        
        # Generate calendar grid
        self.generate_calendar_grid()
        
        # Text input
        self.text_cursor_visible = True
        self.text_cursor_timer = 0
        
        # Notifications
        self.last_notification_check = datetime.now()
    
    def generate_calendar_grid(self):
        """Generate calendar grid for current month"""
        self.calendar_grid = calendar.monthcalendar(self.view_date.year, self.view_date.month)
        
        # Find today's position if in current month
        if (self.view_date.year == self.current_date.year and 
            self.view_date.month == self.current_date.month):
            for row_idx, week in enumerate(self.calendar_grid):
                for col_idx, day in enumerate(week):
                    if day == self.current_date.day:
                        self.selected_row = row_idx
                        self.selected_col = col_idx
                        return
    
    def handle_events(self, event):
        """Handle calendar events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.adding_event or self.editing_event:
                    self.cancel_event_edit()
                else:
                    return "back"
            
            elif self.adding_event or self.editing_event:
                self.handle_event_input(event)
            
            elif self.mode == "month_view":
                self.handle_month_view_events(event)
            
            elif self.mode == "event_view":
                self.handle_event_view_events(event)
        
        return None
    
    def handle_month_view_events(self, event):
        """Handle month view navigation"""
        if event.key == pygame.K_UP:
            if self.selected_row > 0:
                self.selected_row -= 1
            else:
                self.previous_month()
        
        elif event.key == pygame.K_DOWN:
            if self.selected_row < len(self.calendar_grid) - 1:
                self.selected_row += 1
            else:
                self.next_month()
        
        elif event.key == pygame.K_LEFT:
            if self.selected_col > 0:
                self.selected_col -= 1
            else:
                self.selected_col = 6
                if self.selected_row > 0:
                    self.selected_row -= 1
        
        elif event.key == pygame.K_RIGHT:
            if self.selected_col < 6:
                self.selected_col += 1
            else:
                self.selected_col = 0
                if self.selected_row < len(self.calendar_grid) - 1:
                    self.selected_row += 1
        
        elif event.key == pygame.K_RETURN:
            day = self.get_selected_day()
            if day > 0:
                self.selected_day = date(self.view_date.year, self.view_date.month, day)
                if self.has_events(self.selected_day):
                    self.mode = "event_view"
                    self.scroll_offset = 0
                else:
                    self.start_add_event()
        
        elif event.key == pygame.K_a:
            day = self.get_selected_day()
            if day > 0:
                self.selected_day = date(self.view_date.year, self.view_date.month, day)
                self.start_add_event()
        
        elif event.key == pygame.K_n:
            self.next_month()
        
        elif event.key == pygame.K_p:
            self.previous_month()
    
    def handle_event_view_events(self, event):
        """Handle event view navigation"""
        if event.key == pygame.K_UP:
            self.scroll_offset = max(0, self.scroll_offset - 1)
        
        elif event.key == pygame.K_DOWN:
            max_scroll = max(0, len(self.get_day_events(self.selected_day)) - 3)
            self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
        
        elif event.key == pygame.K_RETURN:
            self.mode = "month_view"
        
        elif event.key == pygame.K_a:
            self.start_add_event()
        
        elif event.key == pygame.K_e:
            events = self.get_day_events(self.selected_day)
            if events and self.scroll_offset < len(events):
                self.event_index = self.scroll_offset
                self.start_edit_event()
        
        elif event.key == pygame.K_t:
            events = self.get_day_events(self.selected_day)
            if events and self.scroll_offset < len(events):
                self.delete_event(self.selected_day, self.scroll_offset)
    
    def handle_event_input(self, event):
        """Handle event input"""
        if event.key == pygame.K_RETURN:
            if self.input_mode == "title":
                self.input_mode = "time"
            elif self.input_mode == "time":
                self.input_mode = "description"
            elif self.input_mode == "description":
                self.save_event()
        
        elif event.key == pygame.K_TAB:
            if self.input_mode == "title":
                self.input_mode = "time"
            elif self.input_mode == "time":
                self.input_mode = "description"
            elif self.input_mode == "description":
                self.input_mode = "title"
        
        elif event.key == pygame.K_BACKSPACE:
            if self.input_mode == "title":
                self.event_title = self.event_title[:-1]
            elif self.input_mode == "time":
                self.event_time = self.event_time[:-1]
            elif self.input_mode == "description":
                self.event_description = self.event_description[:-1]
        
        else:
            char = event.unicode
            if char.isprintable():
                if self.input_mode == "title" and len(self.event_title) < 30:
                    self.event_title += char
                elif self.input_mode == "time" and len(self.event_time) < 8:
                    self.event_time += char
                elif self.input_mode == "description" and len(self.event_description) < 100:
                    self.event_description += char
    
    def get_selected_day(self):
        """Get currently selected day"""
        if (0 <= self.selected_row < len(self.calendar_grid) and
            0 <= self.selected_col < len(self.calendar_grid[self.selected_row])):
            return self.calendar_grid[self.selected_row][self.selected_col]
        return 0
    
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
    
    def start_add_event(self):
        """Start adding new event"""
        self.adding_event = True
        self.input_mode = "title"
        self.event_title = ""
        self.event_time = ""
        self.event_description = ""
    
    def start_edit_event(self):
        """Start editing existing event"""
        events = self.get_day_events(self.selected_day)
        if events and self.event_index < len(events):
            event = events[self.event_index]
            self.editing_event = True
            self.input_mode = "title"
            self.event_title = event.get("title", "")
            self.event_time = event.get("time", "")
            self.event_description = event.get("description", "")
    
    def save_event(self):
        """Save current event"""
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
        
        if self.editing_event:
            self.events[day_key][self.event_index] = event
        else:
            self.events[day_key].append(event)
        
        self.cancel_event_edit()
    
    def cancel_event_edit(self):
        """Cancel event editing"""
        self.adding_event = False
        self.editing_event = False
        self.event_title = ""
        self.event_time = ""
        self.event_description = ""
    
    def delete_event(self, day, event_index):
        """Delete an event"""
        day_key = day.strftime("%Y-%m-%d")
        if day_key in self.events and event_index < len(self.events[day_key]):
            del self.events[day_key][event_index]
            if not self.events[day_key]:
                del self.events[day_key]
    
    def has_events(self, day):
        """Check if day has events"""
        day_key = day.strftime("%Y-%m-%d")
        return day_key in self.events and len(self.events[day_key]) > 0
    
    def get_day_events(self, day):
        """Get events for a specific day"""
        day_key = day.strftime("%Y-%m-%d")
        return self.events.get(day_key, [])
    
    def check_notifications(self):
        """Check for event notifications"""
        now = datetime.now()
        
        # Check only once per minute
        if (now - self.last_notification_check).seconds < 60:
            return
        
        self.last_notification_check = now
        
        # Check today's events
        today_events = self.get_day_events(date.today())
        
        for event in today_events:
            if event.get("time"):
                try:
                    # Parse time (assume format HH:MM)
                    time_str = event["time"]
                    if ":" in time_str:
                        hour, minute = map(int, time_str.split(":"))
                        event_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        
                        # Check if event is happening now (within 1 minute)
                        time_diff = abs((now - event_time).total_seconds())
                        if time_diff <= 60:
                            self.os.notification_manager.add_event_notification(
                                event["title"], 
                                event["time"]
                            )
                except:
                    pass
    
    def update(self):
        """Update calendar state"""
        # Update text cursor
        self.text_cursor_timer += 1
        if self.text_cursor_timer >= 30:
            self.text_cursor_visible = not self.text_cursor_visible
            self.text_cursor_timer = 0
    
    def draw(self, screen):
        """Draw calendar interface"""
        if self.adding_event or self.editing_event:
            self.draw_event_editor(screen)
        elif self.mode == "event_view":
            self.draw_event_view(screen)
        else:
            self.draw_month_view(screen)
    
    def draw_month_view(self, screen):
        """Draw month view"""
        # Header
        month_name = self.view_date.strftime("%B %Y")
        header_surface = self.os.font_l.render(month_name, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Day headers
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_width = (SCREEN_WIDTH - 20) // 7
        
        for i, day_name in enumerate(day_names):
            day_surface = self.os.font_s.render(day_name, True, HIGHLIGHT_COLOR)
            day_x = 10 + i * day_width + (day_width - day_surface.get_width()) // 2
            screen.blit(day_surface, (day_x, 35))
        
        # Calendar grid
        cell_height = 22
        start_y = 55
        
        for row_idx, week in enumerate(self.calendar_grid):
            for col_idx, day in enumerate(week):
                if day == 0:
                    continue
                
                x = 10 + col_idx * day_width
                y = start_y + row_idx * cell_height
                
                # Cell background
                cell_rect = pygame.Rect(x, y, day_width, cell_height)
                
                # Colors
                if row_idx == self.selected_row and col_idx == self.selected_col:
                    pygame.draw.rect(screen, CALENDAR_SELECTED_COLOR, cell_rect)
                elif (self.view_date.year == self.current_date.year and 
                      self.view_date.month == self.current_date.month and 
                      day == self.current_date.day):
                    pygame.draw.rect(screen, CALENDAR_TODAY_COLOR, cell_rect)
                
                # Event indicator
                day_date = date(self.view_date.year, self.view_date.month, day)
                if self.has_events(day_date):
                    pygame.draw.circle(screen, CALENDAR_EVENT_COLOR, 
                                     (x + day_width - 8, y + 8), 3)
                
                # Day number
                day_surface = self.os.font_m.render(str(day), True, TEXT_COLOR)
                day_x = x + (day_width - day_surface.get_width()) // 2
                day_y = y + (cell_height - day_surface.get_height()) // 2
                screen.blit(day_surface, (day_x, day_y))
        
        # Controls
        controls = [
            "Arrow keys: Navigate",
            "Enter: Select/View events",
            "A: Add event",
            "N/P: Next/Previous month"
        ]
        
        control_y = SCREEN_HEIGHT - 50
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 2) * 190
            control_y_pos = control_y + (i // 2) * 15
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def draw_event_view(self, screen):
        """Draw event view with scrolling"""
        # Header
        date_str = self.selected_day.strftime("%B %d, %Y")
        header_surface = self.os.font_l.render(date_str, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Events
        events = self.get_day_events(self.selected_day)
        
        if not events:
            no_events_text = "No events for this day"
            no_events_surface = self.os.font_m.render(no_events_text, True, HIGHLIGHT_COLOR)
            no_events_x = SCREEN_WIDTH // 2 - no_events_surface.get_width() // 2
            screen.blit(no_events_surface, (no_events_x, 50))
        else:
            # Draw visible events
            y_offset = 35
            visible_events = events[self.scroll_offset:self.scroll_offset + 3]
            
            for i, event in enumerate(visible_events):
                event_y = y_offset + i * 40
                
                # Event background
                event_rect = pygame.Rect(10, event_y, SCREEN_WIDTH - 20, 35)
                if i == 0:  # Highlight first visible event
                    pygame.draw.rect(screen, SELECTED_COLOR, event_rect)
                
                pygame.draw.rect(screen, BUTTON_BORDER_COLOR, event_rect, 1)
                
                # Event title and time
                title_time = f"{event['title']} - {event['time']}"
                title_surface = self.os.font_m.render(title_time, True, TEXT_COLOR)
                screen.blit(title_surface, (15, event_y + 5))
                
                # Event description (if fits)
                if event['description']:
                    desc_surface = self.os.font_s.render(event['description'], True, HIGHLIGHT_COLOR)
                    screen.blit(desc_surface, (15, event_y + 20))
                
                # Action indicators
                edit_text = "E:Edit"
                delete_text = "T:Delete"
                edit_surface = self.os.font_tiny.render(edit_text, True, SUCCESS_COLOR)
                delete_surface = self.os.font_tiny.render(delete_text, True, ERROR_COLOR)
                
                screen.blit(edit_surface, (SCREEN_WIDTH - 80, event_y + 5))
                screen.blit(delete_surface, (SCREEN_WIDTH - 80, event_y + 18))
            
            # Scroll indicators
            if self.scroll_offset > 0:
                up_arrow = "↑ More above"
                up_surface = self.os.font_tiny.render(up_arrow, True, HIGHLIGHT_COLOR)
                screen.blit(up_surface, (10, 30))
            
            if self.scroll_offset + 3 < len(events):
                down_arrow = "↓ More below"
                down_surface = self.os.font_tiny.render(down_arrow, True, HIGHLIGHT_COLOR)
                screen.blit(down_surface, (10, SCREEN_HEIGHT - 60))
        
        # Controls
        controls = [
            "↑↓: Scroll events",
            "Enter: Back to calendar",
            "A: Add event",
            "E: Edit event",
            "T: Delete event"
        ]
        
        control_y = SCREEN_HEIGHT - 45
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 2) * 190
            control_y_pos = control_y + (i // 2) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def draw_event_editor(self, screen):
        """Draw event editor"""
        # Header
        title = "Edit Event" if self.editing_event else "Add Event"
        header_surface = self.os.font_l.render(title, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Date
        date_str = self.selected_day.strftime("%B %d, %Y")
        date_surface = self.os.font_m.render(date_str, True, HIGHLIGHT_COLOR)
        date_x = SCREEN_WIDTH // 2 - date_surface.get_width() // 2
        screen.blit(date_surface, (date_x, 30))
        
        # Input fields
        y_offset = 55
        
        # Title field
        title_label = "Title:"
        title_surface = self.os.font_s.render(title_label, True, TEXT_COLOR)
        screen.blit(title_surface, (10, y_offset))
        
        title_rect = pygame.Rect(10, y_offset + 20, SCREEN_WIDTH - 20, 25)
        title_color = SELECTED_COLOR if self.input_mode == "title" else BUTTON_COLOR
        pygame.draw.rect(screen, title_color, title_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, title_rect, 2)
        
        title_text = self.event_title
        if self.input_mode == "title" and self.text_cursor_visible:
            title_text += "|"
        
        title_text_surface = self.os.font_s.render(title_text, True, TEXT_COLOR)
        screen.blit(title_text_surface, (15, y_offset + 25))
        
        # Time field
        y_offset += 50
        time_label = "Time (HH:MM):"
        time_surface = self.os.font_s.render(time_label, True, TEXT_COLOR)
        screen.blit(time_surface, (10, y_offset))
        
        time_rect = pygame.Rect(10, y_offset + 20, SCREEN_WIDTH - 20, 25)
        time_color = SELECTED_COLOR if self.input_mode == "time" else BUTTON_COLOR
        pygame.draw.rect(screen, time_color, time_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, time_rect, 2)
        
        time_text = self.event_time
        if self.input_mode == "time" and self.text_cursor_visible:
            time_text += "|"
        
        time_text_surface = self.os.font_s.render(time_text, True, TEXT_COLOR)
        screen.blit(time_text_surface, (15, y_offset + 25))
        
        # Description field
        y_offset += 50
        desc_label = "Description:"
        desc_surface = self.os.font_s.render(desc_label, True, TEXT_COLOR)
        screen.blit(desc_surface, (10, y_offset))
        
        desc_rect = pygame.Rect(10, y_offset + 20, SCREEN_WIDTH - 20, 25)
        desc_color = SELECTED_COLOR if self.input_mode == "description" else BUTTON_COLOR
        pygame.draw.rect(screen, desc_color, desc_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, desc_rect, 2)
        
        desc_text = self.event_description
        if self.input_mode == "description" and self.text_cursor_visible:
            desc_text += "|"
        
        desc_text_surface = self.os.font_s.render(desc_text, True, TEXT_COLOR)
        screen.blit(desc_text_surface, (15, y_offset + 25))
        
        # Controls
        controls = [
            "Enter: Next field/Save",
            "Tab: Next field",
            "ESC: Cancel"
        ]
        
        control_y = SCREEN_HEIGHT - 35
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 2) * 190
            control_y_pos = control_y + (i // 2) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def save_data(self):
        """Save calendar data"""
        return {
            "events": self.events
        }
    
    def load_data(self, data):
        """Load calendar data"""
        self.events = data.get("events", {})
