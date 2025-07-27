import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Configuration settings for the Syrian Arabic Voice Agent.
    Uses environment variables for sensitive data, with defaults or None if not found.
    """

    # SIP Configuration
    SIP_PROVIDER = os.getenv("SIP_PROVIDER", "twilio")
    SIP_SERVER = os.getenv("SIP_SERVER")
    SIP_USERNAME = os.getenv("SIP_USERNAME")
    SIP_PASSWORD = os.getenv("SIP_PASSWORD")
    SIP_PORT = int(os.getenv("SIP_PORT", 5060))
    # Twilio
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

    # STT Configuration
    # Whisper
    STT_PROVIDER = os.getenv("STT_PROVIDER", "whisper")
    # Google Cloud Speech-to-Text
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # TTS Configuration
    # ElevenLabs
    TTS_PROVIDER = os.getenv("TTS_PROVIDER", "elevenlabs")
    ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
    # Syrian Arabic voice ID
    ELEVEN_LABS_VOICE_ID_SYRIAN = os.getenv("ELEVEN_LABS_VOICE_ID_SYRIAN")
    PLAY_HT_USER_ID = os.getenv("PLAY_HT_USER_ID")
    PLAY_HT_API_KEY = os.getenv("PLAY_HT_API_KEY")

    # API Configuration
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", 8000))

    # UI Configuration
    UI_HOST = os.getenv("UI_HOST", "127.0.0.1")
    UI_PORT = int(os.getenv("UI_PORT", 8501)) # Streamlit port

    # Backend Order API Storage
    ORDERS_STORAGE_PATH = os.getenv("ORDERS_STORAGE_PATH", "data/orders.json")

settings = Settings()