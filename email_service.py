import os
import requests
from dotenv import load_dotenv

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
MAIL_FROM = os.getenv("MAIL_FROM")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

SENDGRID_URL = "https://api.sendgrid.com/v3/mail/send"


def send_email(to_email, subject, html_content):
    if not SENDGRID_API_KEY:
        print("❌ SENDGRID_API_KEY not set")
        return False

    if not MAIL_FROM:
        print("❌ MAIL_FROM not set or not verified in SendGrid")
        return False

    payload = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": subject
            }
        ],
        "from": {
            "email": MAIL_FROM
        },
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

    try:
        response = requests.post(
            SENDGRID_URL,
            headers=headers,
            json=payload,
            timeout=15
        )

        if response.status_code in (200, 202):
            print(f"✅ Email sent to {to_email}")
            return True

        print("❌ SendGrid error")
        print("Status:", response.status_code)
        print("Response:", response.text)
        return False

    except requests.RequestException as e:
        print("❌ Network error while sending email:", e)
        return False
