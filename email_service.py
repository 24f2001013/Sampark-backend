import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_FROM = os.getenv('MAIL_FROM', MAIL_USERNAME)
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

def send_email(to_email, subject, html_content):
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = MAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_credentials_email(to_email, registration_number, password):
    """Send login credentials to newly approved user"""
    subject = "Welcome to Sampark - Your Login Credentials"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .credentials {{ background: white; padding: 20px; border-radius: 8px; 
                           margin: 20px 0; border-left: 4px solid #667eea; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: #667eea; 
                   color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Welcome to Sampark!</h1>
            </div>
            <div class="content">
                <p>Congratulations! Your registration has been approved by the admin.</p>
                
                <div class="credentials">
                    <h3>Your Login Credentials:</h3>
                    <p><strong>Registration Number:</strong> {registration_number}</p>
                    <p><strong>Password:</strong> {password}</p>
                </div>
                
                <p><strong>⚠️ Important:</strong> Please save these credentials securely. 
                   We recommend changing your password after your first login.</p>
                
                <p>You can now:</p>
                <ul>
                    <li>✅ Login to your personal portal</li>
                    <li>✏️ Update your profile and interests</li>
                    <li>🤝 Connect with other participants via NFC</li>
                    <li>📊 View your connections and analytics</li>
                </ul>
                
                <a href="{FRONTEND_URL}/login" class="btn">Login Now</a>
                
                <div class="footer">
                    <p>If you have any questions, please contact the Sampark team.</p>
                    <p>&copy; 2024 Sampark Event Portal</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, html_content)

def send_registration_confirmation(to_email, name, registration_number):
    """Send confirmation email after registration submission"""
    subject = "Registration Received - Sampark Event"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #667eea; color: white; padding: 30px; 
                      text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Registration Received!</h1>
            </div>
            <div class="content">
                <p>Dear {name},</p>
                <p>Thank you for registering for Sampark!</p>
                <p><strong>Your Registration Number:</strong> {registration_number}</p>
                <p>Your registration is currently under review by our admin team. 
                   You will receive your login credentials via email once your registration is approved.</p>
                <p>This typically takes 1-2 business days.</p>
                <p>Best regards,<br>Sampark Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, html_content)