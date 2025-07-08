"""
Notification system for LightBerry OS
"""

import pygame
import time
from datetime import datetime, timedelta
from config.constants import *

class Notification:
    def __init__(self, title, message, duration=5, notification_type="info"):
        self.title = title
        self.message = message
        self.duration = duration
        self.type = notification_type
        self.created_time = time.time()
        self.alpha = 255
        self.y_offset = 0
        
        # Colors based on type
        self.colors = {
            "info": NOTIFICATION_COLOR,
            "success": SUCCESS_COLOR,
            "warning": WARNING_COLOR,
            "error": ERROR_COLOR,
            "event": CALENDAR_EVENT_COLOR
        }
        
        self.color = self.colors.get(notification_type, NOTIFICATION_COLOR)
    
    def is_expired(self):
        return time.time() - self.created_time > self.duration
    
    def update(self):
        # Fade out animation
        elapsed = time.time() - self.created_time
        if elapsed > self.duration - 1:
            self.alpha = max(0, 255 - int((elapsed - (self.duration - 1)) * 255))
    
    def draw(self, screen, font, y_position):
        if self.alpha <= 0:
            return
        
        # Create notification surface
        notification_height = 50
        notification_width = SCREEN_WIDTH - 20
        
        # Background with alpha
        surf = pygame.Surface((notification_width, notification_height), pygame.SRCALPHA)
        bg_color = (*self.color, min(200, self.alpha))
        pygame.draw.rect(surf, bg_color, (0, 0, notification_width, notification_height))
        pygame.draw.rect(surf, (*TEXT_COLOR, self.alpha), 
                        (0, 0, notification_width, notification_height), 2)
        
        # Title
        title_color = (*TEXT_COLOR, self.alpha)
        title_surface = font.render(self.title, True, title_color)
        surf.blit(title_surface, (10, 5))
        
        # Message
        message_surface = font.render(self.message, True, title_color)
        surf.blit(message_surface, (10, 25))
        
        # Draw to screen
        screen.blit(surf, (10, y_position))

class NotificationManager:
    def __init__(self):
        self.notifications = []
        self.max_notifications = 3
    
    def add_notification(self, title, message, duration=5, notification_type="info"):
        """Add a new notification"""
        notification = Notification(title, message, duration, notification_type)
        self.notifications.append(notification)
        
        # Remove oldest if too many
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
    
    def add_event_notification(self, event_title, event_time):
        """Add a calendar event notification"""
        self.add_notification(
            "Calendar Event",
            f"{event_title} at {event_time}",
            duration=30,  # 30 seconds
            notification_type="event"
        )
    
    def update(self):
        """Update all notifications"""
        # Update existing notifications
        for notification in self.notifications:
            notification.update()
        
        # Remove expired notifications
        self.notifications = [n for n in self.notifications if not n.is_expired()]
    
    def draw(self, screen, font):
        """Draw all notifications"""
        y_position = 10
        for notification in self.notifications:
            notification.draw(screen, font, y_position)
            y_position += 55
    
    def clear_all(self):
        """Clear all notifications"""
        self.notifications = []
    
    def has_notifications(self):
        """Check if there are active notifications"""
        return len(self.notifications) > 0
