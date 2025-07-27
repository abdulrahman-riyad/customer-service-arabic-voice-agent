import os
import asyncio
import logging
from src.nlp_engine.stt import get_stt_provider
from src.nlp_engine.tts import get_tts_provider


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceAgent:
    """
    Central orchestrator for the Syrian Arabic Voice Agent.
    Manages the flow: Audio Input -> STT -> NLP -> TTS -> Audio Output
    Also handles interaction with the backend API.
    """

    def __init__(self):
        """
        Initializes the agent with configured STT and TTS providers.
        """
        logger.info("Initializing Voice Agent...")
        self.stt_provider = get_stt_provider()
        self.tts_provider = get_tts_provider()
        logger.info("Voice Agent initialized.")

    async def process_audio_input(self, audio_file_path: str) -> str:
        """
        Takes an audio file path, performs STT, and returns the transcription.

        Args:
            audio_file_path (str): Path to the input audio file.

        Returns:
            str: The transcribed text.
        """
        logger.info(f"Processing audio input from: {audio_file_path}")
        try:
            transcription = await self.stt_provider.transcribe(audio_file_path)
            logger.info(f"Transcription: {transcription}")
            return transcription
        except Exception as e:
            logger.error(f"Error in STT processing: {e}")
            return "[STT_ERROR]"

    async def generate_audio_response(self, text_response: str, output_audio_path: str) -> bool:
        """
        Takes text, performs TTS, and saves the audio to a file.

        Args:
            text_response (str): The text for the agent's response.
            output_audio_path (str): Path where the output audio file will be saved.

        Returns:
            bool: True if successful, False otherwise.
        """
        logger.info(f"Generating audio response for: {text_response}")
        try:
            await self.tts_provider.synthesize(text_response, output_file_path=output_audio_path)
            logger.info(f"Audio response saved to: {output_audio_path}")
            return True
        except Exception as e:
            logger.error(f"Error in TTS generation: {e}")
            return False

    async def handle_intent(self, user_input: str) -> str:
        """
        Placeholder for intent classification and dialogue management.
        Currently simulates simple responses.

        Args:
            user_input (str): The transcribed text from the user.

        Returns:
            str: The agent's text response.
        """
        # Simple Simulation
        logger.info(f"Handling user input: {user_input}")
        user_input_lower = user_input.lower()

        if "menu" in user_input_lower or "شو في اليوم" in user_input_lower:
             return "في اليوم مشاوي مشكلة و شاورما دجاج. شو تحب تسوي طلب؟"
        elif "shawarma" in user_input_lower or "شاورما" in user_input_lower:
            return "تمام، حطيت شاورما دجاج بالطلب. شي تاني؟"
        elif "chicken" in user_input_lower or "مشاوي" in user_input_lower:
             return "أكيد، مشاوي مشكلة ممتازة. شي تاني؟"
        elif "order" in user_input_lower or "طلب" in user_input_lower or "yes" in user_input_lower or "أكيد" in user_input_lower:
            return "حاضر، شو طلبك؟" # Simplified prompt
        elif "name" in user_input_lower or "اسم" in user_input_lower:
             return "تمام، شكراً. شو تحب تسوي طلب؟"
        elif "bye" in user_input_lower or "تمام" in user_input_lower or "شكراً" in user_input_lower or "خلاص" in user_input_lower:
            return "شكراً لطلبك! طلبك قيد التنفيذ والوقت المتوقع للوصول هو 30 دقيقة."
        else:
            # Default fallback
            return "أعتذر، ما فهمت. شو اكدر أساعدك فيه؟"

    async def submit_order_to_backend(self, customer_name: str, items: list) -> bool:
        """
        Submits the collected order details to the backend API.
        """
        logger.info("Submitting order to backend API...")

        # Import the module containing the FastAPI app and models
        try:
            import src.api.order_api as order_api_module
            from fastapi.testclient import TestClient
            # Import the specific Pydantic models from the module
            SubmitOrderRequest = order_api_module.SubmitOrderRequest
            OrderItem = order_api_module.OrderItem
        except ImportError as e:
            logger.error(f"Import error when trying to set up API client/models: {e}")
            return False
        except AttributeError as e:
            logger.error(f"Attribute error when accessing models: {e}")
            return False

        # Prepare data according to the API model
        order_items = [OrderItem(name=item['name'], quantity=item.get('quantity', 1)) for item in items]
        order_request = SubmitOrderRequest(customer_name=customer_name, items=order_items)

        try:
            # Create a test client using the app instance
            client = TestClient(order_api_module.app)

            # Make the POST request
            response = client.post("/submit-order", json=order_request.dict())

            if response.status_code == 201:
                response_data = response.json()
                logger.info(f"Order submitted successfully. Order ID: {response_data.get('order_id')}")
                return True
            else:
                logger.error(f"Failed to submit order. Status: {response.status_code}, Detail: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Exception during order submission: {e}")
            return False


# Example Usage
# This demonstrates the core logic without SIP integration.
async def run_test_flow():
    """
    Example of how the agent components work together.
    This is NOT the full SIP call handler, just a test sequence.
    """
    agent = VoiceAgent()

    # Simulate receiving audio input (e.g., from SIP or UI upload) ---
    test_audio_path = "data/test_audio/test_input_arabic.wav" # Path to test audio
    if not os.path.exists(test_audio_path):
        logger.warning(f"Test audio file not found: {test_audio_path}. Skipping test flow.")
        return

    # Process audio input (STT)
    user_text = await agent.process_audio_input(test_audio_path)
    print(f"User said: {user_text}")

    # Handle intent and generate response text
    agent_response_text = await agent.handle_intent(user_text)
    print(f"Agent response text: {agent_response_text}")

    # Generate audio output (TTS)
    os.makedirs("data/agent_output", exist_ok=True)
    output_audio_path = "data/agent_output/test_agent_response.mp3"
    success = await agent.generate_audio_response(agent_response_text, output_audio_path)

    if success:
        print(f"Agent audio response generated at: {output_audio_path}")
    else:
        print("Failed to generate agent audio response.")

if __name__ == "__main__":
    asyncio.run(run_test_flow())
