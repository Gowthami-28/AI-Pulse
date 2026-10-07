import os
from dotenv import load_dotenv
import resend

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")


def send_email(email_content):
    params = {
        "from": "onboarding@resend.dev",
        "to": ["gowthamivanga@gmail.com"],
        "subject": "AI Pulse — Daily Learning Update",
        "text": email_content,
    }

    email = resend.Emails.send(params)

    return email
