import json
import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import List
from fastapi import FastAPI, status, Request, Response
from pydantic import BaseModel
from src.core.config import settings
from twilio.twiml.voice_response import VoiceResponse, Gather
from src.core.agent import VoiceAgent
from src.nlp_engine.tts import get_tts_provider


logging.basicConfig(level=logging.INFO) # Or DEBUG for more detail
logger = logging.getLogger(__name__)

# Pydantic Models for Request/Response
class OrderItem(BaseModel):
    """Represents an item in the customer's order."""
    name: str
    quantity: int

class SubmitOrderRequest(BaseModel):
    """Request body for submitting an order."""
    customer_name: str
    items: List[OrderItem]

class SubmitOrderResponse(BaseModel):
    """Response body after submitting an order."""
    order_id: str
    estimated_time_of_arrival: str
    message: str

# FastAPI App Instance
app = FastAPI(
    title="Charco Chicken Order API",
    description="Backend API for the Syrian Arabic Voice Agent to submit orders.",
    version="1.0.0"
)

# Helper Functions for Order Storage
def get_orders_file_path() -> str:
    """Get the path to the orders storage file."""
    return settings.ORDERS_STORAGE_PATH

def load_orders() -> dict:
    """Load existing orders from the JSON file."""
    file_path = get_orders_file_path()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading orders file: {e}")
            return {}
    return {}

def save_orders(orders: dict) -> None:
    """Save orders dictionary to the JSON file."""
    file_path = get_orders_file_path()
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(orders, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error saving orders file: {e}")

def generate_order_id() -> str:
    """Generate a simple unique order ID (timestamp-based)."""
    return datetime.now().strftime("%Y%m%d%H%M%S%f")

def calculate_eta() -> str:
    """Calculate a mock ETA (e.g., 30 minutes from now)."""
    eta = datetime.now() + timedelta(minutes=30)
    return eta.isoformat()

# API Endpoint
@app.post("/submit-order", response_model=SubmitOrderResponse, status_code=status.HTTP_201_CREATED)
async def submit_order(order_request: SubmitOrderRequest):
    """
    Endpoint to submit a customer order.
    Accepts customer name and list of items.
    Returns order ID, ETA, and confirmation message.
    Stores the order in a JSON file.
    """
    print(f"Received order request: {order_request}")

    order_id = generate_order_id()
    eta = calculate_eta()

    order_data = {
        "order_id": order_id,
        "customer_name": order_request.customer_name,
        "items": [item.dict() for item in order_request.items], # Convert Pydantic models to dict
        "timestamp": datetime.now().isoformat(),
        "eta": eta
    }

    # Load existing orders
    orders = load_orders()
    # Store the new order
    orders[order_id] = order_data
    # Save updated orders back to file
    save_orders(orders)

    # Prepare response
    response = SubmitOrderResponse(
        order_id=order_id,
        estimated_time_of_arrival=eta,
        message=f"Thank you, {order_request.customer_name}. Your order (ID: {order_id}) has been received. Estimated arrival time is {eta}."
    )

    print(f"Order submitted successfully: {response.order_id}")
    return response

@app.get("/orders", response_model=dict)
async def get_all_orders():
    """Endpoint to retrieve all stored orders for debugging/testing."""
    return load_orders()

os.makedirs("data/sip_audio", exist_ok=True)

def generate_sip_tts_filename(call_sid: str) -> str:
    """Generate a unique filename for TTS audio related to a SIP call."""
    return f"data/sip_audio/response_{call_sid}_{uuid.uuid4().hex}.mp3"


@app.post("/sip/incoming_call", include_in_schema=False) # Hidden from docs
async def handle_incoming_sip_call(request: Request):
    """
    Webhook endpoint for Twilio to handle incoming SIP calls.
    Returns TwiML instructions.
    """
    logger.info("SIP Incoming call received.")
    form_data = await request.form()
    call_sid = form_data.get('CallSid', 'unknown_call')
    logger.info(f"Incoming call SID: {call_sid}")

    resp = VoiceResponse()
    greeting_text = "مرحباً بك في تشيكن تشاركو! شو اكدر أساعدك فيه اليوم؟"

    # Use TTS engine to generate audio
    try:
        tts_engine = get_tts_provider()
        greeting_audio_filename = generate_sip_tts_filename(call_sid)
        await tts_engine.synthesize(greeting_text, output_file_path=greeting_audio_filename)

        gather = Gather(
            input='speech',
            action='/sip/handle_speech',
            method='POST',
            language='ar-SY',
            timeout=3,
            speech_timeout='auto'
        )
        # Use Twilio TTS for greeting initially for simplicity
        gather.say(greeting_text, language='ar-SY')
        resp.append(gather)
    except Exception as e:
        logger.error(f"Error generating greeting TTS: {e}")
        resp.say("أعتذر، في مشكلة تقنية حالياً.", language='ar-SY')
        resp.hangup()
        return Response(content=str(resp), media_type="application/xml")

    # Fallback if no input
    resp.say("المعذرة, ما سمعت أي شيء. ودّع!", language='ar-SY')
    resp.hangup()

    logger.debug(f"Generated TwiML for incoming call: {resp}")
    return Response(content=str(resp), media_type="application/xml")

@app.post("/sip/handle_speech", include_in_schema=False)
async def handle_sip_speech(request: Request):
    """
    Webhook endpoint for Twilio to send transcribed user speech.
    Processes the intent and generates a response.
    """
    form_data = await request.form()
    user_speech = form_data.get('SpeechResult', '').strip()
    confidence = form_data.get('Confidence', '0')
    call_sid = form_data.get('CallSid', 'unknown_call')

    logger.info(f"User speech received (Call SID: {call_sid}): '{user_speech}' (Confidence: {confidence})")

    if not user_speech:
        logger.warning("Received empty speech result.")
        resp = VoiceResponse()
        resp.say("المعذرة, ما فهمت. شو اكدر أساعدك فيه؟", language='ar-SY')
        # Could re-prompt with Gather here
        resp.hangup()
        return Response(content=str(resp), media_type="application/xml")

    resp = VoiceResponse()

    try:
        # Integrate with the Core Agent
        agent = VoiceAgent()
        # Process intent
        agent_response_text = f"فهمت. قلت: {user_speech}. شكراً!"

        # Generate TTS Response
        tts_engine = get_tts_provider()
        response_audio_filename = generate_sip_tts_filename(call_sid)
        await tts_engine.synthesize(agent_response_text, output_file_path=response_audio_filename)

        # Fallback/Initial approach: Use Twilio TTS for response
        resp.say(agent_response_text, language='ar-SY') # Use Twilio TTS


    except Exception as e:
        logger.error(f"Error processing speech or generating response: {e}")
        resp.say("أعتذر، فيه مشكلة بمعالجة طلبك حالياً.", language='ar-SY')

    # End the call
    resp.hangup()
    logger.debug(f"Generated TwiML for speech response: {resp}")
    return Response(content=str(resp), media_type="application/xml")


if __name__ == "__main__":
    import uvicorn
    print("Starting Charco Chicken Order API...")
    uvicorn.run(
        "src.api.order_api:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )