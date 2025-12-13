import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import socket
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 465))  # Changed default to 465
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_FROM = os.getenv('MAIL_FROM', MAIL_USERNAME)
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

def send_email(to_email, subject, html_content):
    """Send email using SMTP with support for both port 587 (TLS) and 465 (SSL)"""
    print("\n" + "="*50)
    print("📧 EMAIL DEBUG INFO:")
    print("="*50)
    print(f"MAIL_SERVER: {MAIL_SERVER}")
    print(f"MAIL_PORT: {MAIL_PORT}")
    print(f"MAIL_USERNAME: {MAIL_USERNAME}")
    print(f"MAIL_PASSWORD: {'SET' if MAIL_PASSWORD else 'NOT SET'} (length: {len(MAIL_PASSWORD) if MAIL_PASSWORD else 0})")
    print(f"MAIL_FROM: {MAIL_FROM}")
    print(f"TO: {to_email}")
    print("="*50 + "\n")
    
    if not MAIL_USERNAME:
        print("❌ ERROR: MAIL_USERNAME is not set!")
        return False
    
    if not MAIL_PASSWORD:
        print("❌ ERROR: MAIL_PASSWORD is not set!")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = MAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        print(f"📧 Connecting to {MAIL_SERVER}:{MAIL_PORT}...")
        
        # Use SMTP_SSL for port 465, use SMTP with STARTTLS for port 587
        if MAIL_PORT == 465:
            # Port 465 uses SSL from the start
            with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT, timeout=30) as server:
                print(f"✅ Connected to SMTP server with SSL")
                
                print(f"📧 Logging in as {MAIL_USERNAME}...")
                server.login(MAIL_USERNAME, MAIL_PASSWORD)
                print(f"✅ Login successful")
                
                print(f"📧 Sending message...")
                server.send_message(msg)
                print(f"✅ Message sent")
        else:
            # Port 587 uses STARTTLS
            with smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=30) as server:
                print(f"✅ Connected to SMTP server")
                
                print(f"📧 Starting TLS...")
                server.starttls()
                print(f"✅ TLS started")
                
                print(f"📧 Logging in as {MAIL_USERNAME}...")
                server.login(MAIL_USERNAME, MAIL_PASSWORD)
                print(f"✅ Login successful")
                
                print(f"📧 Sending message...")
                server.send_message(msg)
                print(f"✅ Message sent")
        
        print(f"\n✅ EMAIL SENT SUCCESSFULLY to {to_email}\n")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ SMTP AUTHENTICATION FAILED!")
        print(f"Error: {e}")
        print(f"This usually means:")
        print(f"  1. Wrong username or password")
        print(f"  2. Not using App Password (must be 16 chars)")
        print(f"  3. 2-Step Verification not enabled\n")
        return False
        
    except socket.gaierror as e:
        print(f"\n❌ DNS RESOLUTION FAILED!")
        print(f"Error: {e}")
        print(f"Cannot resolve hostname: {MAIL_SERVER}")
        print(f"Check your MAIL_SERVER setting")
        print(f"Consider using port 465 instead of 587\n")
        return False
        
    except socket.timeout as e:
        print(f"\n❌ CONNECTION TIMEOUT!")
        print(f"Error: {e}")
        print(f"Cannot connect to {MAIL_SERVER}:{MAIL_PORT}")
        print(f"The server might be blocking this port\n")
        return False
    
    except ConnectionRefusedError as e:
        print(f"\n❌ CONNECTION REFUSED!")
        print(f"Error: {e}")
        print(f"The server refused connection to {MAIL_SERVER}:{MAIL_PORT}")
        print(f"Try switching to port 465 (SSL) or 587 (TLS)\n")
        return False
        
    except Exception as e:
        print(f"\n❌ EMAIL FAILED!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        import traceback
        print("\nFull Traceback:")
        traceback.print_exc()
        print()
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
    
    result = send_email(to_email, subject, html_content)
    
    # Log the result
    if result:
        print(f"✅ Credentials email sent successfully to {to_email}")
    else:
        print(f"❌ Failed to send credentials email to {to_email}")
    
    return result


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




