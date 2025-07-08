"""
Enhanced Weather Module for LightBerry OS
Professional weather display with real API integration and scrolling
"""

import pygame
import requests
import json
import os
from datetime import datetime, timedelta
from config.constants import *

class Weather:
    def __init__(self, os_instance):
        self.os = os_instance
        self.init_weather()
    
    def init_weather(self):
        """Initialize weather state"""
        self.locations = ["Madrid", "New York", "Tokyo"]
        self.weather_data = {}
        self.mode = "view"
        self.selected_location = 0
        self.scroll_offset = 0
        self.location_input = ""
        self.unit = "celsius"
        self.last_update = {}
        self.update_interval = 1800  # 30 minutes
        
        # Weather icons
        self.weather_icons = {
            "clear": "☀", "sunny": "☀", "partly_cloudy": "⛅", "cloudy": "☁",
            "overcast": "☁", "rain": "🌧", "drizzle": "🌦", "showers": "🌦", 
            "thunderstorm": "⛈", "storm": "⛈", "snow": "🌨", "sleet": "🌨",
            "fog": "🌫", "mist": "🌫", "wind": "💨", "hot": "🌡", "cold": "❄",
            "default": "🌤"
        }
        
        # Weather condition colors
        self.weather_colors = {
            "clear": SUNNY_COLOR, "sunny": SUNNY_COLOR, "partly_cloudy": CLOUDY_COLOR,
            "cloudy": CLOUDY_COLOR, "overcast": CLOUDY_COLOR, "rain": RAINY_COLOR,
            "drizzle": RAINY_COLOR, "showers": RAINY_COLOR, "thunderstorm": THUNDERSTORM_COLOR,
            "storm": THUNDERSTORM_COLOR, "snow": SNOWY_COLOR, "sleet": SNOWY_COLOR,
            "fog": FOGGY_COLOR, "mist": FOGGY_COLOR, "wind": CLOUDY_COLOR,
            "hot": TEMP_HOT_COLOR, "cold": TEMP_COLD_COLOR, "default": HIGHLIGHT_COLOR
        }
        
        # API configuration
        self.api_key = os.getenv("WEATHER_API_KEY", "demo_key")
        self.api_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # Text input
        self.text_cursor_visible = True
        self.text_cursor_timer = 0
        
        # Initialize with sample data if no API key
        if self.api_key == "demo_key":
            self.generate_sample_data()
        else:
            self.fetch_all_weather_data()
    
    def generate_sample_data(self):
        """Generate sample weather data for demonstration"""
        sample_data = {
            "Madrid": {
                "temperature": 22,
                "condition": "sunny",
                "humidity": 45,
                "wind_speed": 12,
                "pressure": 1013,
                "visibility": 10,
                "feels_like": 24,
                "description": "Clear skies",
                "last_updated": datetime.now().isoformat()
            },
            "New York": {
                "temperature": 18,
                "condition": "cloudy",
                "humidity": 60,
                "wind_speed": 8,
                "pressure": 1015,
                "visibility": 8,
                "feels_like": 16,
                "description": "Overcast",
                "last_updated": datetime.now().isoformat()
            },
            "Tokyo": {
                "temperature": 25,
                "condition": "partly_cloudy",
                "humidity": 55,
                "wind_speed": 6,
                "pressure": 1011,
                "visibility": 12,
                "feels_like": 27,
                "description": "Partly cloudy",
                "last_updated": datetime.now().isoformat()
            }
        }
        self.weather_data = sample_data
    
    def fetch_weather_data(self, location):
        """Fetch weather data for a specific location"""
        if self.api_key == "demo_key":
            return  # Use sample data
        
        try:
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(self.api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant data
                weather_info = {
                    "temperature": int(data["main"]["temp"]),
                    "condition": data["weather"][0]["main"].lower(),
                    "humidity": data["main"]["humidity"],
                    "wind_speed": int(data["wind"]["speed"] * 3.6),  # Convert to km/h
                    "pressure": data["main"]["pressure"],
                    "visibility": data.get("visibility", 0) // 1000,  # Convert to km
                    "feels_like": int(data["main"]["feels_like"]),
                    "description": data["weather"][0]["description"].title(),
                    "last_updated": datetime.now().isoformat()
                }
                
                self.weather_data[location] = weather_info
                self.last_update[location] = datetime.now()
                
        except Exception as e:
            print(f"Error fetching weather data for {location}: {e}")
    
    def fetch_all_weather_data(self):
        """Fetch weather data for all locations"""
        for location in self.locations:
            self.fetch_weather_data(location)
    
    def should_update_weather(self, location):
        """Check if weather data should be updated"""
        if location not in self.last_update:
            return True
        
        time_since_update = datetime.now() - self.last_update[location]
        return time_since_update.total_seconds() > self.update_interval
    
    def update_weather_data(self):
        """Update weather data if needed"""
        for location in self.locations:
            if self.should_update_weather(location):
                self.fetch_weather_data(location)
    
    def get_temperature_color(self, temperature):
        """Get color based on temperature"""
        if temperature >= 30:
            return TEMP_HOT_COLOR
        elif temperature >= 20:
            return TEMP_WARM_COLOR
        elif temperature >= 10:
            return TEMP_MILD_COLOR
        elif temperature >= 0:
            return TEMP_COOL_COLOR
        else:
            return TEMP_COLD_COLOR
    
    def handle_events(self, event):
        """Handle weather events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.mode == "add":
                    self.mode = "view"
                    self.location_input = ""
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
            self.selected_location = max(0, self.selected_location - 1)
            self.scroll_offset = 0
        
        elif event.key == pygame.K_DOWN:
            self.selected_location = min(len(self.locations) - 1, self.selected_location + 1)
            self.scroll_offset = 0
        
        elif event.key == pygame.K_RETURN:
            # Show detailed view with scrolling
            self.scroll_offset = 0
        
        elif event.key == pygame.K_a:
            self.mode = "add"
            self.location_input = ""
        
        elif event.key == pygame.K_d:
            if len(self.locations) > 1:
                location = self.locations[self.selected_location]
                self.locations.remove(location)
                if location in self.weather_data:
                    del self.weather_data[location]
                self.selected_location = min(self.selected_location, len(self.locations) - 1)
        
        elif event.key == pygame.K_r:
            # Refresh weather data
            self.fetch_all_weather_data()
        
        elif event.key == pygame.K_u:
            # Toggle temperature units
            self.unit = "fahrenheit" if self.unit == "celsius" else "celsius"
        
        elif event.key == pygame.K_s:
            # Scroll through detailed weather info
            if self.locations:
                location = self.locations[self.selected_location]
                if location in self.weather_data:
                    self.scroll_offset = (self.scroll_offset + 1) % 3
    
    def handle_add_events(self, event):
        """Handle add mode events"""
        if event.key == pygame.K_RETURN:
            if self.location_input.strip():
                location = self.location_input.strip().title()
                if location not in self.locations:
                    self.locations.append(location)
                    self.fetch_weather_data(location)
                self.mode = "view"
                self.location_input = ""
        
        elif event.key == pygame.K_BACKSPACE:
            self.location_input = self.location_input[:-1]
        
        else:
            char = event.unicode
            if char.isprintable() and len(self.location_input) < 20:
                self.location_input += char
    
    def convert_temperature(self, celsius):
        """Convert temperature based on unit setting"""
        if self.unit == "fahrenheit":
            return int(celsius * 9/5 + 32)
        return celsius
    
    def get_unit_symbol(self):
        """Get temperature unit symbol"""
        return "°F" if self.unit == "fahrenheit" else "°C"
    
    def update(self):
        """Update weather state"""
        # Update text cursor
        self.text_cursor_timer += 1
        if self.text_cursor_timer >= 30:
            self.text_cursor_visible = not self.text_cursor_visible
            self.text_cursor_timer = 0
    
    def draw(self, screen):
        """Draw weather interface"""
        if self.mode == "add":
            self.draw_add_mode(screen)
        else:
            self.draw_view_mode(screen)
    
    def draw_view_mode(self, screen):
        """Draw view mode"""
        # Header
        header_text = f"Weather ({self.unit.title()})"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        if not self.locations:
            no_locations_text = "No locations added"
            no_locations_surface = self.os.font_m.render(no_locations_text, True, ERROR_COLOR)
            no_locations_x = SCREEN_WIDTH // 2 - no_locations_surface.get_width() // 2
            screen.blit(no_locations_surface, (no_locations_x, 60))
        else:
            # Current location highlight
            if self.selected_location < len(self.locations):
                location = self.locations[self.selected_location]
                
                # Location selector
                location_y = 30
                for i, loc in enumerate(self.locations):
                    loc_x = 10 + i * ((SCREEN_WIDTH - 20) // len(self.locations))
                    loc_width = (SCREEN_WIDTH - 20) // len(self.locations)
                    
                    if i == self.selected_location:
                        loc_rect = pygame.Rect(loc_x, location_y, loc_width - 5, 20)
                        pygame.draw.rect(screen, SELECTED_COLOR, loc_rect)
                        pygame.draw.rect(screen, ACCENT_COLOR, loc_rect, 2)
                    
                    loc_text = loc if len(loc) <= 8 else loc[:8] + "..."
                    loc_surface = self.os.font_m.render(loc_text, True, TEXT_COLOR)
                    screen.blit(loc_surface, (loc_x + 5, location_y + 2))
                
                # Weather display
                if location in self.weather_data:
                    weather = self.weather_data[location]
                    
                    # Main weather info
                    main_y = 55
                    
                    # Weather icon and condition
                    condition = weather.get("condition", "default")
                    icon = self.weather_icons.get(condition, self.weather_icons["default"])
                    condition_color = self.weather_colors.get(condition, self.weather_colors["default"])
                    
                    # Large weather icon
                    icon_surface = self.os.font_xl.render(icon, True, condition_color)
                    icon_x = 20
                    screen.blit(icon_surface, (icon_x, main_y))
                    
                    # Temperature
                    temp = self.convert_temperature(weather["temperature"])
                    temp_text = f"{temp}{self.get_unit_symbol()}"
                    temp_surface = self.os.font_xl.render(temp_text, True, 
                                                        self.get_temperature_color(weather["temperature"]))
                    temp_x = 80
                    screen.blit(temp_surface, (temp_x, main_y))
                    
                    # Feels like
                    feels_like = self.convert_temperature(weather["feels_like"])
                    feels_text = f"Feels like {feels_like}{self.get_unit_symbol()}"
                    feels_surface = self.os.font_s.render(feels_text, True, HIGHLIGHT_COLOR)
                    screen.blit(feels_surface, (temp_x, main_y + 35))
                    
                    # Description
                    desc_surface = self.os.font_m.render(weather["description"], True, TEXT_COLOR)
                    screen.blit(desc_surface, (20, main_y + 55))
                    
                    # Detailed info (scrollable)
                    detail_y = main_y + 80
                    
                    details = [
                        ("Humidity", f"{weather['humidity']}%"),
                        ("Wind", f"{weather['wind_speed']} km/h"),
                        ("Pressure", f"{weather['pressure']} hPa"),
                        ("Visibility", f"{weather['visibility']} km"),
                        ("Updated", datetime.fromisoformat(weather['last_updated']).strftime("%H:%M"))
                    ]
                    
                    # Show details based on scroll offset
                    visible_details = details[self.scroll_offset:self.scroll_offset + 3]
                    
                    for i, (label, value) in enumerate(visible_details):
                        detail_text = f"{label}: {value}"
                        detail_surface = self.os.font_m.render(detail_text, True, TEXT_COLOR)
                        screen.blit(detail_surface, (20, detail_y + i * 18))
                    
                    # Scroll indicators
                    if self.scroll_offset > 0:
                        up_text = "↑ More info"
                        up_surface = self.os.font_tiny.render(up_text, True, HIGHLIGHT_COLOR)
                        screen.blit(up_surface, (SCREEN_WIDTH - 80, detail_y - 10))
                    
                    if self.scroll_offset + 3 < len(details):
                        down_text = "↓ More info"
                        down_surface = self.os.font_tiny.render(down_text, True, HIGHLIGHT_COLOR)
                        screen.blit(down_surface, (SCREEN_WIDTH - 80, detail_y + 50))
                
                else:
                    # No data available
                    no_data_text = "Loading weather data..."
                    no_data_surface = self.os.font_m.render(no_data_text, True, WARNING_COLOR)
                    no_data_x = SCREEN_WIDTH // 2 - no_data_surface.get_width() // 2
                    screen.blit(no_data_surface, (no_data_x, 80))
        
        # Controls
        controls = [
            "↑↓: Navigate locations",
            "A: Add location",
            "D: Delete location",
            "R: Refresh",
            "U: Toggle units",
            "S: Scroll details"
        ]
        
        control_y = SCREEN_HEIGHT - 50
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 3) * 125
            control_y_pos = control_y + (i // 3) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def draw_add_mode(self, screen):
        """Draw add mode"""
        # Header
        header_text = "Add Weather Location"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Input label
        input_label = "Enter city name:"
        input_surface = self.os.font_m.render(input_label, True, TEXT_COLOR)
        screen.blit(input_surface, (10, 40))
        
        # Input field
        input_rect = pygame.Rect(10, 60, SCREEN_WIDTH - 20, 30)
        pygame.draw.rect(screen, BUTTON_COLOR, input_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, input_rect, 2)
        
        input_text = self.location_input
        if self.text_cursor_visible:
            input_text += "|"
        
        input_text_surface = self.os.font_m.render(input_text, True, TEXT_COLOR)
        screen.blit(input_text_surface, (15, 65))
        
        # Instructions
        instructions = [
            "Enter the name of a city to add weather information.",
            "Examples: London, Paris, Tokyo, New York",
            "Press Enter to add, ESC to cancel."
        ]
        
        instruction_y = 110
        for instruction in instructions:
            instruction_surface = self.os.font_s.render(instruction, True, HIGHLIGHT_COLOR)
            instruction_x = SCREEN_WIDTH // 2 - instruction_surface.get_width() // 2
            screen.blit(instruction_surface, (instruction_x, instruction_y))
            instruction_y += 20
        
        # Current locations
        if self.locations:
            current_label = "Current locations:"
            current_surface = self.os.font_m.render(current_label, True, TEXT_COLOR)
            screen.blit(current_surface, (10, 170))
            
            locations_text = ", ".join(self.locations)
            if len(locations_text) > 45:
                locations_text = locations_text[:45] + "..."
            
            locations_surface = self.os.font_s.render(locations_text, True, HIGHLIGHT_COLOR)
            screen.blit(locations_surface, (10, 190))
        
        # Controls
        controls = [
            "Type: Enter city name",
            "Enter: Add location",
            "ESC: Cancel"
        ]
        
        control_y = SCREEN_HEIGHT - 35
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 2) * 180
            control_y_pos = control_y + (i // 2) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def save_data(self):
        """Save weather data"""
        return {
            "locations": self.locations,
            "unit": self.unit,
            "weather_data": self.weather_data
        }
    
    def load_data(self, data):
        """Load weather data"""
        self.locations = data.get("locations", self.locations)
        self.unit = data.get("unit", self.unit)
        
        # Don't load old weather data, fetch fresh data
        self.weather_data = {}
        self.fetch_all_weather_data()
