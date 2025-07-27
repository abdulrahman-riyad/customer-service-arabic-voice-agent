import logging
from twilio.rest import Client
from src.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SIPClient:
    """
    Handles SIP/VoIP interactions, specifically using Twilio Programmable Voice.
    This class sets up the connection and handles incoming/outgoing calls via webhooks.
    NOTE: This requires a publicly accessible URL for webhooks (use ngrok for local dev).
    """

    def __init__(self):
        """
        Initializes the Twilio client using credentials from settings.
        """
        logger.info("Initializing SIP Client (Twilio)...")
        if settings.SIP_PROVIDER.lower() != 'twilio':
            raise ValueError("SIP Provider in settings is not 'twilio'. This client is for Twilio.")

        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER

        if not all([self.account_sid, self.auth_token, self.phone_number]):
            raise ValueError("Twilio credentials (Account SID, Auth Token, Phone Number) are missing in settings.")

        # Initialize the Twilio REST client
        self.twilio_client = Client(self.account_sid, self.auth_token)
        logger.info("Twilio SIP Client initialized.")

    def setup_incoming_call_webhook(self, webhook_url: str):
        """
        Configures the Twilio phone number to point its incoming call webhook to the given URL.
        This tells Twilio where to send HTTP requests when a call comes in.

        Args:
            webhook_url (str): The publicly accessible URL for your call handling endpoint.
                               Example: "https://your-ngrok-url.ngrok.io/incoming_call"
        """
        try:
            # Update the phone number's voice webhook URL
            self.twilio_client.incoming_phone_numbers.list(phone_number=self.phone_number)[0].update(
                voice_url=webhook_url
            )
            logger.info(f"Incoming call webhook configured for {self.phone_number} -> {webhook_url}")
        except IndexError:
            logger.error(f"Twilio phone number {self.phone_number} not found in your account.")
            raise ValueError(f"Phone number {self.phone_number} not associated with this Twilio account.")
        except Exception as e:
            logger.error(f"Error setting up incoming call webhook: {e}")
            raise