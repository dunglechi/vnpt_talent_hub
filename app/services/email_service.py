"""
Email service for sending verification and notification emails.
Supports both real SMTP and console logging for development/testing.
"""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service with configurable SMTP backend.
    Falls back to console logging if SMTP is not configured.
    """
    
    def __init__(self):
        """Initialize email service with environment configuration."""
        self.smtp_enabled = os.getenv("SMTP_ENABLED", "false").lower() == "true"
        self.smtp_host = os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.sender_email = os.getenv("SMTP_SENDER_EMAIL", "noreply@vnpt.vn")
        self.sender_name = os.getenv("SMTP_SENDER_NAME", "VNPT Talent Hub")
        self.base_url = os.getenv("BASE_URL", "http://localhost:3000")
        
        if self.smtp_enabled:
            logger.info(f"Email service initialized with SMTP: {self.smtp_host}:{self.smtp_port}")
        else:
            logger.info("Email service initialized in CONSOLE MODE (SMTP disabled)")
    
    def send_email(
        self, 
        to: str, 
        subject: str, 
        body: str, 
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send an email to the specified recipient.
        
        Args:
            to: Recipient email address
            subject: Email subject line
            body: Plain text email body
            html_body: Optional HTML version of email body
            
        Returns:
            True if email sent successfully (or logged), False otherwise
        """
        if not self.smtp_enabled:
            # Console logging mode for development
            logger.info("="*80)
            logger.info("📧 EMAIL (Console Mode - SMTP Disabled)")
            logger.info("="*80)
            logger.info(f"From: {self.sender_name} <{self.sender_email}>")
            logger.info(f"To: {to}")
            logger.info(f"Subject: {subject}")
            logger.info("-"*80)
            logger.info("Body:")
            logger.info(body)
            if html_body:
                logger.info("-"*80)
                logger.info("HTML Body:")
                logger.info(html_body)
            logger.info("="*80)
            return True
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to
            msg['Subject'] = subject
            
            # Attach plain text body
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {str(e)}")
            return False
    
    def send_verification_email(self, to: str, token: str, user_name: str) -> bool:
        """
        Send email verification link to user.
        
        Args:
            to: User's email address
            token: Verification token
            user_name: User's full name
            
        Returns:
            True if email sent successfully
        """
        verification_url = f"{self.base_url}/verify?token={token}"
        
        subject = "Verify Your Email - VNPT Talent Hub"
        
        # Plain text body
        body = f"""
Hello {user_name},

Thank you for registering with VNPT Talent Hub!

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you did not create an account, please ignore this email.

Best regards,
VNPT Talent Hub Team
"""
        
        # HTML body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #0066cc; color: white; padding: 20px; text-align: center; }}
        .content {{ background-color: #f9f9f9; padding: 30px; }}
        .button {{ display: inline-block; padding: 12px 30px; background-color: #0066cc; 
                   color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>VNPT Talent Hub</h1>
        </div>
        <div class="content">
            <h2>Hello {user_name},</h2>
            <p>Thank you for registering with VNPT Talent Hub!</p>
            <p>Please verify your email address by clicking the button below:</p>
            <a href="{verification_url}" class="button">Verify Email Address</a>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #0066cc;">{verification_url}</p>
            <p><strong>This link will expire in 24 hours.</strong></p>
            <p>If you did not create an account, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2025 VNPT Talent Hub. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(to, subject, body, html_body)
    
    def send_password_reset_email(self, to: str, token: str, user_name: str) -> bool:
        """
        Send password reset link to user.
        
        Args:
            to: User's email address
            token: Password reset token
            user_name: User's full name
            
        Returns:
            True if email sent successfully
        """
        reset_url = f"{self.base_url}/reset-password?token={token}"
        
        subject = "Password Reset Request - VNPT Talent Hub"
        
        body = f"""
Hello {user_name},

We received a request to reset your password for VNPT Talent Hub.

Click the link below to reset your password:

{reset_url}

This link will expire in 1 hour.

If you did not request a password reset, please ignore this email and your password will remain unchanged.

Best regards,
VNPT Talent Hub Team
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #cc0000; color: white; padding: 20px; text-align: center; }}
        .content {{ background-color: #f9f9f9; padding: 30px; }}
        .button {{ display: inline-block; padding: 12px 30px; background-color: #cc0000; 
                   color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        .warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>VNPT Talent Hub</h1>
        </div>
        <div class="content">
            <h2>Hello {user_name},</h2>
            <p>We received a request to reset your password.</p>
            <p>Click the button below to reset your password:</p>
            <a href="{reset_url}" class="button">Reset Password</a>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #cc0000;">{reset_url}</p>
            <div class="warning">
                <strong>⚠️ This link will expire in 1 hour.</strong>
            </div>
            <p>If you did not request a password reset, please ignore this email and your password will remain unchanged.</p>
        </div>
        <div class="footer">
            <p>© 2025 VNPT Talent Hub. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return self.send_email(to, subject, body, html_body)


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or create singleton email service instance."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
