"""
Notes Module for LightBerry OS

"""

import pygame
from datetime import datetime
from config.constants import *

class Notes:
    def __init__(self, os_instance):
        self.os = os_instance
        self.init_notes()
    
    def init_notes(self):
        """Initialize notes state"""
        self.notes = []
        self.mode = "list"
        self.selected_index = 0
        self.scroll_offset = 0
        self.visible_items = 6
        
        # Editing/Adding note
        self.editing_index = -1
        self.input_mode = "title"
        self.current_title = ""
        self.current_description = ""
        self.current_priority = "medium"
        self.current_category = "general"
        self.description_lines = []
        self.description_scroll = 0
        
        # Categories
        self.categories = ["general", "work", "personal", "shopping", "ideas"]
        self.category_colors = {
            "general": HIGHLIGHT_COLOR,
            "work": (255, 200, 100),
            "personal": (100, 255, 200),
            "shopping": (200, 100, 255),
            "ideas": (255, 100, 200)
        }
        
        # Priority configuration
        self.priorities = ["low", "medium", "high"]
        self.priority_colors = {
            "high": HIGH_PRIORITY_COLOR,
            "medium": MEDIUM_PRIORITY_COLOR,
            "low": LOW_PRIORITY_COLOR
        }
        
        self.priority_labels = {
            "high": "High",
            "medium": "Medium",
            "low": "Low"
        }
        
        # Text input
        self.text_cursor_visible = True
        self.text_cursor_timer = 0
        
        # Input field selection for editing
        self.input_fields = ["title", "description", "priority", "category"]
        self.input_field_index = 0
    
    def handle_events(self, event):
        """Handle notes events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.mode == "edit" or self.mode == "add":
                    self.cancel_edit()
                else:
                    return "back"
            
            elif self.mode == "list":
                self.handle_list_events(event)
            
            elif self.mode == "view":
                self.handle_view_events(event)
            
            elif self.mode == "edit" or self.mode == "add":
                self.handle_edit_events(event)
        
        return None
    
    def handle_list_events(self, event):
        """Handle list view events"""
        if event.key == pygame.K_UP:
            self.selected_index = max(0, self.selected_index - 1)
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = max(0, self.scroll_offset - 1)
        
        elif event.key == pygame.K_DOWN:
            self.selected_index = min(len(self.notes) - 1, self.selected_index + 1)
            if self.selected_index >= self.scroll_offset + self.visible_items:
                self.scroll_offset = min(len(self.notes) - self.visible_items, self.scroll_offset + 1)
        
        elif event.key == pygame.K_RETURN:
            if self.notes:
                self.mode = "view"
                self.description_scroll = 0
        
        elif event.key == pygame.K_a:
            self.start_add_note()
        
        elif event.key == pygame.K_e:
            if self.notes:
                self.start_edit_note()
        
        elif event.key == pygame.K_t:
            if self.notes:
                self.delete_note()
        
        elif event.key == pygame.K_s:
            self.sort_notes()
    
    def handle_view_events(self, event):
        """Handle view events"""
        if event.key == pygame.K_UP:
            self.description_scroll = max(0, self.description_scroll - 1)
        
        elif event.key == pygame.K_DOWN:
            max_scroll = max(0, len(self.description_lines) - 5)
            self.description_scroll = min(max_scroll, self.description_scroll + 1)
        
        elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
            self.mode = "list"
        
        elif event.key == pygame.K_e:
            self.start_edit_note()
        
        elif event.key == pygame.K_t:
            self.delete_note()
            self.mode = "list"
    
    def handle_edit_events(self, event):
        """Handle edit events"""
        if event.key == pygame.K_TAB:
            self.input_field_index = (self.input_field_index + 1) % len(self.input_fields)
            self.input_mode = self.input_fields[self.input_field_index]
        
        elif event.key == pygame.K_UP:
            if self.input_mode == "priority":
                current_idx = self.priorities.index(self.current_priority)
                self.current_priority = self.priorities[(current_idx - 1) % len(self.priorities)]
            elif self.input_mode == "category":
                current_idx = self.categories.index(self.current_category)
                self.current_category = self.categories[(current_idx - 1) % len(self.categories)]
            else:
                self.input_field_index = (self.input_field_index - 1) % len(self.input_fields)
                self.input_mode = self.input_fields[self.input_field_index]
        
        elif event.key == pygame.K_DOWN:
            if self.input_mode == "priority":
                current_idx = self.priorities.index(self.current_priority)
                self.current_priority = self.priorities[(current_idx + 1) % len(self.priorities)]
            elif self.input_mode == "category":
                current_idx = self.categories.index(self.current_category)
                self.current_category = self.categories[(current_idx + 1) % len(self.categories)]
            else:
                self.input_field_index = (self.input_field_index + 1) % len(self.input_fields)
                self.input_mode = self.input_fields[self.input_field_index]
        
        elif event.key == pygame.K_RETURN:
            if self.input_mode == "description":
                self.current_description += "\n"
            else:
                self.save_note()
        
        elif event.key == pygame.K_BACKSPACE:
            if self.input_mode == "title":
                self.current_title = self.current_title[:-1]
            elif self.input_mode == "description":
                self.current_description = self.current_description[:-1]
        
        else:
            char = event.unicode
            if char.isprintable():
                if self.input_mode == "title" and len(self.current_title) < 50:
                    self.current_title += char
                elif self.input_mode == "description" and len(self.current_description) < 500:
                    self.current_description += char
    
    def start_add_note(self):
        """Start adding new note"""
        self.mode = "add"
        self.editing_index = -1
        self.input_mode = "title"
        self.input_field_index = 0
        self.current_title = ""
        self.current_description = ""
        self.current_priority = "medium"
        self.current_category = "general"
    
    def start_edit_note(self):
        """Start editing existing note"""
        if not self.notes or self.selected_index >= len(self.notes):
            return
        
        note = self.notes[self.selected_index]
        self.mode = "edit"
        self.editing_index = self.selected_index
        self.input_mode = "title"
        self.input_field_index = 0
        self.current_title = note["title"]
        self.current_description = note["description"]
        self.current_priority = note.get("priority", "medium")
        self.current_category = note.get("category", "general")
    
    def save_note(self):
        """Save current note"""
        if not self.current_title.strip():
            return
        
        note = {
            "title": self.current_title.strip(),
            "description": self.current_description.strip(),
            "priority": self.current_priority,
            "category": self.current_category,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }
        
        if self.mode == "edit":
            note["created"] = self.notes[self.editing_index]["created"]
            self.notes[self.editing_index] = note
        else:
            self.notes.append(note)
        
        self.mode = "list"
        self.sort_notes()
    
    def cancel_edit(self):
        """Cancel editing"""
        self.mode = "list"
        self.current_title = ""
        self.current_description = ""
        self.current_priority = "medium"
        self.current_category = "general"
    
    def delete_note(self):
        """Delete selected note"""
        if self.notes and self.selected_index < len(self.notes):
            del self.notes[self.selected_index]
            self.selected_index = min(self.selected_index, len(self.notes) - 1)
            if self.selected_index < 0:
                self.selected_index = 0
            self.adjust_scroll()
    
    def sort_notes(self):
        """Sort notes by priority and date"""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        
        self.notes.sort(key=lambda x: (
            priority_order.get(x.get("priority", "medium"), 1),
            x.get("modified", x.get("created", ""))
        ), reverse=True)
        
        self.selected_index = 0
        self.scroll_offset = 0
    
    def adjust_scroll(self):
        """Adjust scroll offset"""
        if self.scroll_offset > 0 and self.scroll_offset >= len(self.notes):
            self.scroll_offset = max(0, len(self.notes) - self.visible_items)
    
    def wrap_text(self, text, max_width):
        """Wrap text to fit within width"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_width = self.os.font_m.get_text_width(test_line) if hasattr(self.os.font_m, 'get_text_width') else len(test_line) * 12
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def update(self):
        """Update notes state"""
        # Update text cursor
        self.text_cursor_timer += 1
        if self.text_cursor_timer >= 30:
            self.text_cursor_visible = not self.text_cursor_visible
            self.text_cursor_timer = 0
        
        # Update description lines for current note
        if self.mode == "view" and self.notes:
            note = self.notes[self.selected_index]
            self.description_lines = self.wrap_text(note["description"], SCREEN_WIDTH - 40)
    
    def draw(self, screen):
        """Draw notes interface"""
        if self.mode == "list":
            self.draw_list_view(screen)
        elif self.mode == "view":
            self.draw_view_mode(screen)
        elif self.mode == "edit" or self.mode == "add":
            self.draw_edit_mode(screen)
    
    def draw_list_view(self, screen):
        """Draw list view"""
        # Header
        header_text = f"Notes ({len(self.notes)})"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Notes list
        if not self.notes:
            no_notes_text = "No notes yet"
            no_notes_surface = self.os.font_m.render(no_notes_text, True, HIGHLIGHT_COLOR)
            no_notes_x = SCREEN_WIDTH // 2 - no_notes_surface.get_width() // 2
            screen.blit(no_notes_surface, (no_notes_x, 60))
        else:
            y_offset = 35
            visible_notes = self.notes[self.scroll_offset:self.scroll_offset + self.visible_items]
            
            for i, note in enumerate(visible_notes):
                note_index = self.scroll_offset + i
                note_y = y_offset + i * 30
                
                # Note background
                note_rect = pygame.Rect(10, note_y, SCREEN_WIDTH - 20, 28)
                if note_index == self.selected_index:
                    pygame.draw.rect(screen, SELECTED_COLOR, note_rect)
                
                # Priority indicator
                priority_color = self.priority_colors.get(note.get("priority", "medium"), MEDIUM_PRIORITY_COLOR)
                pygame.draw.rect(screen, priority_color, (10, note_y, 5, 28))
                
                # Category indicator
                category_color = self.category_colors.get(note.get("category", "general"), HIGHLIGHT_COLOR)
                pygame.draw.circle(screen, category_color, (SCREEN_WIDTH - 20, note_y + 14), 4)
                
                # Note title
                title_text = note["title"]
                if len(title_text) > 35:
                    title_text = title_text[:35] + "..."
                
                title_surface = self.os.font_m.render(title_text, True, TEXT_COLOR)
                screen.blit(title_surface, (20, note_y + 2))
                
                # Note preview
                preview_text = note["description"].replace("\n", " ")
                if len(preview_text) > 40:
                    preview_text = preview_text[:40] + "..."
                
                preview_surface = self.os.font_s.render(preview_text, True, HIGHLIGHT_COLOR)
                screen.blit(preview_surface, (20, note_y + 16))
                
                # Action indicators
                if note_index == self.selected_index:
                    actions = "E:Edit T:Delete"
                    action_surface = self.os.font_s.render(actions, True, WARNING_COLOR)
                    screen.blit(action_surface, (SCREEN_WIDTH - 100, note_y + 2))
            
            # Scroll indicators
            if self.scroll_offset > 0:
                up_text = "↑ More above"
                up_surface = self.os.font_s.render(up_text, True, HIGHLIGHT_COLOR)
                screen.blit(up_surface, (10, 30))
            
            if self.scroll_offset + self.visible_items < len(self.notes):
                down_text = "↓ More below"
                down_surface = self.os.font_s.render(down_text, True, HIGHLIGHT_COLOR)
                screen.blit(down_surface, (10, SCREEN_HEIGHT - 65))
        
        # Controls
        controls = [
            "↑↓: Navigate",
            "Enter: View note",
            "A: Add note",
            "E: Edit note",
            "T: Delete note",
            "S: Sort notes"
        ]
        
        control_y = SCREEN_HEIGHT - 50
        for i, control in enumerate(controls):
            control_surface = self.os.font_s.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 3) * 125
            control_y_pos = control_y + (i // 3) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
        
        # Draw scroll bar
        self.draw_scroll_bar(screen, len(self.notes), self.visible_items, self.scroll_offset)
    
    def draw_view_mode(self, screen):
        """Draw view mode"""
        if not self.notes:
            return
        
        note = self.notes[self.selected_index]
        
        # Header
        header_surface = self.os.font_l.render("Note Details", True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Note title
        title_surface = self.os.font_m.render(note["title"], True, TEXT_COLOR)
        screen.blit(title_surface, (10, 30))
        
        # Priority and category
        priority_text = f"Priority: {self.priority_labels[note.get('priority', 'medium')]}"
        priority_surface = self.os.font_s.render(priority_text, True, 
                                               self.priority_colors[note.get('priority', 'medium')])
        screen.blit(priority_surface, (10, 50))
        
        category_text = f"Category: {note.get('category', 'general').title()}"
        category_surface = self.os.font_s.render(category_text, True, 
                                               self.category_colors[note.get('category', 'general')])
        screen.blit(category_surface, (150, 50))
        
        # Description
        desc_lines = self.wrap_text(note["description"], SCREEN_WIDTH - 20)
        visible_lines = desc_lines[self.description_scroll:self.description_scroll + 8]
        
        for i, line in enumerate(visible_lines):
            line_surface = self.os.font_m.render(line, True, TEXT_COLOR)
            screen.blit(line_surface, (10, 75 + i * 18))
        
        # Scroll indicators
        if self.description_scroll > 0:
            up_text = "↑ More above"
            up_surface = self.os.font_s.render(up_text, True, HIGHLIGHT_COLOR)
            screen.blit(up_surface, (10, 70))
        
        if self.description_scroll + 8 < len(desc_lines):
            down_text = "↓ More below"
            down_surface = self.os.font_s.render(down_text, True, HIGHLIGHT_COLOR)
            screen.blit(down_surface, (10, SCREEN_HEIGHT - 50))
        
        # Controls
        controls = [
            "↑↓: Scroll",
            "Enter/ESC: Back",
            "E: Edit",
            "T: Delete"
        ]
        
        control_y = SCREEN_HEIGHT - 35
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 2) * 180
            control_y_pos = control_y + (i // 2) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
        
        # Draw scroll bar for description
        desc_lines = note["description"].split("\n") if note["description"] else [""]
        self.draw_scroll_bar(screen, len(desc_lines), 8, self.description_scroll)
        
        # Draw scroll bar
        self.draw_scroll_bar(screen, len(self.notes), self.visible_items, self.scroll_offset)
    
    def draw_edit_mode(self, screen):
        """Draw edit mode"""
        # Header
        title = "Edit Note" if self.mode == "edit" else "Add Note"
        header_surface = self.os.font_l.render(title, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        y_offset = 35
        
        # Title field
        title_label = "Title:"
        title_surface = self.os.font_m.render(title_label, True, TEXT_COLOR)
        screen.blit(title_surface, (10, y_offset))
        
        title_rect = pygame.Rect(10, y_offset + 20, SCREEN_WIDTH - 20, 25)
        title_color = SELECTED_COLOR if self.input_mode == "title" else BUTTON_COLOR
        pygame.draw.rect(screen, title_color, title_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, title_rect, 2)
        
        title_text = self.current_title
        if self.input_mode == "title" and self.text_cursor_visible:
            title_text += "|"
        
        title_text_surface = self.os.font_m.render(title_text, True, TEXT_COLOR)
        screen.blit(title_text_surface, (15, y_offset + 22))
        
        # Description field
        y_offset += 50
        desc_label = "Description:"
        desc_surface = self.os.font_m.render(desc_label, True, TEXT_COLOR)
        screen.blit(desc_surface, (10, y_offset))
        
        desc_rect = pygame.Rect(10, y_offset + 20, SCREEN_WIDTH - 20, 60)
        desc_color = SELECTED_COLOR if self.input_mode == "description" else BUTTON_COLOR
        pygame.draw.rect(screen, desc_color, desc_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, desc_rect, 2)
        
        desc_text = self.current_description
        if self.input_mode == "description" and self.text_cursor_visible:
            desc_text += "|"
        
        # Wrap description text
        desc_lines = self.wrap_text(desc_text, SCREEN_WIDTH - 30)
        for i, line in enumerate(desc_lines[:3]):  # Show first 3 lines
            line_surface = self.os.font_m.render(line, True, TEXT_COLOR)
            screen.blit(line_surface, (15, y_offset + 25 + i * 18))
        
        # Priority field
        y_offset += 85
        priority_label = "Priority:"
        priority_surface = self.os.font_m.render(priority_label, True, TEXT_COLOR)
        screen.blit(priority_surface, (10, y_offset))
        
        priority_rect = pygame.Rect(10, y_offset + 20, (SCREEN_WIDTH - 30) // 2, 25)
        priority_color = SELECTED_COLOR if self.input_mode == "priority" else BUTTON_COLOR
        pygame.draw.rect(screen, priority_color, priority_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, priority_rect, 2)
        
        priority_text = self.priority_labels[self.current_priority]
        priority_text_surface = self.os.font_m.render(priority_text, True, 
                                                    self.priority_colors[self.current_priority])
        screen.blit(priority_text_surface, (15, y_offset + 22))
        
        # Category field
        category_rect = pygame.Rect(SCREEN_WIDTH // 2 + 5, y_offset + 20, 
                                   (SCREEN_WIDTH - 30) // 2, 25)
        category_color = SELECTED_COLOR if self.input_mode == "category" else BUTTON_COLOR
        pygame.draw.rect(screen, category_color, category_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, category_rect, 2)
        
        category_text = self.current_category.title()
        category_text_surface = self.os.font_m.render(category_text, True, 
                                                    self.category_colors[self.current_category])
        screen.blit(category_text_surface, (SCREEN_WIDTH // 2 + 10, y_offset + 22))
        
        # Controls removed from edit mode
    
    def draw_scroll_bar(self, screen, total_items, visible_items, current_offset):
        """Draw a visual scroll bar"""
        if total_items <= visible_items:
            return
            
        # Calculate scroll bar dimensions
        bar_height = max(20, int((SCREEN_HEIGHT - 100) * (visible_items / total_items)))
        bar_start = 50 + int(((SCREEN_HEIGHT - 150) * current_offset) / max(1, total_items - visible_items))
        
        # Draw scroll track
        track_rect = pygame.Rect(SCREEN_WIDTH - 15, 50, 8, SCREEN_HEIGHT - 100)
        pygame.draw.rect(screen, BUTTON_COLOR, track_rect)
        
        # Draw scroll thumb
        thumb_rect = pygame.Rect(SCREEN_WIDTH - 14, bar_start, 6, bar_height)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, thumb_rect)

        def save_data(self):
            """Save notes data"""
            return {
                "notes": self.notes
            }
        
    def load_data(self, data):
        """Load notes data"""
        self.notes = data.get("notes", [])
        self.sort_notes()
