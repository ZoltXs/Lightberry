
"""
Enhanced Weather Module with Beautiful Animations for LightBerry OS
"""

import pygame
import subprocess
import json
import os
import math
import random
from datetime import datetime, timedelta
from config.constants import *

class Weather:
    def __init__(self, os_instance):
        self.os = os_instance
        self.init_weather()
    
    def init_weather(self):
        """Initialize weather state"""
        self.location = "Madrid"  # Single focused city
        self.weather_data = {}
        self.mode = "view"
        self.last_update = datetime.now()
        self.update_interval = 1800  # 30 minutes
        
        # Animation system
        self.animation_time = 0
        self.particles = []
        self.lightning_flash = 0
        self.lightning_timer = 0
        
        # Weather conditions for testing
        self.current_condition = "sunny"  # Will be dynamic
        self.current_temp = 25
        self.feels_like = 27
        self.humidity = 60
        self.wind_speed = 12
        self.uv_index = 7
        
        # Load proper fonts for emoji support
        self.load_fonts()
        
        # Initialize particles based on weather
        self.init_particles()
        
        # Simple weather icons that work on all systems
        self.weather_icons = {
            "clear": "☀", "sunny": "☀", "partly_cloudy": "⛅", "cloudy": "☁",
            "overcast": "☁", "rain": "🌧", "drizzle": "🌦", "showers": "🌦", 
            "thunderstorm": "⛈", "storm": "⛈", "snow": "🌨", "sleet": "🌨",
            "fog": "🌫", "mist": "🌫", "wind": "💨", "hot": "🌡", "cold": "❄",
            "night_clear": "🌙", "night_cloudy": "🌙", "default": "🌥"
        }
        
        # Enhanced color gradients for each weather condition
        self.weather_gradients = {
            "sunny": [(255, 215, 0), (255, 165, 0), (255, 140, 0)],
            "clear": [(135, 206, 250), (173, 216, 230), (240, 248, 255)],
            "partly_cloudy": [(169, 169, 169), (192, 192, 192), (220, 220, 220)],
            "cloudy": [(128, 128, 128), (169, 169, 169), (192, 192, 192)],
            "rain": [(70, 130, 180), (100, 149, 237), (135, 206, 235)],
            "thunderstorm": [(25, 25, 112), (75, 0, 130), (138, 43, 226)],
            "snow": [(248, 248, 255), (230, 230, 250), (255, 250, 250)],
            "fog": [(128, 128, 128), (169, 169, 169), (192, 192, 192)],
            "night": [(25, 25, 112), (72, 61, 139), (123, 104, 238)]
        }
    
    def load_fonts(self):
        """Load fonts with emoji support"""
        try:
            # Try to use system fonts with emoji support
            self.emoji_font = pygame.font.SysFont('dejavusans', 48)
            if not self.emoji_font:
                self.emoji_font = pygame.font.SysFont('symbola', 48)
            if not self.emoji_font:
                self.emoji_font = pygame.font.Font(None, 48)
        except:
            self.emoji_font = pygame.font.Font(None, 48)
        
        # Test emoji rendering
        try:
            test_surface = self.emoji_font.render("☀", True, (255, 255, 255))
            print("✓ Emoji font loaded successfully")
        except:
            print("✗ Emoji font loading failed, using fallback")
    
    def init_particles(self):
        """Initialize particles based on current weather"""
        self.particles = []
        
        if self.current_condition in ["rain", "drizzle", "showers"]:
            # Rain particles
            for _ in range(80):
                self.particles.append({
                    'type': 'rain',
                    'x': random.randint(0, SCREEN_WIDTH),
                    'y': random.randint(-SCREEN_HEIGHT, 0),
                    'speed': random.uniform(3, 7),
                    'length': random.randint(8, 15)
                })
        
        elif self.current_condition in ["snow", "sleet"]:
            # Snow particles
            for _ in range(60):
                self.particles.append({
                    'type': 'snow',
                    'x': random.randint(0, SCREEN_WIDTH),
                    'y': random.randint(-SCREEN_HEIGHT, 0),
                    'speed': random.uniform(1, 3),
                    'size': random.randint(2, 4),
                    'drift': random.uniform(-0.5, 0.5)
                })
        
        elif self.is_night() and self.current_condition in ["clear", "partly_cloudy"]:
            # Stars for night
            for _ in range(25):
                self.particles.append({
                    'type': 'star',
                    'x': random.randint(0, SCREEN_WIDTH),
                    'y': random.randint(0, SCREEN_HEIGHT // 2),
                    'brightness': random.uniform(0.3, 1.0),
                    'twinkle_speed': random.uniform(0.02, 0.05)
                })
    
    def is_night(self):
        """Check if it's night time"""
        hour = datetime.now().hour
        return hour < 6 or hour > 18
    
    def update_particles(self):
        """Update particle animations"""
        for particle in self.particles:
            if particle['type'] == 'rain':
                particle['y'] += particle['speed']
                if particle['y'] > SCREEN_HEIGHT:
                    particle['y'] = random.randint(-50, 0)
                    particle['x'] = random.randint(0, SCREEN_WIDTH)
            
            elif particle['type'] == 'snow':
                particle['y'] += particle['speed']
                particle['x'] += particle['drift']
                if particle['y'] > SCREEN_HEIGHT:
                    particle['y'] = random.randint(-50, 0)
                    particle['x'] = random.randint(0, SCREEN_WIDTH)
                if particle['x'] < 0 or particle['x'] > SCREEN_WIDTH:
                    particle['x'] = random.randint(0, SCREEN_WIDTH)
            
            elif particle['type'] == 'star':
                particle['brightness'] += particle['twinkle_speed']
                if particle['brightness'] > 1.0 or particle['brightness'] < 0.3:
                    particle['twinkle_speed'] *= -1
    
    def update_lightning(self):
        """Update lightning effect"""
        if self.current_condition == "thunderstorm":
            self.lightning_timer += 1
            if self.lightning_timer > 180:  # Every 3 seconds
                if random.randint(0, 5) == 0:
                    self.lightning_flash = 30
                self.lightning_timer = 0
            
            if self.lightning_flash > 0:
                self.lightning_flash -= 1
    
    def draw_gradient_background(self, screen, condition):
        """Draw beautiful gradient background"""
        colors = self.weather_gradients.get(condition, self.weather_gradients["clear"])
        
        # Create gradient effect
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            if ratio < 0.5:
                # Top half gradient
                blend_ratio = ratio * 2
                r = int(colors[0][0] * (1 - blend_ratio) + colors[1][0] * blend_ratio)
                g = int(colors[0][1] * (1 - blend_ratio) + colors[1][1] * blend_ratio)
                b = int(colors[0][2] * (1 - blend_ratio) + colors[1][2] * blend_ratio)
            else:
                # Bottom half gradient
                blend_ratio = (ratio - 0.5) * 2
                r = int(colors[1][0] * (1 - blend_ratio) + colors[2][0] * blend_ratio)
                g = int(colors[1][1] * (1 - blend_ratio) + colors[2][1] * blend_ratio)
                b = int(colors[1][2] * (1 - blend_ratio) + colors[2][2] * blend_ratio)
            
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    def draw_particles(self, screen):
        """Draw weather particles"""
        for particle in self.particles:
            if particle['type'] == 'rain':
                color = (173, 216, 230)  # Light blue
                start_pos = (int(particle['x']), int(particle['y']))
                end_pos = (int(particle['x']), int(particle['y'] + particle['length']))
                pygame.draw.line(screen, color, start_pos, end_pos, 2)
            
            elif particle['type'] == 'snow':
                color = (255, 255, 255)
                pygame.draw.circle(screen, color, 
                                 (int(particle['x']), int(particle['y'])), 
                                 particle['size'])
            
            elif particle['type'] == 'star':
                brightness = int(255 * particle['brightness'])
                color = (brightness, brightness, brightness)
                pygame.draw.circle(screen, color, 
                                 (int(particle['x']), int(particle['y'])), 2)
    
    def draw_sun(self, screen):
        """Draw animated sun"""
        if self.current_condition in ["sunny", "clear"] and not self.is_night():
            sun_x = SCREEN_WIDTH - 80
            sun_y = 60
            
            # Sun rays
            for i in range(8):
                angle = (i * 45 + self.animation_time * 2) % 360
                ray_x = sun_x + math.cos(math.radians(angle)) * 45
                ray_y = sun_y + math.sin(math.radians(angle)) * 45
                ray_end_x = sun_x + math.cos(math.radians(angle)) * 55
                ray_end_y = sun_y + math.sin(math.radians(angle)) * 55
                pygame.draw.line(screen, (255, 215, 0), (ray_x, ray_y), (ray_end_x, ray_end_y), 3)
            
            # Sun circle
            pygame.draw.circle(screen, (255, 215, 0), (sun_x, sun_y), 25)
            pygame.draw.circle(screen, (255, 255, 0), (sun_x, sun_y), 20)
    
    def draw_moon(self, screen):
        """Draw moon for night time"""
        if self.is_night() and self.current_condition in ["clear", "partly_cloudy"]:
            moon_x = SCREEN_WIDTH - 80
            moon_y = 60
            
            # Moon
            pygame.draw.circle(screen, (245, 245, 220), (moon_x, moon_y), 20)
            pygame.draw.circle(screen, (220, 220, 180), (moon_x - 5, moon_y - 5), 15)
    
    def draw_lightning(self, screen):
        """Draw lightning effect"""
        if self.lightning_flash > 0:
            # Flash effect
            flash_alpha = int((self.lightning_flash / 30) * 100)
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.set_alpha(flash_alpha)
            flash_surface.fill((255, 255, 255))
            screen.blit(flash_surface, (0, 0))
            
            # Lightning bolt
            if self.lightning_flash > 20:
                bolt_x = random.randint(50, SCREEN_WIDTH - 50)
                points = [
                    (bolt_x, 0),
                    (bolt_x - 10, 40),
                    (bolt_x + 5, 80),
                    (bolt_x - 8, 120),
                    (bolt_x + 3, 160)
                ]
                pygame.draw.lines(screen, (255, 255, 100), False, points, 4)
    
    def draw_weather_info(self, screen):
        """Draw main weather information"""
        # Location
        location_surface = self.os.font_xl.render(self.location, True, (255, 255, 255))
        location_x = SCREEN_WIDTH // 2 - location_surface.get_width() // 2
        screen.blit(location_surface, (location_x, 20))
        
        # Weather icon and condition
        condition = self.current_condition
        if self.is_night() and condition in ["clear", "partly_cloudy"]:
            condition = f"night_{condition}"
        
        # Try to render emoji icon with fallback
        icon = self.weather_icons.get(condition, self.weather_icons["default"])
        try:
            icon_surface = self.emoji_font.render(icon, True, (255, 255, 255))
        except:
            # Fallback to text representation
            icon_surface = self.os.font_xl.render(condition.upper(), True, (255, 255, 255))
        
        icon_x = SCREEN_WIDTH // 2 - icon_surface.get_width() // 2
        screen.blit(icon_surface, (icon_x, 60))
        
        # Temperature
        temp_text = f"{self.current_temp}°"
        temp_surface = self.os.font_xl.render(temp_text, True, (255, 255, 255))
        temp_x = SCREEN_WIDTH // 2 - temp_surface.get_width() // 2
        screen.blit(temp_surface, (temp_x, 110))
        
        # Condition description
        desc_text = condition.replace("_", " ").title()
        desc_surface = self.os.font_l.render(desc_text, True, (220, 220, 220))
        desc_x = SCREEN_WIDTH // 2 - desc_surface.get_width() // 2
        screen.blit(desc_surface, (desc_x, 160))
        
        # Additional info
        info_y = 190
        info_items = [
            f"Feels like {self.feels_like}°",
            f"Humidity {self.humidity}%",
            f"Wind {self.wind_speed} km/h",
            f"UV Index {self.uv_index}"
        ]
        
        for i, info in enumerate(info_items):
            info_surface = self.os.font_s.render(info, True, (200, 200, 200))
            info_x = 20 + (i % 2) * 180
            info_y_pos = info_y + (i // 2) * 20
            screen.blit(info_surface, (info_x, info_y_pos))
    
    def handle_events(self, event):
        """Handle weather events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            elif event.key == pygame.K_r:
                # Test rain
                self.current_condition = "rain"
                self.init_particles()
                print("✓ Switched to rain mode")
            elif event.key == pygame.K_s:
                # Test snow
                self.current_condition = "snow"
                self.init_particles()
                print("✓ Switched to snow mode")
            elif event.key == pygame.K_t:
                # Test thunderstorm
                self.current_condition = "thunderstorm"
                self.init_particles()
                print("✓ Switched to thunderstorm mode")
            elif event.key == pygame.K_c:
                # Test clear
                self.current_condition = "clear"
                self.init_particles()
                print("✓ Switched to clear mode")
        
        return None
    
    def update(self):
        """Update weather animations"""
        self.animation_time += 1
        self.update_particles()
        self.update_lightning()
    
    def draw(self, screen):
        """Draw weather interface with animations"""
        # Draw gradient background
        condition = "night" if self.is_night() else self.current_condition
        self.draw_gradient_background(screen, condition)
        
        # Draw lightning effect
        self.draw_lightning(screen)
        
        # Draw particles (rain, snow, etc.)
        self.draw_particles(screen)
        
        # Draw sun or moon
        self.draw_sun(screen)
        self.draw_moon(screen)
        
        # Draw weather information
        self.draw_weather_info(screen)
        
        # Controls hint
        controls_text = "R:Rain S:Snow T:Thunder C:Clear ESC:Back"
        controls_surface = self.os.font_tiny.render(controls_text, True, (150, 150, 150))
        screen.blit(controls_surface, (10, SCREEN_HEIGHT - 15))
    
    def save_data(self):
        """Save weather data"""
        return {
            "location": self.location,
            "weather_data": self.weather_data
        }
    
    def load_data(self, data):
        """Load weather data"""
        self.location = data.get("location", "Madrid")
        self.weather_data = data.get("weather_data", {})
