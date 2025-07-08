"""
Enhanced Terminal Module for LightBerry OS
Professional terminal emulator with command execution and improved UI
"""

import pygame
import subprocess
import os
import threading
from config.constants import *

class Terminal:
    def __init__(self, os_instance):
        self.os = os_instance
        self.init_terminal()
    
    def init_terminal(self):
        """Initialize terminal state"""
        self.command_history = []
        self.current_command = ""
        self.output_lines = []
        self.scroll_offset = 0
        self.max_history = 100
        self.max_output_lines = 1000
        self.visible_lines = 10
        
        # Cursor
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # Working directory
        self.current_dir = os.getcwd()
        
        # Add welcome message
        self.output_lines.append("LightBerry OS Terminal")
        self.output_lines.append("Type 'help' for available commands")
        self.output_lines.append("")
        
        # Built-in commands
        self.builtin_commands = {
            "help": self.cmd_help,
            "clear": self.cmd_clear,
            "pwd": self.cmd_pwd,
            "cd": self.cmd_cd,
            "ls": self.cmd_ls,
            "cat": self.cmd_cat,
            "echo": self.cmd_echo,
            "date": self.cmd_date,
            "whoami": self.cmd_whoami,
            "uname": self.cmd_uname,
            "df": self.cmd_df,
            "free": self.cmd_free,
            "ps": self.cmd_ps,
            "top": self.cmd_top,
            "history": self.cmd_history,
            "exit": self.cmd_exit
        }
    
    def handle_events(self, event):
        """Handle terminal events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            
            elif event.key == pygame.K_RETURN:
                self.execute_command()
            
            elif event.key == pygame.K_UP:
                self.scroll_up()
            
            elif event.key == pygame.K_DOWN:
                self.scroll_down()
            
            elif event.key == pygame.K_BACKSPACE:
                if self.current_command:
                    self.current_command = self.current_command[:-1]
            
            elif event.key == pygame.K_TAB:
                self.tab_completion()
            
            else:
                char = event.unicode
                if char.isprintable():
                    self.current_command += char
        
        return None
    
    def execute_command(self):
        """Execute the current command"""
        if not self.current_command.strip():
            return
        
        # Add command to history
        self.command_history.append(self.current_command)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
        
        # Display command
        prompt = f"{os.path.basename(self.current_dir)}$ {self.current_command}"
        self.output_lines.append(prompt)
        
        # Parse command
        parts = self.current_command.strip().split()
        if not parts:
            self.current_command = ""
            return
        
        command = parts[0]
        args = parts[1:]
        
        # Execute command
        if command in self.builtin_commands:
            self.builtin_commands[command](args)
        else:
            self.execute_system_command(command, args)
        
        # Clear current command
        self.current_command = ""
        
        # Limit output lines
        if len(self.output_lines) > self.max_output_lines:
            self.output_lines = self.output_lines[-self.max_output_lines:]
        
        # Auto-scroll to bottom
        self.scroll_offset = max(0, len(self.output_lines) - self.visible_lines)
    
    def execute_system_command(self, command, args):
        """Execute system command"""
        try:
            full_command = [command] + args
            result = subprocess.run(full_command, 
                                  capture_output=True, 
                                  text=True, 
                                  cwd=self.current_dir,
                                  timeout=30)
            
            if result.stdout:
                self.output_lines.extend(result.stdout.split('\n'))
            
            if result.stderr:
                self.output_lines.extend([f"Error: {line}" for line in result.stderr.split('\n')])
            
            if result.returncode != 0:
                self.output_lines.append(f"Command exited with code {result.returncode}")
        
        except subprocess.TimeoutExpired:
            self.output_lines.append("Command timed out")
        
        except FileNotFoundError:
            self.output_lines.append(f"Command not found: {command}")
        
        except Exception as e:
            self.output_lines.append(f"Error executing command: {e}")
    
    def scroll_up(self):
        """Scroll output up"""
        self.scroll_offset = max(0, self.scroll_offset - 1)
    
    def scroll_down(self):
        """Scroll output down"""
        max_scroll = max(0, len(self.output_lines) - self.visible_lines)
        self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
    
    def tab_completion(self):
        """Simple tab completion"""
        if not self.current_command:
            return
        
        # Get available commands
        available_commands = list(self.builtin_commands.keys())
        
        # Add system commands in PATH
        try:
            path_commands = []
            for path in os.environ.get('PATH', '').split(':'):
                if os.path.isdir(path):
                    for file in os.listdir(path):
                        if os.access(os.path.join(path, file), os.X_OK):
                            path_commands.append(file)
            
            available_commands.extend(path_commands)
        except:
            pass
        
        # Find matches
        matches = [cmd for cmd in available_commands if cmd.startswith(self.current_command)]
        
        if len(matches) == 1:
            self.current_command = matches[0]
        elif len(matches) > 1:
            self.output_lines.append(f"Matches: {', '.join(matches[:10])}")
    
    # Built-in commands
    def cmd_help(self, args):
        """Show help"""
        help_text = [
            "Available commands:",
            "  help     - Show this help",
            "  clear    - Clear screen",
            "  pwd      - Show current directory",
            "  cd       - Change directory",
            "  ls       - List directory contents",
            "  cat      - Display file contents",
            "  echo     - Echo text",
            "  date     - Show current date/time",
            "  whoami   - Show current user",
            "  uname    - Show system info",
            "  df       - Show disk usage",
            "  free     - Show memory usage",
            "  ps       - Show processes",
            "  history  - Show command history",
            "  exit     - Exit terminal",
            "",
            "Use arrow keys to scroll, Tab for completion"
        ]
        self.output_lines.extend(help_text)
    
    def cmd_clear(self, args):
        """Clear screen"""
        self.output_lines = []
        self.scroll_offset = 0
    
    def cmd_pwd(self, args):
        """Show current directory"""
        self.output_lines.append(self.current_dir)
    
    def cmd_cd(self, args):
        """Change directory"""
        if not args:
            new_dir = os.path.expanduser("~")
        else:
            new_dir = args[0]
        
        try:
            if not os.path.isabs(new_dir):
                new_dir = os.path.join(self.current_dir, new_dir)
            
            new_dir = os.path.abspath(new_dir)
            
            if os.path.isdir(new_dir):
                self.current_dir = new_dir
                os.chdir(new_dir)
            else:
                self.output_lines.append(f"cd: {new_dir}: No such directory")
        
        except Exception as e:
            self.output_lines.append(f"cd: {e}")
    
    def cmd_ls(self, args):
        """List directory contents"""
        try:
            target_dir = args[0] if args else self.current_dir
            
            if not os.path.isabs(target_dir):
                target_dir = os.path.join(self.current_dir, target_dir)
            
            items = os.listdir(target_dir)
            items.sort()
            
            for item in items:
                item_path = os.path.join(target_dir, item)
                if os.path.isdir(item_path):
                    self.output_lines.append(f"{item}/")
                else:
                    self.output_lines.append(item)
        
        except Exception as e:
            self.output_lines.append(f"ls: {e}")
    
    def cmd_cat(self, args):
        """Display file contents"""
        if not args:
            self.output_lines.append("cat: missing filename")
            return
        
        try:
            filename = args[0]
            
            if not os.path.isabs(filename):
                filename = os.path.join(self.current_dir, filename)
            
            with open(filename, 'r') as f:
                content = f.read()
                self.output_lines.extend(content.split('\n'))
        
        except Exception as e:
            self.output_lines.append(f"cat: {e}")
    
    def cmd_echo(self, args):
        """Echo text"""
        self.output_lines.append(' '.join(args))
    
    def cmd_date(self, args):
        """Show current date/time"""
        from datetime import datetime
        self.output_lines.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def cmd_whoami(self, args):
        """Show current user"""
        self.output_lines.append(os.getenv('USER', 'lightberry'))
    
    def cmd_uname(self, args):
        """Show system info"""
        import platform
        self.output_lines.append(f"{platform.system()} {platform.release()}")
    
    def cmd_df(self, args):
        """Show disk usage"""
        try:
            result = subprocess.run(['df', '-h'], capture_output=True, text=True)
            if result.stdout:
                self.output_lines.extend(result.stdout.split('\n'))
        except:
            self.output_lines.append("df: command not available")
    
    def cmd_free(self, args):
        """Show memory usage"""
        try:
            result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            if result.stdout:
                self.output_lines.extend(result.stdout.split('\n'))
        except:
            self.output_lines.append("free: command not available")
    
    def cmd_ps(self, args):
        """Show processes"""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if result.stdout:
                lines = result.stdout.split('\n')[:20]  # Limit to first 20 lines
                self.output_lines.extend(lines)
        except:
            self.output_lines.append("ps: command not available")
    
    def cmd_top(self, args):
        """Show top processes"""
        try:
            result = subprocess.run(['top', '-b', '-n', '1'], capture_output=True, text=True)
            if result.stdout:
                lines = result.stdout.split('\n')[:15]  # Limit to first 15 lines
                self.output_lines.extend(lines)
        except:
            self.output_lines.append("top: command not available")
    
    def cmd_history(self, args):
        """Show command history"""
        for i, cmd in enumerate(self.command_history[-20:], 1):
            self.output_lines.append(f"{i:3d}  {cmd}")
    
    def cmd_exit(self, args):
        """Exit terminal"""
        self.output_lines.append("Goodbye!")
        # Could signal to parent to exit
    
    def update(self):
        """Update terminal state"""
        # Update cursor
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen):
        """Draw terminal interface"""
        # Header
        header_text = "Terminal"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Terminal background
        terminal_rect = pygame.Rect(5, 25, SCREEN_WIDTH - 10, SCREEN_HEIGHT - 75)
        pygame.draw.rect(screen, (10, 10, 10), terminal_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, terminal_rect, 2)
        
        # Output lines
        line_height = 16
        start_y = 30
        
        visible_lines = self.output_lines[self.scroll_offset:self.scroll_offset + self.visible_lines]
        
        for i, line in enumerate(visible_lines):
            if not line:
                continue
            
            y_pos = start_y + i * line_height
            
            # Truncate long lines
            if len(line) > 50:
                line = line[:50] + "..."
            
            # Color coding
            if line.startswith("Error:"):
                color = ERROR_COLOR
            elif line.endswith("$"):
                color = SUCCESS_COLOR
            else:
                color = TEXT_COLOR
            
            line_surface = self.os.font_m.render(line, True, color)
            screen.blit(line_surface, (10, y_pos))
        
        # Scroll indicators
        if self.scroll_offset > 0:
            up_text = "↑ More above"
            up_surface = self.os.font_tiny.render(up_text, True, HIGHLIGHT_COLOR)
            screen.blit(up_surface, (SCREEN_WIDTH - 100, 30))
        
        if self.scroll_offset + self.visible_lines < len(self.output_lines):
            down_text = "↓ More below"
            down_surface = self.os.font_tiny.render(down_text, True, HIGHLIGHT_COLOR)
            screen.blit(down_surface, (SCREEN_WIDTH - 100, start_y + self.visible_lines * line_height))
        
        # Command input area (moved to top)
        input_y = SCREEN_HEIGHT - 45
        input_rect = pygame.Rect(5, input_y, SCREEN_WIDTH - 10, 25)
        pygame.draw.rect(screen, BUTTON_COLOR, input_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, input_rect, 2)
        
        # Prompt
        prompt_text = f"{os.path.basename(self.current_dir)}$ "
        prompt_surface = self.os.font_m.render(prompt_text, True, SUCCESS_COLOR)
        screen.blit(prompt_surface, (10, input_y + 3))
        
        # Current command
        command_x = 10 + prompt_surface.get_width()
        command_text = self.current_command
        
        # Add cursor
        if self.cursor_visible:
            command_text += "|"
        
        command_surface = self.os.font_m.render(command_text, True, TEXT_COLOR)
        screen.blit(command_surface, (command_x, input_y + 3))
        
        # Controls
        controls = [
            "Type: Enter command",
            "Enter: Execute",
            "↑↓: Scroll output",
            "Tab: Completion",
            "ESC: Back"
        ]
        
        control_y = SCREEN_HEIGHT - 15
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 3) * 125
            control_y_pos = control_y + (i // 3) * 10
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def save_data(self):
        """Save terminal data"""
        return {
            "command_history": self.command_history[-50:],  # Save last 50 commands
            "current_dir": self.current_dir
        }
    
    def load_data(self, data):
        """Load terminal data"""
        self.command_history = data.get("command_history", [])
        self.current_dir = data.get("current_dir", os.getcwd())
        try:
            os.chdir(self.current_dir)
        except:
            self.current_dir = os.getcwd()
