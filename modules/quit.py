"""
Enhanced Quit Module for LightBerry OS - Fixed version
Professional system shutdown and restart functionality
"""

import pygame
import subprocess
import sys
import os
from config.constants import *

class Quit:
    def __init__(self, os_instance):
        self.os = os_instance
        self.init_quit()
    
    def init_quit(self):
        """Initialize quit module state"""
        self.options = [
            {
                "name": "Restart",
                "description": "Restart the system",
                "action": "restart",
                "icon": "R",
                "color": WARNING_COLOR
            },
            {
                "name": "Shut Down",
                "description": "Power off the system",
                "action": "shutdown",
                "icon": "S",
                "color": ERROR_COLOR
            },
            {
                "name": "Exit LightBerry OS",
                "description": "Exit to desktop",
                "action": "exit",
                "icon": "E",
                "color": ACCENT_COLOR
            }
        ]
        
        self.selected_option = 0
        self.confirmation_mode = False
        self.selected_action = None
        self.countdown_active = False
        self.countdown_time = 10
        self.countdown_start = 0
        self.show_info = False
        
        # Status messages
        self.status_message = ""
        self.status_color = TEXT_COLOR
        
        # Animation
        self.animation_time = 0
        self.pulse_alpha = 255
    
    def handle_events(self, event):
        """Handle quit module events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.confirmation_mode:
                    self.cancel_action()
                else:
                    return "back"
            elif event.key == pygame.K_i:
                self.show_info = not self.show_info
            elif self.confirmation_mode:
                self.handle_confirmation_events(event)
            else:
                self.handle_main_events(event)
        
        return None
    
    def handle_main_events(self, event):
        """Handle main menu events"""
        if event.key == pygame.K_UP:
            self.selected_option = max(0, self.selected_option - 1)
        elif event.key == pygame.K_DOWN:
            self.selected_option = min(len(self.options) - 1, self.selected_option + 1)
        elif event.key == pygame.K_RETURN:
            self.start_confirmation()
        elif event.key == pygame.K_q:
            # Quick exit
            self.selected_option = 2  # Exit option
            self.start_confirmation()
        elif event.key == pygame.K_r:
            # Quick restart
            self.selected_option = 0  # Restart option
            self.start_confirmation()
        elif event.key == pygame.K_s:
            # Quick shutdown
            self.selected_option = 1  # Shutdown option
            self.start_confirmation()

    def handle_confirmation_events(self, event):
        """Handle confirmation dialog events"""
        if event.key == pygame.K_y:
            self.execute_action()
        elif event.key == pygame.K_n:
            self.cancel_action()
        elif event.key == pygame.K_RETURN:
            self.execute_action()
        elif event.key == pygame.K_c:
            self.cancel_action()

    def start_confirmation(self):
        """Start confirmation dialog"""
        self.confirmation_mode = True
        self.selected_action = self.options[self.selected_option]
        self.countdown_active = True
        self.countdown_time = 10
        self.countdown_start = pygame.time.get_ticks()
        
        self.status_message = f"Confirm {self.selected_action['name'].lower()}?"
        self.status_color = self.selected_action['color']
    
    def cancel_action(self):
        """Cancel current action"""
        self.confirmation_mode = False
        self.selected_action = None
        self.countdown_active = False
        self.countdown_time = 10
        
        self.status_message = "Action cancelled"
        self.status_color = SUCCESS_COLOR

    def execute_action(self):
        """Execute the selected action"""
        if not self.selected_action:
            return
        
        action = self.selected_action['action']
        
        try:
            if action == "restart":
                self.restart_system()
            elif action == "shutdown":
                self.shutdown_system()
            elif action == "exit":
                self.exit_application()
        except Exception as e:
            self.status_message = f"Error: {str(e)[:30]}..."
            self.status_color = ERROR_COLOR
            self.confirmation_mode = False
            self.countdown_active = False

    def restart_system(self):
        """Restart the system"""
        self.status_message = "Restarting system..."
        self.status_color = WARNING_COLOR
        
        # Save all data before restart
        if self.os and hasattr(self.os, 'save_data'):
            self.os.save_data()
        
        # Try to restart
        try:
            os.system("sudo shutdown -r now")
        except Exception as e:
            self.status_message = f"Cannot restart: {e}"
            self.status_color = ERROR_COLOR
            self.confirmation_mode = False
            self.countdown_active = False

    def shutdown_system(self):
        """Shutdown the system"""
        self.status_message = "Shutting down system..."
        self.status_color = ERROR_COLOR
        
        # Save all data before shutdown
        if self.os and hasattr(self.os, 'save_data'):
            self.os.save_data()
        
        # Try to shutdown
        try:
            os.system("sudo shutdown -h now")
        except Exception as e:
            self.status_message = f"Cannot shutdown: {e}"
            self.status_color = ERROR_COLOR
            self.confirmation_mode = False
            self.countdown_active = False

    def exit_application(self):
        """Exit the LightBerry OS application"""
        self.status_message = "Exiting LightBerry OS..."
        self.status_color = ACCENT_COLOR
        
        # Save all data before exit
        if self.os and hasattr(self.os, "save_data"):
            self.os.save_data()
        
        # Show exit message
        print("\n" + "="*50)
        print("To return to LightBerry, run the command: startx")
        print("="*50 + "\n")
        
        # Clean exit
        pygame.quit()
        
        # Kill X server to return to terminal
        try:
            subprocess.run(["pkill", "X"], check=False)
        except Exception as e:
            print(f"Error killing X server: {e}")
        
        sys.exit(0)
    def update(self):
        """Update quit module state"""
        # Update animation
        self.animation_time += 1
        
        # Pulse effect for selected option
        import math
        self.pulse_alpha = int(200 + 55 * math.sin(self.animation_time * 0.1))
        
        # Update countdown
        if self.countdown_active:
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - self.countdown_start) / 1000
            remaining = max(0, self.countdown_time - elapsed)
            
            if remaining <= 0:
                # Auto-execute after countdown
                self.execute_action()
            else:
                self.countdown_time = remaining

    def draw(self, screen):
        """Draw quit module interface"""
        if self.confirmation_mode:
            self.draw_confirmation_dialog(screen)
        else:
            self.draw_main_menu(screen)

    def draw_main_menu(self, screen):
        """Draw main quit menu"""
        # Header
        header_text = "Power Options"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 10))
        
        # Options
        start_y = 70
        option_height = 40
        
        for i, option in enumerate(self.options):
            y_pos = start_y + i * option_height
            
            # Option background
            option_rect = pygame.Rect(20, y_pos, SCREEN_WIDTH - 40, option_height - 5)
            
            if i == self.selected_option:
                # Selected option background
                pygame.draw.rect(screen, SELECTED_COLOR, option_rect)
                pygame.draw.rect(screen, option['color'], option_rect, 3)
            else:
                pygame.draw.rect(screen, BUTTON_COLOR, option_rect)
                pygame.draw.rect(screen, BUTTON_BORDER_COLOR, option_rect, 2)
            
            # Option icon
            icon_surface = self.os.font_l.render(option['icon'], True, option['color'])
            icon_x = option_rect.x + 15
            icon_y = option_rect.y + 5
            screen.blit(icon_surface, (icon_x, icon_y))
            
            # Option name
            name_surface = self.os.font_m.render(option['name'], True, TEXT_COLOR)
            name_x = icon_x + 30
            name_y = option_rect.y + 5
            screen.blit(name_surface, (name_x, name_y))
            
            # Option description
            desc_surface = self.os.font_s.render(option['description'], True, HIGHLIGHT_COLOR)
            desc_x = name_x
            desc_y = name_y + 18
            screen.blit(desc_surface, (desc_x, desc_y))
        
        # Status message
        if self.status_message:
            status_surface = self.os.font_m.render(self.status_message, True, self.status_color)
            status_x = SCREEN_WIDTH // 2 - status_surface.get_width() // 2
            screen.blit(status_surface, (status_x, start_y + len(self.options) * option_height + 10))

        # Show control info if enabled
        if self.show_info:
            info_text = "↑↓: Navigate | Enter: Select | Q: Quick exit | R: Restart | S: Shutdown"
            info_surface = self.os.font_tiny.render(info_text, True, HIGHLIGHT_COLOR)
            info_x = SCREEN_WIDTH // 2 - info_surface.get_width() // 2
            screen.blit(info_surface, (info_x, SCREEN_HEIGHT - 20))

    def draw_confirmation_dialog(self, screen):
        """Draw confirmation dialog"""
        # Semi-transparent overlay (avoid alpha blending issues)
        overlay_color = (0, 0, 0)
        pygame.draw.rect(screen, overlay_color, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Dialog box
        dialog_width = 300
        dialog_height = 120
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2
        
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(screen, BACKGROUND_COLOR, dialog_rect)
        pygame.draw.rect(screen, self.selected_action['color'], dialog_rect, 3)
        
        # Dialog title
        title_text = f"Confirm {self.selected_action['name']}"
        title_surface = self.os.font_l.render(title_text, True, self.selected_action['color'])
        title_x = dialog_x + (dialog_width - title_surface.get_width()) // 2
        screen.blit(title_surface, (title_x, dialog_y + 15))
        
        # Dialog description
        desc_surface = self.os.font_m.render(self.selected_action['description'], True, TEXT_COLOR)
        desc_x = dialog_x + (dialog_width - desc_surface.get_width()) // 2
        screen.blit(desc_surface, (desc_x, dialog_y + 45))
        
        # Countdown
        if self.countdown_active:
            countdown_text = f"Auto-execute in {int(self.countdown_time)} seconds"
            countdown_surface = self.os.font_s.render(countdown_text, True, WARNING_COLOR)
            countdown_x = dialog_x + (dialog_width - countdown_surface.get_width()) // 2
            screen.blit(countdown_surface, (countdown_x, dialog_y + 70))
        
        # Controls
        controls_text = "Y: Yes | N: No | Enter: Confirm | ESC: Cancel"
        controls_surface = self.os.font_tiny.render(controls_text, True, HIGHLIGHT_COLOR)
        controls_x = dialog_x + (dialog_width - controls_surface.get_width()) // 2
        screen.blit(controls_surface, (controls_x, dialog_y + 95))

    def save_data(self):
        """Save quit module data"""
        return {
            "last_action": self.selected_action['action'] if self.selected_action else None
        }

    def load_data(self, data):
        """Load quit module data"""
        # Nothing to load for quit module
        pass
