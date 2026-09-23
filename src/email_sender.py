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



if __name__ == "__main__":
    test_content = """Hello from AI Pulse!

This is a test of the email sender.

The email sender is working correctly.
"""

    result = send_email(test_content)

    print("Email sent successfully!")
    print(result)    