import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define possible intent
ORDER_INTENT = "order"
MENU_INTENT = "menu"
GREETING_INTENT = "greeting"
GOODBYE_INTENT = "goodbye"
COMPLAINT_INTENT = "complaint"
CONFIRMATION_INTENT = "confirmation"
CLARIFICATION_INTENT = "clarification"
FALLBACK_INTENT = "fallback"

# Map keywords/phrases to intents
INTENT_KEYWORDS = {
    MENU_INTENT: [
        "menu", "القائمة", "شو في", "شو فيه اليوم", "available", "today's special",
        "special", "dish", "what do you have"
    ],
    ORDER_INTENT: [
        "order", "طلب", "أ хочу", "I want", "I'd like", "give me", "get",
        "shawarma", "شاورما", "chicken", "مشاوي", "grilled", "sandwich", "ساندويش",
        "بيتزا", "pizza", "بطاطا", "fries", "pepsi", "cola", "مشروب"
    ],
    GREETING_INTENT: [
        "hello", "hi", "hey", "مرحباً", "سلام", "bonjour", "здравствуйте"
    ],
    GOODBYE_INTENT: [
        "bye", "goodbye", "ودّع", "شكراً", "thanks", "thank you", "that's all",
        "تمام", "خلاص", "finish", "done", "exit"
    ],
    COMPLAINT_INTENT: [
        "problem", "issue", "complaint", "wrong", "خطأ", "مشكلة", "غير صحيح",
        "late", "متأخر", "cold", "بارد", "bad", "سيء"
    ],
    CONFIRMATION_INTENT: [
        "yes", "أكيد", "sure", "correct", "right", "نعم", "positive", "confirm", "exact"
    ],
    CLARIFICATION_INTENT: [
        "what", "ماذا", "repeat", "كرر", "again", "slow", "بطيء", "clear", "واضح",
        "meaning", "معنى", "explain", "اشرح", "how", "كيف", "كم", "how much"
    ]
}

def classify_intent(user_input: str) -> str:
    """
    Classifies the user's intent based on keywords in the input text.

    Args:
        user_input (str): The text input from the user (transcribed speech).

    Returns:
        str: The detected intent (one of the defined intent constants).
             Returns FALLBACK_INTENT if no intent is confidently detected.
    """
    logger.info(f"Classifying intent for input: '{user_input}'")
    input_lower = user_input.lower().strip()

    # Simple Keyword Matching
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in input_lower for keyword in keywords):
            logger.info(f"Intent classified as: {intent}")
            return intent

    # Fallback
    logger.info("No specific intent keywords matched. Returning FALLBACK_INTENT.")
    return FALLBACK_INTENT


if __name__ == "__main__":
    test_inputs = [
        "مرحباً, شو في القائمة اليوم؟",
        "أ хочу شاورما دجاج و مشروب.",
        "ودّع, شكراً!",
        "فيه مشكلة بالطلب, وصل بارد.",
        "كم سعر الشاورما؟",
        "أكيد, هذا صحيح.",
        "xyz unknown input"
    ]

    for inp in test_inputs:
        intent = classify_intent(inp)
        print(f"Input: '{inp}' -> Intent: {intent}")