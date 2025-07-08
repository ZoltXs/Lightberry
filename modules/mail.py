"""
Enhanced Mail Module for LightBerry OS
Professional email client with account management through settings
"""

import pygame
import imaplib
import smtplib
import email
import os
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.constants import *

class Mail:
    def __init__(self, os_instance):
        self.os = os_instance
        self.init_mail()
    
    def init_mail(self):
        """Initialize mail state"""
        self.accounts = []
        self.current_account = None
        self.current_account_index = 0
        self.mode = "inbox"
        self.selected_message = 0
        self.scroll_offset = 0
        self.messages = []
        self.visible_messages = 6
        
        # Compose mail
        self.compose_mode = False
        self.compose_field = "to"  # "to", "subject", "body"
        self.compose_to = ""
        self.compose_subject = ""
        self.compose_body = ""
        self.compose_fields = ["to", "subject", "body"]
        self.compose_field_index = 0
        
        # Text input
        self.text_cursor_visible = True
        self.text_cursor_timer = 0
        
        # Mail status
        self.connection_status = "Disconnected"
        self.last_update = None
        self.error_message = ""
        
        # Load mail accounts from settings
        self.load_accounts()
        
        # If no accounts, show setup message
        if not self.accounts:
            self.show_setup_message()
    
    def load_accounts(self):
        """Load mail accounts from settings"""
        try:
            settings_data = self.os.data_manager.get_module_data("Settings")
            mail_accounts = settings_data.get("mail_accounts", [])
            
            for account_data in mail_accounts:
                account = {
                    "name": account_data.get("name", "Unknown"),
                    "email": account_data.get("email", ""),
                    "password": account_data.get("password", ""),
                    "imap_server": account_data.get("imap_server", ""),
                    "imap_port": account_data.get("imap_port", 993),
                    "smtp_server": account_data.get("smtp_server", ""),
                    "smtp_port": account_data.get("smtp_port", 587),
                    "use_ssl": account_data.get("use_ssl", True)
                }
                self.accounts.append(account)
            
            if self.accounts:
                self.current_account = self.accounts[0]
                self.current_account_index = 0
                
        except Exception as e:
            print(f"Error loading mail accounts: {e}")
            self.error_message = "Failed to load accounts"
    
    def show_setup_message(self):
        """Show setup message when no accounts configured"""
        self.error_message = "No mail accounts configured. Please add accounts in Settings."
    
    def connect_to_account(self):
        """Connect to current mail account"""
        if not self.current_account:
            self.error_message = "No account selected"
            return False
        
        try:
            # Test IMAP connection
            if self.current_account["use_ssl"]:
                server = imaplib.IMAP4_SSL(self.current_account["imap_server"], 
                                         self.current_account["imap_port"])
            else:
                server = imaplib.IMAP4(self.current_account["imap_server"], 
                                     self.current_account["imap_port"])
            
            server.login(self.current_account["email"], self.current_account["password"])
            server.select("INBOX")
            
            self.connection_status = "Connected"
            self.error_message = ""
            server.logout()
            return True
            
        except Exception as e:
            self.connection_status = "Connection Failed"
            self.error_message = f"Connection error: {str(e)[:30]}..."
            return False
    
    def fetch_messages(self):
        """Fetch messages from current account"""
        if not self.current_account:
            return
        
        try:
            if self.current_account["use_ssl"]:
                server = imaplib.IMAP4_SSL(self.current_account["imap_server"], 
                                         self.current_account["imap_port"])
            else:
                server = imaplib.IMAP4(self.current_account["imap_server"], 
                                     self.current_account["imap_port"])
            
            server.login(self.current_account["email"], self.current_account["password"])
            server.select("INBOX")
            
            # Search for messages
            result, data = server.search(None, "ALL")
            message_ids = data[0].split()
            
            # Fetch latest 20 messages
            messages = []
            for msg_id in message_ids[-20:]:
                result, msg_data = server.fetch(msg_id, "(RFC822)")
                email_message = email.message_from_bytes(msg_data[0][1])
                
                # Extract message info
                subject = email_message.get("Subject", "No Subject")
                sender = email_message.get("From", "Unknown Sender")
                date = email_message.get("Date", "Unknown Date")
                
                # Get message body
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            break
                else:
                    body = email_message.get_payload(decode=True).decode("utf-8", errors="ignore")
                
                messages.append({
                    "id": msg_id,
                    "subject": subject,
                    "sender": sender,
                    "date": date,
                    "body": body[:200] + "..." if len(body) > 200 else body
                })
            
            self.messages = messages
            self.last_update = datetime.now()
            self.connection_status = "Connected"
            self.error_message = ""
            
            server.logout()
            
        except Exception as e:
            self.error_message = f"Fetch error: {str(e)[:30]}..."
            self.connection_status = "Error"
    
    def send_message(self, to_address, subject, body):
        """Send email message"""
        if not self.current_account:
            self.error_message = "No account selected"
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.current_account["email"]
            msg['To'] = to_address
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.current_account["smtp_server"], 
                                self.current_account["smtp_port"])
            server.starttls()
            server.login(self.current_account["email"], self.current_account["password"])
            
            # Send message
            server.send_message(msg)
            server.quit()
            
            self.error_message = "Message sent successfully"
            return True
            
        except Exception as e:
            self.error_message = f"Send error: {str(e)[:30]}..."
            return False
    
    def handle_events(self, event):
        """Handle mail events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.compose_mode:
                    self.compose_mode = False
                    self.compose_to = ""
                    self.compose_subject = ""
                    self.compose_body = ""
                else:
                    return "back"
            
            elif self.compose_mode:
                self.handle_compose_events(event)
            
            else:
                self.handle_inbox_events(event)
        
        return None
    
    def handle_inbox_events(self, event):
        """Handle inbox events"""
        if event.key == pygame.K_UP:
            self.selected_message = max(0, self.selected_message - 1)
            if self.selected_message < self.scroll_offset:
                self.scroll_offset = max(0, self.scroll_offset - 1)
        
        elif event.key == pygame.K_DOWN:
            self.selected_message = min(len(self.messages) - 1, self.selected_message + 1)
            if self.selected_message >= self.scroll_offset + self.visible_messages:
                self.scroll_offset = min(len(self.messages) - self.visible_messages, 
                                       self.scroll_offset + 1)
        
        elif event.key == pygame.K_LEFT:
            if len(self.accounts) > 1:
                self.current_account_index = max(0, self.current_account_index - 1)
                self.current_account = self.accounts[self.current_account_index]
                self.messages = []
                self.selected_message = 0
                self.scroll_offset = 0
        
        elif event.key == pygame.K_RIGHT:
            if len(self.accounts) > 1:
                self.current_account_index = min(len(self.accounts) - 1, 
                                               self.current_account_index + 1)
                self.current_account = self.accounts[self.current_account_index]
                self.messages = []
                self.selected_message = 0
                self.scroll_offset = 0
        
        elif event.key == pygame.K_RETURN:
            if self.messages:
                # Show message details (could expand this)
                pass
        
        elif event.key == pygame.K_c:
            self.compose_mode = True
            self.compose_field_index = 0
            self.compose_field = self.compose_fields[0]
        
        elif event.key == pygame.K_r:
            if self.current_account:
                self.fetch_messages()
        
        elif event.key == pygame.K_t:
            if self.current_account:
                self.connect_to_account()
    
    def handle_compose_events(self, event):
        """Handle compose events"""
        if event.key == pygame.K_TAB:
            self.compose_field_index = (self.compose_field_index + 1) % len(self.compose_fields)
            self.compose_field = self.compose_fields[self.compose_field_index]
        
        elif event.key == pygame.K_UP:
            self.compose_field_index = max(0, self.compose_field_index - 1)
            self.compose_field = self.compose_fields[self.compose_field_index]
        
        elif event.key == pygame.K_DOWN:
            self.compose_field_index = min(len(self.compose_fields) - 1, 
                                         self.compose_field_index + 1)
            self.compose_field = self.compose_fields[self.compose_field_index]
        
        elif event.key == pygame.K_RETURN:
            if self.compose_field == "body":
                self.compose_body += "\n"
            elif self.compose_field_index < len(self.compose_fields) - 1:
                self.compose_field_index += 1
                self.compose_field = self.compose_fields[self.compose_field_index]
        
        elif event.key == pygame.K_BACKSPACE:
            if self.compose_field == "to":
                self.compose_to = self.compose_to[:-1]
            elif self.compose_field == "subject":
                self.compose_subject = self.compose_subject[:-1]
            elif self.compose_field == "body":
                self.compose_body = self.compose_body[:-1]
        
        elif event.key == pygame.K_F1:  # Send (F1 as send key)
            if self.compose_to and self.compose_subject:
                success = self.send_message(self.compose_to, self.compose_subject, self.compose_body)
                if success:
                    self.compose_mode = False
                    self.compose_to = ""
                    self.compose_subject = ""
                    self.compose_body = ""
        
        else:
            char = event.unicode
            if char.isprintable():
                if self.compose_field == "to" and len(self.compose_to) < 50:
                    self.compose_to += char
                elif self.compose_field == "subject" and len(self.compose_subject) < 50:
                    self.compose_subject += char
                elif self.compose_field == "body" and len(self.compose_body) < 500:
                    self.compose_body += char
    
    def update(self):
        """Update mail state"""
        # Update text cursor
        self.text_cursor_timer += 1
        if self.text_cursor_timer >= 30:
            self.text_cursor_visible = not self.text_cursor_visible
            self.text_cursor_timer = 0
    
    def draw(self, screen):
        """Draw mail interface"""
        if self.compose_mode:
            self.draw_compose_mode(screen)
        else:
            self.draw_inbox_mode(screen)
    
    def draw_inbox_mode(self, screen):
        """Draw inbox mode"""
        # Header
        if self.current_account:
            header_text = f"Mail - {self.current_account['name']}"
        else:
            header_text = "Mail - No Account"
        
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # Account selector
        if len(self.accounts) > 1:
            account_text = f"Account {self.current_account_index + 1}/{len(self.accounts)}"
            account_surface = self.os.font_m.render(account_text, True, HIGHLIGHT_COLOR)
            account_x = SCREEN_WIDTH // 2 - account_surface.get_width() // 2
            screen.blit(account_surface, (account_x, 25))
        
        # Status
        status_y = 45
        status_color = SUCCESS_COLOR if self.connection_status == "Connected" else ERROR_COLOR
        status_surface = self.os.font_m.render(self.connection_status, True, status_color)
        screen.blit(status_surface, (10, status_y))
        
        # Last update
        if self.last_update:
            update_text = f"Updated: {self.last_update.strftime('%H:%M')}"
            update_surface = self.os.font_s.render(update_text, True, HIGHLIGHT_COLOR)
            screen.blit(update_surface, (SCREEN_WIDTH - 100, status_y))
        
        # Error message
        if self.error_message:
            error_surface = self.os.font_s.render(self.error_message, True, ERROR_COLOR)
            screen.blit(error_surface, (10, status_y + 20))
        
        # Messages
        if not self.accounts:
            no_account_text = "No mail accounts configured."
            no_account_surface = self.os.font_m.render(no_account_text, True, WARNING_COLOR)
            no_account_x = SCREEN_WIDTH // 2 - no_account_surface.get_width() // 2
            screen.blit(no_account_surface, (no_account_x, 90))
            
            setup_text = "Add accounts in Settings → Mail Accounts"
            setup_surface = self.os.font_s.render(setup_text, True, HIGHLIGHT_COLOR)
            setup_x = SCREEN_WIDTH // 2 - setup_surface.get_width() // 2
            screen.blit(setup_surface, (setup_x, 110))
        
        elif not self.messages:
            no_messages_text = "No messages or not connected"
            no_messages_surface = self.os.font_m.render(no_messages_text, True, WARNING_COLOR)
            no_messages_x = SCREEN_WIDTH // 2 - no_messages_surface.get_width() // 2
            screen.blit(no_messages_surface, (no_messages_x, 90))
        
        else:
            # Message list
            message_y = 70
            visible_messages = self.messages[self.scroll_offset:self.scroll_offset + self.visible_messages]
            
            for i, message in enumerate(visible_messages):
                msg_index = self.scroll_offset + i
                y_pos = message_y + i * 25
                
                # Message background
                msg_rect = pygame.Rect(10, y_pos, SCREEN_WIDTH - 20, 23)
                if msg_index == self.selected_message:
                    pygame.draw.rect(screen, SELECTED_COLOR, msg_rect)
                    pygame.draw.rect(screen, ACCENT_COLOR, msg_rect, 2)
                
                # Sender
                sender_text = message["sender"]
                if len(sender_text) > 20:
                    sender_text = sender_text[:20] + "..."
                
                sender_surface = self.os.font_m.render(sender_text, True, TEXT_COLOR)
                screen.blit(sender_surface, (15, y_pos + 2))
                
                # Subject
                subject_text = message["subject"]
                if len(subject_text) > 15:
                    subject_text = subject_text[:15] + "..."
                
                subject_surface = self.os.font_s.render(subject_text, True, HIGHLIGHT_COLOR)
                screen.blit(subject_surface, (15, y_pos + 14))
                
                # Date (simplified)
                date_text = message["date"][:10] if len(message["date"]) > 10 else message["date"]
                date_surface = self.os.font_tiny.render(date_text, True, HIGHLIGHT_COLOR)
                date_x = SCREEN_WIDTH - date_surface.get_width() - 15
                screen.blit(date_surface, (date_x, y_pos + 2))
            
            # Scroll indicators
            if self.scroll_offset > 0:
                up_text = "↑ More messages"
                up_surface = self.os.font_tiny.render(up_text, True, HIGHLIGHT_COLOR)
                screen.blit(up_surface, (10, message_y - 10))
            
            if self.scroll_offset + self.visible_messages < len(self.messages):
                down_text = "↓ More messages"
                down_surface = self.os.font_tiny.render(down_text, True, HIGHLIGHT_COLOR)
                screen.blit(down_surface, (10, message_y + self.visible_messages * 25))
        
        # Controls
        controls = [
            "↑↓: Navigate messages",
            "←→: Change account",
            "C: Compose",
            "R: Refresh",
            "T: Test connection"
        ]
        
        control_y = SCREEN_HEIGHT - 40
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 3) * 125
            control_y_pos = control_y + (i // 3) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def draw_compose_mode(self, screen):
        """Draw compose mode"""
        # Header
        header_text = "Compose Mail"
        header_surface = self.os.font_l.render(header_text, True, ACCENT_COLOR)
        header_x = SCREEN_WIDTH // 2 - header_surface.get_width() // 2
        screen.blit(header_surface, (header_x, 5))
        
        # From field (read-only)
        from_label = "From:"
        from_surface = self.os.font_m.render(from_label, True, TEXT_COLOR)
        screen.blit(from_surface, (10, 30))
        
        from_email = self.current_account["email"] if self.current_account else "No account"
        from_email_surface = self.os.font_m.render(from_email, True, HIGHLIGHT_COLOR)
        screen.blit(from_email_surface, (60, 30))
        
        # To field
        to_y = 50
        to_label = "To:"
        to_surface = self.os.font_m.render(to_label, True, TEXT_COLOR)
        screen.blit(to_surface, (10, to_y))
        
        to_rect = pygame.Rect(60, to_y, SCREEN_WIDTH - 70, 20)
        to_color = SELECTED_COLOR if self.compose_field == "to" else BUTTON_COLOR
        pygame.draw.rect(screen, to_color, to_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, to_rect, 2)
        
        to_text = self.compose_to
        if self.compose_field == "to" and self.text_cursor_visible:
            to_text += "|"
        
        to_text_surface = self.os.font_m.render(to_text, True, TEXT_COLOR)
        screen.blit(to_text_surface, (65, to_y + 2))
        
        # Subject field
        subject_y = 75
        subject_label = "Subject:"
        subject_surface = self.os.font_m.render(subject_label, True, TEXT_COLOR)
        screen.blit(subject_surface, (10, subject_y))
        
        subject_rect = pygame.Rect(75, subject_y, SCREEN_WIDTH - 85, 20)
        subject_color = SELECTED_COLOR if self.compose_field == "subject" else BUTTON_COLOR
        pygame.draw.rect(screen, subject_color, subject_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, subject_rect, 2)
        
        subject_text = self.compose_subject
        if self.compose_field == "subject" and self.text_cursor_visible:
            subject_text += "|"
        
        subject_text_surface = self.os.font_m.render(subject_text, True, TEXT_COLOR)
        screen.blit(subject_text_surface, (80, subject_y + 2))
        
        # Body field
        body_y = 105
        body_label = "Message:"
        body_surface = self.os.font_m.render(body_label, True, TEXT_COLOR)
        screen.blit(body_surface, (10, body_y))
        
        body_rect = pygame.Rect(10, body_y + 20, SCREEN_WIDTH - 20, 80)
        body_color = SELECTED_COLOR if self.compose_field == "body" else BUTTON_COLOR
        pygame.draw.rect(screen, body_color, body_rect)
        pygame.draw.rect(screen, BUTTON_BORDER_COLOR, body_rect, 2)
        
        # Body text (wrapped)
        body_text = self.compose_body
        if self.compose_field == "body" and self.text_cursor_visible:
            body_text += "|"
        
        body_lines = body_text.split('\n')
        for i, line in enumerate(body_lines[:4]):  # Show first 4 lines
            if len(line) > 45:
                line = line[:45] + "..."
            
            line_surface = self.os.font_m.render(line, True, TEXT_COLOR)
            screen.blit(line_surface, (15, body_y + 25 + i * 16))
        
        # Status message
        if self.error_message:
            error_surface = self.os.font_s.render(self.error_message, True, 
                                                SUCCESS_COLOR if "success" in self.error_message.lower() 
                                                else ERROR_COLOR)
            screen.blit(error_surface, (10, body_y + 105))
        
        # Controls
        controls = [
            "Tab/↑↓: Navigate fields",
            "F1: Send message",
            "Enter: New line (body)",
            "ESC: Cancel"
        ]
        
        control_y = SCREEN_HEIGHT - 35
        for i, control in enumerate(controls):
            control_surface = self.os.font_tiny.render(control, True, HIGHLIGHT_COLOR)
            control_x = 10 + (i % 2) * 180
            control_y_pos = control_y + (i // 2) * 12
            screen.blit(control_surface, (control_x, control_y_pos))
    
    def save_data(self):
        """Save mail data"""
        return {
            "current_account_index": self.current_account_index
        }
    
    def load_data(self, data):
        """Load mail data"""
        self.current_account_index = data.get("current_account_index", 0)
        if self.accounts and self.current_account_index < len(self.accounts):
            self.current_account = self.accounts[self.current_account_index]
