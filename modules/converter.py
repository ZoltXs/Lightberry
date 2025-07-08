"""
Enhanced Converter Module for LightBerry OS
Professional unit converter with multiple categories and improved input
"""

import pygame
import math
from config.constants import *

class Converter:
    def __init__(self, os_instance):
        self.os = os_instance
        self.init_converter()
    
    def init_converter(self):
        """Initialize converter state"""
        self.categories = {
            "Length": {
                "units": ["mm", "cm", "m", "km", "in", "ft", "yd", "mi"],
                "base_unit": "m",
                "conversions": {
                    "mm": 0.001, "cm": 0.01, "m": 1, "km": 1000,
                    "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.34
                }
            },
            "Weight": {
                "units": ["mg", "g", "kg", "lb", "oz", "ton"],
                "base_unit": "kg",
                "conversions": {
                    "mg": 0.000001, "g": 0.001, "kg": 1,
                    "lb": 0.453592, "oz": 0.0283495, "ton": 1000
                }
            },
            "Temperature": {
                "units": ["°C", "°F", "K"],
                "base_unit": "°C",
                "conversions": None  # Special handling
            },
            "Volume": {
                "units": ["ml", "l", "m³", "gal", "qt", "pt", "fl oz"],
                "base_unit": "l",
                "conversions": {
                    "ml": 0.001, "l": 1, "m³": 1000,
                    "gal": 3.78541, "qt": 0.946353, "pt": 0.473176, "fl oz": 0.0295735
                }
            },
            "Area": {
                "units": ["mm²", "cm²", "m²", "km²", "in²", "ft²", "yd²", "acre"],
                "base_unit": "m²",
                "conversions": {
                    "mm²": 0.000001, "cm²": 0.0001, "m²": 1, "km²": 1000000,
                    "in²": 0.00064516, "ft²": 0.092903, "yd²": 0.836127, "acre": 4046.86
                }
            },
            "Speed": {
                "units": ["m/s", "km/h", "mph", "knot", "ft/s"],
                "base_unit": "m/s",
                "conversions": {
                    "m/s": 1, "km/h": 0.277778, "mph": 0.44704,
                    "knot": 0.514444, "ft/s": 0.3048
                }
            }
        }
        
        self.current_category = "Length"
        self.from_unit_index = 0
        self.to_unit_index = 1
        self.input_value = ""
        self.result_value = ""
        self.selected_field = "value"  # "value", "from_unit", "to_unit", "category"
        
        # Navigation
        self.field_order = ["value", "from_unit", "to_unit", "category"]
        self.field_index = 0
        
        # Text input
        self.text_cursor_visible = True
        self.text_cursor_timer = 0
        
        # Number input mode
        self.number_input_mode = True
        self.decimal_entered = False
        
        # Initialize with default values
        self.input_value = "1"
        self.calculate_conversion()
    
    def handle_events(self, event):
        """Handle converter events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            
            elif event.key == pygame.K_TAB:
                self.field_index = (self.field_index + 1) % len(self.field_order)
                self.selected_field = self.field_order[self.field_index]
            
            elif event.key == pygame.K_UP:
                self.handle_navigation(-1)
            
            elif event.key == pygame.K_DOWN:
                self.handle_navigation(1)
            
            elif event.key == pygame.K_LEFT:
                if self.selected_field == "value":
                    pass  # Could move cursor in value field
                else:
                    self.handle_navigation(-1)
            
            elif event.key == pygame.K_RIGHT:
                if self.selected_field == "value":
                    pass  # Could move cursor in value field
                else:
                    self.handle_navigation(1)
            
            elif event.key == pygame.K_RETURN:
                self.calculate_conversion()
            
            elif event.key == pygame.K_BACKSPACE:
                if self.selected_field == "value":
                    self.input_value = self.input_value[:-1]
                    if not self.input_value:
                        self.input_value = "0"
                    self.decimal_entered = "." in self.input_value
                    self.calculate_conversion()
            
            elif event.key == pygame.K_c:
                self.clear_input()
            
            elif event.key == pygame.K_s:
                self.swap_units()
            
            # Number input (direct key handling)
            elif event.key >= pygame.K_0 and event.key <= pygame.K_9:
                if self.selected_field == "value":
                    number = str(event.key - pygame.K_0)
                    self.handle_number_input(number)
            
            elif event.key == pygame.K_PERIOD:
                if self.selected_field == "value":
                    self.handle_decimal_input()
            
            # Alternative number input with character
            else:
                char = event.unicode
                if char.isdigit() and self.selected_field == "value":
                    self.handle_number_input(char)
                elif char == "." and self.selected_field == "value":
                    self.handle_decimal_input()
        
        return None
    
    def handle_navigation(self, direction):
        """Handle navigation based on current field"""
        if self.selected_field == "category":
            categories = list(self.categories.keys())
            current_index = categories.index(self.current_category)
            new_index = (current_index + direction) % len(categories)
            self.current_category = categories[new_index]
            self.from_unit_index = 0
            self.to_unit_index = 1
            self.calculate_conversion()
        
        elif self.selected_field == "from_unit":
            units = self.categories[self.current_category]["units"]
            self.from_unit_index = (self.from_unit_index + direction) % len(units)
            self.calculate_conversion()
        
        elif self.selected_field == "to_unit":
            units = self.categories[self.current_category]["units"]
            self.to_unit_index = (self.to_unit_index + direction) % len(units)
            self.calculate_conversion()
        
        elif self.selected_field == "value":
            # Navigate between fields
            self.field_index = (self.field_index + direction) % len(self.field_order)
            self.selected_field = self.field_order[self.field_index]
    
    def handle_number_input(self, number):
        """Handle number input"""
        if self.input_value == "0":
            self.input_value = number
        else:
            if len(self.input_value) < 10:  # Limit input length
                self.input_value += number
        
        self.calculate_conversion()
    
    def handle_decimal_input(self):
        """Handle decimal point input"""
        if not self.decimal_entered:
            if not self.input_value:
                self.input_value = "0."
            else:
                self.input_value += "."
            self.decimal_entered = True
            self.calculate_conversion()
    
    def clear_input(self):
        """Clear input value"""
        self.input_value = "0"
        self.decimal_entered = False
        self.calculate_conversion()
    
    def swap_units(self):
        """Swap from and to units"""
        self.from_unit_index, self.to_unit_index = self.to_unit_index, self.from_unit_index
        self.calculate_conversion()
    
    def calculate_conversion(self):
        """Calculate conversion result"""
        try:
            value = float(self.input_value) if self.input_value else 0
            
            if value == 0:
                self.result_value = "0"
                return
            
            category = self.categories[self.current_category]
            units = category["units"]
            from_unit = units[self.from_unit_index]
            to_unit = units[self.to_unit_index]
            
            # Special handling for temperature
            if self.current_category == "Temperature":
                result = self.convert_temperature(value, from_unit, to_unit)
            else:
                # Standard unit conversion
                conversions = category["conversions"]
                # Convert to base unit first, then to target unit
                base_value = value * conversions[from_unit]
                result = base_value / conversions[to_unit]
            
            # Format result
            if abs(result) >= 1000000:
                self.result_value = f"{result:.2e}"
            elif abs(result) >= 1:
                self.result_value = f"{result:.6f}".rstrip('0').rstrip('.')
            else:
                self.result_value = f"{result:.8f}".rstrip('0').rstrip('.')
            
        except (ValueError, ZeroDivisionError):
            self.result_value = "Error"
    
    def convert_temperature(self, value, from_unit, to_unit):
        """Convert temperature units"""
        # Convert to Celsius first
        if from_unit == "°C":
            celsius = value
        elif from_unit == "°F":
            celsius = (value - 32) * 5/9
        elif from_unit == "K":
            celsius = value - 273.15
        
        # Convert from Celsius to target unit
        if to_unit == "°C":
            return celsius
        elif to_unit == "°F":
            return celsius * 9/5 + 32
        elif to_unit == "K":
            return celsius + 273.15
        
        return celsius
    
    def update(self):
        """Update converter state"""
        # Update text cursor
        self.text_cursor_timer += 1
        if self.text_cursor_timer >= 30:
            self.text_cursor_visible = not self.text_cursor_visible
            self.text_cursor_timer = 0
    
    def draw(self, screen):
        """Draw converter interface"""
        # Header
        header_text = f"Unit Converter - {self.current_category}"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Category selector
        category_y = 30
        category_label = "Category:"
        category_surface = self.os.font_m.render(category_label, True, TEXT_COLOR)
        screen.blit(category_surface, (10, category_y))
        
        category_rect = pygame.Rect(80, category_y, SCREEN_WIDTH - 90, 20)
        category_color = SELECTED_COLOR if self.selected_field == "category" else BUTTON_COLOR
        pygame.draw.rect(screen, category_color, category_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, category_rect, 2)
        
        category_text_surface = self.os.font_m.render(self.current_category, True, TEXT_COLOR)
        screen.blit(category_text_surface, (85, category_y + 2))
        
        # Input value
        value_y = 60
        value_label = "Value:"
        value_surface = self.os.font_m.render(value_label, True, TEXT_COLOR)
        screen.blit(value_surface, (10, value_y))
        
        value_rect = pygame.Rect(70, value_y, SCREEN_WIDTH - 80, 25)
        value_color = SELECTED_COLOR if self.selected_field == "value" else BUTTON_COLOR
        pygame.draw.rect(screen, value_color, value_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, value_rect, 2)
        
        value_text = self.input_value
        if self.selected_field == "value" and self.text_cursor_visible:
            value_text += "|"
        
        value_text_surface = self.os.font_l.render(value_text, True, TEXT_COLOR)
        screen.blit(value_text_surface, (75, value_y + 2))
        
        # From unit
        from_y = 95
        from_label = "From:"
        from_surface = self.os.font_m.render(from_label, True, TEXT_COLOR)
        screen.blit(from_surface, (10, from_y))
        
        from_rect = pygame.Rect(60, from_y, (SCREEN_WIDTH - 70) // 2, 25)
        from_color = SELECTED_COLOR if self.selected_field == "from_unit" else BUTTON_COLOR
        pygame.draw.rect(screen, from_color, from_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, from_rect, 2)
        
        units = self.categories[self.current_category]["units"]
        from_unit_text = units[self.from_unit_index]
        from_unit_surface = self.os.font_m.render(from_unit_text, True, TEXT_COLOR)
        from_unit_x = from_rect.centerx - from_unit_surface.get_width() // 2
        screen.blit(from_unit_surface, (from_unit_x, from_y + 4))
        
        # To unit
        to_rect = pygame.Rect(SCREEN_WIDTH // 2 + 5, from_y, (SCREEN_WIDTH - 70) // 2, 25)
        to_color = SELECTED_COLOR if self.selected_field == "to_unit" else BUTTON_COLOR
        pygame.draw.rect(screen, to_color, to_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, to_rect, 2)
        
        to_label = "To:"
        to_surface = self.os.font_m.render(to_label, True, TEXT_COLOR)
        screen.blit(to_surface, (SCREEN_WIDTH // 2 - 25, from_y))
        
        to_unit_text = units[self.to_unit_index]
        to_unit_surface = self.os.font_m.render(to_unit_text, True, TEXT_COLOR)
        to_unit_x = to_rect.centerx - to_unit_surface.get_width() // 2
        screen.blit(to_unit_surface, (to_unit_x, from_y + 4))
        
        # Conversion arrow
        arrow_y = from_y + 35
        arrow_surface = self.os.font_l.render("↓", True, ACCENT_COLOR)
        arrow_x = SCREEN_WIDTH // 2 - arrow_surface.get_width() // 2
        screen.blit(arrow_surface, (arrow_x, arrow_y))
        
        # Result
        result_y = arrow_y + 30
        result_label = "Result:"
        result_surface = self.os.font_m.render(result_label, True, TEXT_COLOR)
        screen.blit(result_surface, (10, result_y))
        
        result_rect = pygame.Rect(70, result_y, SCREEN_WIDTH - 80, 25)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, result_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, result_rect, 2)
        
        result_text_surface = self.os.font_l.render(self.result_value, True, TEXT_COLOR)
        screen.blit(result_text_surface, (75, result_y + 2))
        
        # Unit reference
        ref_y = result_y + 35
        ref_label = f"Available {self.current_category.lower()} units:"
        ref_surface = self.os.font_s.render(ref_label, True, HIGHLIGHT_COLOR)
        screen.blit(ref_surface, (10, ref_y))
        
        # Display available units
        unit_text = ", ".join(units)
        if len(unit_text) > 50:
            unit_text = unit_text[:50] + "..."
        
        unit_surface = self.os.font_s.render(unit_text, True, TEXT_COLOR)
        screen.blit(unit_surface, (10, ref_y + 15))
        
        # Controls
        controls = [
            "Tab: Next field",
            "↑↓: Navigate/Change",
            "0-9: Enter numbers",
            ".: Decimal point",
            "C: Clear",
            "S: Swap units"
        ]
        
        control_y = SCREEN_HEIGHT - 45
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 3) * 125
            control_y_pos = control_y + (i // 3) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
        
        # Field indicator
        field_indicator = f"Current field: {self.selected_field.replace('_', ' ').title()}"
        indicator_surface = self.os.font_tiny.render(field_indicator, True, WARNING_COLOR)
        indicator_x = SCREEN_WIDTH // 2 - indicator_surface.get_width() // 2
        screen.blit(indicator_surface, (indicator_x, SCREEN_HEIGHT - 15))
    
    def save_data(self):
        """Save converter data"""
        return {
            "current_category": self.current_category,
            "from_unit_index": self.from_unit_index,
            "to_unit_index": self.to_unit_index
        }
    
    def load_data(self, data):
        """Load converter data"""
        self.current_category = data.get("current_category", "Length")
        self.from_unit_index = data.get("from_unit_index", 0)
        self.to_unit_index = data.get("to_unit_index", 1)
        self.calculate_conversion()
