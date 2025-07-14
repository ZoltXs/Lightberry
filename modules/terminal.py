"""
Terminal Module for LightBerry OS
"""

import pygame
import subprocess
import os
import threading
import time
from config.constants import *

class Terminal:
    def __init__(self, os_instance):
        self.os = os_instance
        self.init_terminal()

    def init_terminal(self):
        """Initialize terminal state"""
        self.screen_buffer = []
        self.input_buffer = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_rate = 30
        self.scroll_offset = 0
        
        # Terminal settings optimized for 400x240 with larger font
        self.max_lines = 200
        self.visible_lines = 12  # More lines for better visibility
        self.max_input_length = 40  # Adjusted for larger font
        
        # Colors
        self.bg_color = (0, 0, 0)
        self.fg_color = (0, 255, 0)  # Green like classic terminals
        self.cursor_color = (255, 255, 255)
        self.prompt_color = (255, 255, 0)  # Yellow for prompt
        
        # Terminal state
        self.command_history = []
        self.history_index = -1
        self.current_directory = os.getcwd()
        
        # Welcome message
        self.add_output_line("LightBerry Terminal v1.0")
        self.add_output_line("Type 'help' for available commands")
        self.add_output_line("")

    def add_output_line(self, line):
        """Add a line to the terminal output"""
        if len(line) > self.max_input_length:
            # Split long lines
            while len(line) > self.max_input_length:
                self.screen_buffer.append(line[:self.max_input_length])
                line = line[self.max_input_length:]
        
        if line:
            self.screen_buffer.append(line)
        
        # Keep buffer size manageable
        if len(self.screen_buffer) > self.max_lines:
            self.screen_buffer = self.screen_buffer[-self.max_lines:]
        
        # Auto-scroll to bottom
        self.scroll_to_bottom()

    def get_prompt(self):
        """Get the command prompt"""
        username = os.getenv('USER', 'pi')
        hostname = os.getenv('HOSTNAME', 'raspberry')
        current_dir = os.path.basename(self.current_directory) or '/'
        return f"{username}@{hostname}:{current_dir}$ "

    def scroll_to_bottom(self):
        """Scroll to the bottom"""
        self.scroll_offset = max(0, len(self.screen_buffer) - self.visible_lines + 1)

    def scroll_up(self):
        """Scroll up"""
        if self.scroll_offset > 0:
            self.scroll_offset -= 1

    def scroll_down(self):
        """Scroll down"""
        max_scroll = max(0, len(self.screen_buffer) - self.visible_lines + 1)
        if self.scroll_offset < max_scroll:
            self.scroll_offset += 1

    def execute_command(self, command):
        """Execute a command"""
        if not command.strip():
            return
            
        # Add command to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Show command being executed
        self.add_output_line(self.get_prompt() + command)
        
        # Handle built-in commands
        if command.strip() == "help":
            self.show_help()
        elif command.strip() == "clear":
            self.screen_buffer = []
            self.scroll_offset = 0
        elif command.strip().startswith("cd "):
            self.change_directory(command[3:].strip())
        elif command.strip() == "pwd":
            self.add_output_line(self.current_directory)
        elif command.strip() == "exit":
            return "exit"
        else:
            # Execute system command
            self.execute_system_command(command)

    def show_help(self):
        """Show help information"""
        help_text = [
            "Built-in commands:",
            "  help     - Show this help",
            "  clear    - Clear screen",
            "  pwd      - Show current directory",
            "  cd <dir> - Change directory",
            "  exit     - Exit terminal",
            "",
            "All other commands are passed to bash.",
            "Use UP/DOWN arrows for command history.",
            "Use Ctrl+UP/DOWN to scroll."
        ]
        for line in help_text:
            self.add_output_line(line)

    def change_directory(self, path):
        """Change directory"""
        try:
            if path == "":
                path = os.path.expanduser("~")
            elif path.startswith("~"):
                path = os.path.expanduser(path)
            
            new_dir = os.path.abspath(os.path.join(self.current_directory, path))
            if os.path.isdir(new_dir):
                self.current_directory = new_dir
                os.chdir(new_dir)
            else:
                self.add_output_line(f"cd: {path}: No such file or directory")
        except Exception as e:
            self.add_output_line(f"cd: {e}")

    def execute_system_command(self, command):
        """Execute a system command"""
        try:
            # Change to current directory
            original_dir = os.getcwd()
            os.chdir(self.current_directory)
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Restore directory
            os.chdir(original_dir)
            
            # Show output
            if result.stdout:
                for line in result.stdout.splitlines():
                    self.add_output_line(line)
            
            if result.stderr:
                for line in result.stderr.splitlines():
                    self.add_output_line(line)
            
            if result.returncode != 0 and not result.stdout and not result.stderr:
                self.add_output_line(f"Command exited with code {result.returncode}")
                
        except subprocess.TimeoutExpired:
            self.add_output_line("Command timed out")
        except Exception as e:
            self.add_output_line(f"Error executing command: {e}")

    def handle_events(self, event):
        """Handle terminal events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            
            elif event.key == pygame.K_RETURN:
                result = self.execute_command(self.input_buffer)
                self.input_buffer = ""
                if result == "exit":
                    return "back"
            
            elif event.key == pygame.K_BACKSPACE:
                if self.input_buffer:
                    self.input_buffer = self.input_buffer[:-1]
            
            elif event.key == pygame.K_UP:
                if event.mod & pygame.KMOD_CTRL:
                    self.scroll_up()
                else:
                    # Command history
                    if self.command_history and self.history_index > 0:
                        self.history_index -= 1
                        self.input_buffer = self.command_history[self.history_index]
            
            elif event.key == pygame.K_DOWN:
                if event.mod & pygame.KMOD_CTRL:
                    self.scroll_down()
                else:
                    # Command history
                    if self.command_history and self.history_index < len(self.command_history) - 1:
                        self.history_index += 1
                        self.input_buffer = self.command_history[self.history_index]
                    else:
                        self.history_index = len(self.command_history)
                        self.input_buffer = ""
            
            elif event.key == pygame.K_c and event.mod & pygame.KMOD_CTRL:
                # Ctrl+C - Cancel current input
                self.input_buffer = ""
                self.add_output_line(self.get_prompt() + self.input_buffer + "^C")
            
            elif event.key == pygame.K_l and event.mod & pygame.KMOD_CTRL:
                # Ctrl+L - Clear screen
                self.screen_buffer = []
                self.scroll_offset = 0
            
            else:
                # Regular character input
                char = event.unicode
                if char and char.isprintable() and len(self.input_buffer) < self.max_input_length:
                    self.input_buffer += char
        
        return None

    def update(self):
        """Update terminal state"""
        # Update cursor blinking
        self.cursor_timer += 1
        if self.cursor_timer >= self.cursor_blink_rate:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen):
        """Draw terminal interface with traditional layout"""
        # Clear screen
        screen.fill(self.bg_color)
        
        # Header
        header_text = "LightBerry Terminal"
        header_surface = self.os.font_s.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 2))
        
        # Terminal window
        terminal_rect = pygame.Rect(2, 18, SCREEN_WIDTH - 4, SCREEN_HEIGHT - 35)
        pygame.draw.rect(screen, self.bg_color, terminal_rect)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, terminal_rect, 1)
        
        # Use larger font (font_s instead of font_tiny)
        line_height = 16  # Increased line height for larger font
        start_y = 22
        
        # Draw input line at the top (traditional terminal style)
        current_input = self.get_prompt() + self.input_buffer
        
        # Add cursor
        if self.cursor_visible:
            current_input += "_"
        
        # Truncate if too long
        if len(current_input) > self.max_input_length:
            current_input = "..." + current_input[-(self.max_input_length-3):]
        
        input_surface = self.os.font_s.render(current_input, True, self.prompt_color)
        screen.blit(input_surface, (5, start_y))
        
        # Draw separator line
        separator_y = start_y + line_height + 2
        pygame.draw.line(screen, HIGHLIGHT_COLOR, (5, separator_y), (SCREEN_WIDTH - 7, separator_y), 1)
        
        # Draw terminal content below input (traditional layout)
        content_start_y = separator_y + 5
        
        # Calculate visible lines (reduced due to input at top)
        available_height = SCREEN_HEIGHT - content_start_y - 25
        visible_lines = min(available_height // line_height, len(self.screen_buffer))
        
        # Calculate visible range
        visible_start = max(0, len(self.screen_buffer) - visible_lines)
        visible_end = len(self.screen_buffer)
        
        # Draw terminal output
        for i in range(visible_start, visible_end):
            line = self.screen_buffer[i]
            y_pos = content_start_y + (i - visible_start) * line_height
            
            # Draw line with larger font
            if line:
                line_surface = self.os.font_s.render(line, True, self.fg_color)
                screen.blit(line_surface, (5, y_pos))
        
        # Controls at bottom
        control_y = SCREEN_HEIGHT - 18
        controls_text = "ESC:Exit | Enter:Execute | Ctrl+L:Clear | ↑↓:History"
        control_surface = self.os.font_tiny.render(controls_text, True, HIGHLIGHT_COLOR)
        screen.blit(control_surface, (2, control_y))

    def save_data(self):
        """Save terminal data"""
        return {
            "command_history": self.command_history[-50:],  # Keep last 50 commands
            "current_directory": self.current_directory
        }

    def load_data(self, data):
        """Load terminal data"""
        if "command_history" in data:
            self.command_history = data["command_history"]
        if "current_directory" in data:
            self.current_directory = data["current_directory"]
            try:
                os.chdir(self.current_directory)
            except:
                self.current_directory = os.getcwd()
        
        self.history_index = len(self.command_history)
