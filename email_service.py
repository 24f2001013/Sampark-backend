import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
MAIL_FROM = os.getenv('MAIL_FROM', 'vohrasaakshi27@gmail.com')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

def send_email(to_email, subject, html_content):
    """Send email using SendGrid HTTP API"""
    print("\n" + "="*50)
    print("📧 EMAIL DEBUG INFO (SendGrid HTTP API):")
    print("="*50)
    print(f"SENDGRID_API_KEY: {'SET' if SENDGRID_API_KEY else 'NOT SET'} (length: {len(SENDGRID_API_KEY) if SENDGRID_API_KEY else 0})")
    print(f"MAIL_FROM: {MAIL_FROM}")
    print(f"TO: {to_email}")
    print("="*50 + "\n")
    
    if not SENDGRID_API_KEY:
        print("❌ ERROR: SENDGRID_API_KEY is not set!")
        print("Please add SENDGRID_API_KEY to your Railway environment variables")
        return False
    
    # SendGrid API endpoint
    url = "https://api.sendgrid.com/v3/mail/send"
    
    # Request headers
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Request body
    data = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": subject
            }
        ],
        "from": {"email": MAIL_FROM},
        "content": [
            {
                "type": "text/html",
                "value": html_content
            }
        ]
    }
    
    try:
        print(f"📧 Sending email via SendGrid HTTP API...")
        print(f"   API Endpoint: {url}")
        print(f"   From: {MAIL_FROM}")
        print(f"   To: {to_email}")
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code == 202:
            print(f"✅ Email accepted by SendGrid!")
            print(f"   Message ID: {response.headers.get('X-Message-Id', 'N/A')}")
            print(f"\n✅ EMAIL SENT SUCCESSFULLY to {to_email}\n")
            return True
        else:
            print(f"❌ SendGrid API Error!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ HTTP REQUEST FAILED!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
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
