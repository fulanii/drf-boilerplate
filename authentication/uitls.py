import os
import resend
import secrets
from dotenv import load_dotenv
from resend.exceptions import ResendError


# load .env file
load_dotenv()


def generate_strong_6_digit_number():
    """Generates a cryptographically strong random 6-digit number as a string."""

    random_int = secrets.randbelow(1_000_000)

    return int(f"{random_int:06d}")


def send_verification_email(code: str, email: str) -> bool:
    """
    Send verification code to user email
    returns True if sucessful False otherwise
    """

    try:
        resend.api_key = os.getenv("RESEND_API_KEY")

        from_name = os.getenv("FROM_NAME")
        from_email = os.getenv("FROM_EMAIL")

        params: resend.Emails.SendParams = {
            "from": f"{from_name} <{from_email}>",
            "to": [f"{email}"],
            "subject": "Verification Code",
            "html": f"Here is the verification code you requested: {code}",
        }

        email = resend.Emails.send(params)

        return True

    except ResendError:
        return False
