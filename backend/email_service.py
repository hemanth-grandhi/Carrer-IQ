"""
Email Service Module
Sends email notifications using SMTP or EmailJS (free tier)
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from emailjs_service import EmailJSService


class EmailService:
    """Send emails via SMTP or EmailJS (free tier)"""
    
    def __init__(self):
        # Email configuration - can be set via environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        self.use_tls = True
        
        # Try EmailJS first (free, no backend SMTP needed)
        self.emailjs = EmailJSService()
    
    def send_login_notification(self, recipient_email: str, recipient_name: str) -> bool:
        """
        Send login notification email
        
        Args:
            recipient_email: Recipient email address
            recipient_name: Recipient name
        
        Returns:
            True if email sent successfully, False otherwise
        """
        # Try EmailJS first (free, easier)
        if self.emailjs.enabled:
            return self.emailjs.send_login_notification(recipient_email, recipient_name)
        
        # Fallback to SMTP
        subject = "Login Successful – career-IQ"
        
        body = f"""Hello {recipient_name},

You have successfully logged in to career-IQ.

Your future will be bright with the right skills and opportunities.
Let's build your career smarter with AI.

– career-IQ Team"""
        
        return self._send_email(recipient_email, subject, body)
    
    def _send_email(self, recipient: str, subject: str, body: str) -> bool:
        """
        Send email via SMTP
        
        Args:
            recipient: Recipient email address
            subject: Email subject
            body: Email body
        
        Returns:
            True if sent successfully, False otherwise
        """
        # If no email credentials configured, print to console (for development)
        if not self.sender_email or not self.sender_password:
            print("\n" + "="*50)
            print("EMAIL NOTIFICATION (SMTP not configured)")
            print("="*50)
            print(f"To: {recipient}")
            print(f"Subject: {subject}")
            print(f"\n{body}")
            print("="*50 + "\n")
            print("To enable real email sending, set environment variables:")
            print("  SENDER_EMAIL=your-email@gmail.com")
            print("  SENDER_PASSWORD=your-app-password")
            print("="*50 + "\n")
            return True  # Return True for development
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            # Log successful email send
            print(f"✓ Login notification email sent successfully to {recipient}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"✗ Email authentication failed: {str(e)}")
            print("   Please check your SENDER_EMAIL and SENDER_PASSWORD in .env file")
            print("   For Gmail, make sure you're using an App Password, not your regular password")
            return False
        except smtplib.SMTPException as e:
            print(f"✗ SMTP error while sending email: {str(e)}")
            return False
        except Exception as e:
            print(f"✗ Error sending email: {str(e)}")
            return False


