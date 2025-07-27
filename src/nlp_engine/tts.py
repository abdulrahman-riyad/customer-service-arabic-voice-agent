import os
from src.core.config import settings

class TTSProvider:
    """
    Abstract base class for TTS providers.
    Defines the interface that specific TTS implementations must follow.
    """
    async def synthesize(self, text: str, output_file_path: str = None) -> bytes:
        """
        Synthesize speech from text.

        Args:
            text (str): The text to convert to speech.
            output_file_path (str, optional): Path to save the audio file.
                                              If None, returns audio bytes.

        Returns:
            bytes: The raw audio data (e.g., MP3, WAV) if output_file_path is None.
                   Otherwise, saves to file and might return confirmation/path.
        """
        raise NotImplementedError("Subclasses must implement synthesize method.")

class ElevenLabsTTS(TTSProvider):
    """
    TTS implementation using ElevenLabs API.
    Requires ELEVEN_LABS_API_KEY in settings.
    Crucial: Find and configure a Syrian Arabic voice.
    """
    def __init__(self):
        self.api_key = settings.ELEVEN_LABS_API_KEY
        if not self.api_key:
            raise ValueError("ElevenLabs API key not found in settings.")
        try:
            import elevenlabs
            self.elevenlabs = elevenlabs
            import os
            os.environ['ELEVENLABS_API_KEY'] = self.api_key

            # Initialize the Client
            try:
                # Standard naming
                self.client = self.elevenlabs.ElevenLabs(api_key=self.api_key)
            except AttributeError:
                try:
                    # Class name
                    self.client = self.elevenlabs.Client(api_key=self.api_key)
                except AttributeError:
                    raise ImportError(
                        "Could not initialize ElevenLabs client. Check library documentation for client instantiation in v2.8.1.")

        except ImportError as e:
            raise ImportError(f"ElevenLabs library issue: {e}. Run 'pip install elevenlabs'.")

        self.voice_id_syrian = getattr(settings, 'ELEVEN_LABS_VOICE_ID_SYRIAN', None)
        if not self.voice_id_syrian:
            raise ValueError("Syrian Arabic Voice ID (ELEVEN_LABS_VOICE_ID_SYRIAN) not configured in settings.")

    async def synthesize(self, text: str, output_file_path: str = None) -> bytes:
        """
        Synthesize speech using ElevenLabs SDK v2.8.1.
        Tries common client methods for TTS generation.
        """
        try:
            audio_stream_or_generator = await asyncio.to_thread(
                self.client.text_to_speech.convert,
                text=text,
                voice_id=self.voice_id_syrian,
                model_id="eleven_multilingual_v2",
            )

            # Handle Streaming Response
            if hasattr(audio_stream_or_generator, '__iter__') and not isinstance(audio_stream_or_generator,
                                                                                 (bytes, bytearray)):
                audio_data = b"".join(chunk for chunk in audio_stream_or_generator)
            else:
                audio_data = audio_stream_or_generator

            # Save to file
            if output_file_path:
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                with open(output_file_path, 'wb') as f:
                    f.write(audio_data)
                print(f"TTS audio saved to {output_file_path}")

            return audio_data

        except AttributeError as ae1:
            print(f"Attempt 1 (client.text_to_speech.convert) failed: {ae1}")
            try:
                audio_stream_or_generator = await asyncio.to_thread(
                    self.client.tts,  # <--- Try this path
                    text=text,
                    voice_id=self.voice_id_syrian,  # Check parameter names
                    model_id="eleven_multilingual_v2",
                )

                # Handle Streaming Response
                if hasattr(audio_stream_or_generator, '__iter__') and not isinstance(audio_stream_or_generator,
                                                                                     (bytes, bytearray)):
                    audio_data = b"".join(chunk for chunk in audio_stream_or_generator)
                else:
                    audio_data = audio_stream_or_generator

                # Save to file
                if output_file_path:
                    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                    with open(output_file_path, 'wb') as f:
                        f.write(audio_data)
                    print(f"TTS audio saved to {output_file_path}")

                return audio_data

            except AttributeError as ae2:
                # Report detailed error
                print(f"Attempt 2 (client.tts) failed: {ae2}")
                print(
                    f"Final AttributeError in ElevenLabs TTS (v2.8.1) using client: Neither 'client.text_to_speech.convert' nor 'client.tts' seem to exist.")
                print("Error details from first attempt:")
                print(f"  - {ae1}")
                print("Error details from second attempt:")
                print(f"  - {ae2}")
                print(
                    "Please consult the official ElevenLabs Python SDK 2.8.1 documentation or GitHub examples for the EXACT method name and signature.")
                print(
                    "You might need to inspect the 'self.client' object attributes (e.g., dir(self.client)) to find the correct method.")
                raise
            except Exception as e_inner:
                print(f"Error during ElevenLabs TTS synthesis (v2.8.1) - Attempt 2 (client.tts): {e_inner}")
                raise

        except Exception as e_outer:
            print(
                f"Error during ElevenLabs TTS synthesis (v2.8.1) - Attempt 1 (client.text_to_speech.convert): {e_outer}")
            raise


def get_tts_provider(provider_name: str = None) -> TTSProvider:
    """
    Factory function to instantiate the correct TTS provider based on settings.

    Args:
        provider_name (str, optional): Explicitly specify provider ('elevenlabs', 'playht').
                                       If None, uses the one from settings.TTS_PROVIDER.

    Returns:
        TTSProvider: An instance of the selected TTS provider class.

    Raises:
        ValueError: If the provider name is invalid or configuration is missing.
    """
    if provider_name is None:
        provider_name = settings.TTS_PROVIDER.lower()

    if provider_name == "elevenlabs":
        return ElevenLabsTTS()
    else:
        raise ValueError(f"Unsupported or unspecified TTS provider: '{provider_name}'. "
                         f"Check settings.TTS_PROVIDER or provide a valid provider name.")

if __name__ == "__main__":
    import asyncio

    async def test_tts():
        try:
            tts_engine = get_tts_provider()
            test_text = "مرحباً! شو اكدر أساعدك فيه اليوم؟"
            print(f"Synthesizing text with {settings.TTS_PROVIDER}: {test_text}")

            audio_bytes = await tts_engine.synthesize(test_text)
            print(f"Received audio data: {len(audio_bytes)} bytes")

            output_path = "data/test_output.mp3"
            await tts_engine.synthesize(test_text, output_file_path=output_path)
            print(f"Audio saved to {output_path}")

        except Exception as e:
            print(f"Test failed: {e}")

    asyncio.run(test_tts())