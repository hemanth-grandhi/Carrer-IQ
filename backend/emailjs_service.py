"""
EmailJS Service Module
Free email service for sending notifications
Uses EmailJS (free tier) - no backend SMTP needed
"""

import requests
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class EmailJSService:
    """Send emails using EmailJS (free tier)"""
    
    def __init__(self):
        self.service_id = os.getenv("EMAILJS_SERVICE_ID", "")
        self.template_id = os.getenv("EMAILJS_TEMPLATE_ID", "")
        self.public_key = os.getenv("EMAILJS_PUBLIC_KEY", "")
        self.api_url = "https://api.emailjs.com/api/v1.0/email/send"
        self.enabled = bool(self.service_id and self.template_id and self.public_key)
    
    def send_login_notification(self, recipient_email: str, recipient_name: str) -> bool:
        """
        Send login notification email via EmailJS
        
        Args:
            recipient_email: Recipient email address
            recipient_name: Recipient name
        
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.enabled:
            print("EmailJS not configured. Skipping email notification.")
            return False
        
        template_params = {
            "to_email": recipient_email,
            "to_name": recipient_name,
            "message": "You have successfully logged in to career-IQ. Your future will be bright with the right skills and opportunities.",
            "subject": "Login Successful – career-IQ"
        }
        
        try:
            response = requests.post(
                self.api_url,
                json={
                    "service_id": self.service_id,
                    "template_id": self.template_id,
                    "user_id": self.public_key,
                    "template_params": template_params
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✓ EmailJS notification sent to {recipient_email}")
                return True
            else:
                print(f"✗ EmailJS error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ EmailJS exception: {str(e)}")
            return False


