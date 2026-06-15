from dotenv import load_dotenv
from twilio.rest import Client
import os

# Load environment variables
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_sms(to: str, message: str) -> str:
    """
    Send SMS using Twilio.
    Returns the message SID.
    """
    sms = _client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=to,
    )
    return sms.sid
