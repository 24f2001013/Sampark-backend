import os
import requests
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
MAIL_FROM = os.getenv("MAIL_FROM")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

SENDGRID_URL = "https://api.sendgrid.com/v3/mail/send"


def send_email(to_email, subject, html_content):
    payload = {
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

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        SENDGRID_URL,
        headers=headers,
        json=payload,
        timeout=15
    )

    return response.status_code in (200, 202)


# ============================
# REQUIRED WRAPPER FUNCTIONS
# ============================

def send_credentials_email(user_email, username, password):
    html = f"""
    <h2>Your Sampark Admin Account</h2>
    <p><b>Username:</b> {username}</p>
    <p><b>Password:</b> {password}</p>
    <p>Login here: <a href="{FRONTEND_URL}">{FRONTEND_URL}</a></p>
    """
    return send_email(user_email, "Your Sampark Login Credentials", html)


def send_registration_confirmation(user_email):
    html = """
    <h2>Registration Successful</h2>
    <p>Your account has been created successfully.</p>
    """
    return send_email(user_email, "Registration Successful", html)
