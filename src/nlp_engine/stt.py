import os
from src.core.config import settings

class STTProvider:
    """
    Abstract base class for STT providers.
    Defines the interface that specific STT implementations must follow.
    """
    async def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribe speech from an audio file.

        Args:
            audio_file_path (str): Path to the audio file (WAV, MP3, etc.).

        Returns:
            str: The transcribed text.
        """
        raise NotImplementedError("Subclasses must implement transcribe method.")

class WhisperSTT(STTProvider):
    """
    STT implementation using OpenAI Whisper.
    Requires 'whisper' library installed.
    Whisper is good for local processing and supports many languages.
    """
    def __init__(self):
        try:
            import whisper
            self.whisper = whisper
            # Load the base model
            print("Loading Whisper model (base)...")
            self.model = self.whisper.load_model("base")
            print("Whisper model loaded.")
        except ImportError:
            raise ImportError("Whisper library not installed. Run 'pip install openai-whisper'.")

    async def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribe audio using Whisper.
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        try:
            result = await asyncio.to_thread(
                self.model.transcribe, # The function to run in thread
                audio_file_path, # Argument to the function
                language='ar'
            )
            transcription = result.get("text", "").strip()
            print(f"Whisper Transcription: {transcription}")
            return transcription

        except Exception as e:
            print(f"Error during Whisper STT transcription: {e}")
            raise

def get_stt_provider(provider_name: str = None) -> STTProvider:
    """
    Factory function to instantiate the correct STT provider based on settings.

    Args:
        provider_name (str, optional): Explicitly specify provider ('whisper', 'google', 'azure').
                                       If None, uses the one from settings.STT_PROVIDER.

    Returns:
        STTProvider: An instance of the selected STT provider class.

    Raises:
        ValueError: If the provider name is invalid or configuration is missing.
    """
    if provider_name is None:
        provider_name = settings.STT_PROVIDER.lower()

    if provider_name == "whisper":
        return WhisperSTT()
    else:
        raise ValueError(f"Unsupported or unspecified STT provider: '{provider_name}'. "
                         f"Check settings.STT_PROVIDER or provide a valid provider name.")


if __name__ == "__main__":
    import asyncio

    async def test_stt():
        try:
            stt_engine = get_stt_provider()
            test_audio_path = "data/test_input_arabic.wav" # Example path

            if not os.path.exists(test_audio_path):
                 print(f"Warning: Test audio file '{test_audio_path}' not found. Please provide a sample audio file.")
                 return

            print(f"Transcribing audio file: {test_audio_path} using {settings.STT_PROVIDER}")

            transcription = await stt_engine.transcribe(test_audio_path)
            print(f"Transcribed Text: {transcription}")

        except Exception as e:
            print(f"Test failed: {e}")

    asyncio.run(test_stt())