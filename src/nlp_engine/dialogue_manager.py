import logging
from typing import Dict, List, Any, Optional
from src.nlp_engine.intent_classifier import (
    classify_intent,
    ORDER_INTENT,
    MENU_INTENT,
    GREETING_INTENT,
    GOODBYE_INTENT,
    COMPLAINT_INTENT,
    CONFIRMATION_INTENT,
    CLARIFICATION_INTENT,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DialogueState:
    """
    Represents the current state and context of the conversation.
    """
    def __init__(self):
        self.state = "greeting"
        self.order_items: List[Dict[str, Any]] = [] # Hold ordered items
        self.customer_name: Optional[str] = None
        self.pending_action: Optional[str] = None
        self.last_agent_response: str = ""
        self.conversation_history: List[Dict[str, str]] = []

    def update_state(self, new_state: str):
        """Updates the current dialogue state."""
        logger.debug(f"Dialogue state changing from '{self.state}' to '{new_state}'")
        self.state = new_state

    def add_order_item(self, item_name: str, quantity: int = 1):
        """Adds an item to the current order."""
        # Check for duplicates and increment quantity
        for item in self.order_items:
            if item['name'].lower() == item_name.lower():
                item['quantity'] += quantity
                logger.info(f"Updated quantity for '{item_name}' to {item['quantity']}")
                return
        # If not found, add new item
        self.order_items.append({'name': item_name, 'quantity': quantity})
        logger.info(f"Added item to order: {item_name} x {quantity}")

    def clear_order(self):
        """Clears the current order items."""
        self.order_items.clear()
        logger.info("Order items cleared.")

    def set_pending_action(self, action: str):
        """Sets an action that the agent is waiting for user confirmation on."""
        self.pending_action = action
        logger.debug(f"Pending action set: {action}")

    def clear_pending_action(self):
        """Clears the pending action."""
        self.pending_action = None
        logger.debug("Pending action cleared.")

    def add_to_history(self, user_input: str, agent_response: str):
        """Adds the turn to the conversation history."""
        self.conversation_history.append({'user': user_input, 'agent': agent_response})


class DialogueManager:
    """
    Manages the conversation flow and generates agent responses.
    """

    def __init__(self):
        """
        Initializes the Dialogue Manager.
        """
        logger.info("Initializing Dialogue Manager...")
        logger.info("Dialogue Manager initialized.")

    def get_response(self, user_input: str, dialogue_state: DialogueState) -> str:
        """
        Generates the agent's response based on user input and current dialogue state.

        Args:
            user_input (str): The latest input from the user.
            dialogue_state (DialogueState): The current state/context of the conversation.

        Returns:
            str: The agent's response text.
        """
        logger.info(f"Generating response for input: '{user_input}' in state: '{dialogue_state.state}'")
        # Classify the user's intent
        intent = classify_intent(user_input)
        logger.debug(f"Classified intent: {intent}")

        # Generate response based on intent
        response_text = self._generate_response_for_intent(intent, user_input, dialogue_state)

        # Record the interaction
        dialogue_state.add_to_history(user_input, response_text)
        dialogue_state.last_agent_response = response_text

        return response_text

    def _generate_response_for_intent(self, intent: str, user_input: str, state: DialogueState) -> str:
        """
        Internal method to generate response based on intent and state.
        This is where the core dialogue logic resides.
        """
        # Handle Greeting
        if intent == GREETING_INTENT and state.state == "greeting":
            state.update_state("awaiting_request") # Move to next state
            return "مرحباً بك في تشيكن تشاركو! شو اقدر أساعدك فيه اليوم؟"

        # Handle Menu Inquiry
        elif intent == MENU_INTENT:
            return "في اليوم مشاوي مشكلة و شاورما دجاج و ساندويش فرانكي. شو تحب تطلب؟"

        # Handle Ordering
        elif intent == ORDER_INTENT:
            items_mentioned = []
            if "shawarma" in user_input.lower() or "شاورما" in user_input.lower():
                items_mentioned.append("شاورما دجاج")
            if "chicken" in user_input.lower() or "مشاوي" in user_input.lower():
                items_mentioned.append("مشاوي مشكلة")
            if "sandwich" in user_input.lower() or "ساندويش" in user_input.lower() or "frankie" in user_input.lower():
                 items_mentioned.append("ساندويش فرانكي")

            if items_mentioned:
                added_items = []
                for item in items_mentioned:
                    state.add_order_item(item, 1) # Assume quantity 1
                    added_items.append(item)
                state.update_state("order_in_progress")
                # List added items
                items_str = ", ".join(added_items)
                return f"تمام، حطيت {items_str} بالطلب. شي تاني؟"
            else:
                state.update_state("order_in_progress")
                return "حاضر، شو طلبك؟"

        # Order Confirmation
        elif intent == CONFIRMATION_INTENT and state.state == "order_in_progress":
             if state.order_items:
                 # Asking for name before confirming the order
                 state.update_state("awaiting_name")
                 return "تمام. شو اسمك عشان نسجل الطلب؟"
             else:
                 return "ما في شي بالطلب حالياً. شو تحب تسوي طلب؟"

        # Handle Providing Name
        elif state.state == "awaiting_name":
            state.customer_name = user_input.strip()
            state.update_state("order_summary")
            # Transition to summary
            items_list = ', '.join([f"{item['name']} x{item['quantity']}" for item in state.order_items])
            return f"تمام {state.customer_name}، طلبك يحتوي على: {items_list}. صح هذا؟"

        # Final Confirmation
        elif intent == CONFIRMATION_INTENT and state.state == "order_summary":
            state.update_state("order_placed")
            return "شكراً لطلبك! طلبك قيد التنفيذ والوقت المتوقع للوصول هو 30 دقيقة."

        # Handle Goodbye
        elif intent == GOODBYE_INTENT:
            # Clear context for next call
            state.update_state("greeting")
            state.clear_order()
            state.customer_name = None
            state.clear_pending_action()
            return "شكراً على اتصالك! سلام!"

        # Handle Complaint
        elif intent == COMPLAINT_INTENT:
            return "المعذرة على الإزعاج. شو المشكلة تحديداً؟"

        # Handle Clarification Requests
        elif intent == CLARIFICATION_INTENT:
            # Ask for clarification
            if state.last_agent_response:
                return f"قلت: {state.last_agent_response}. صح هذا؟"
            else:
                return "أعتذر، شو تحتاج توضحه؟"

        # Check state for specific fallbacks
        else:
            if state.state == "greeting":
                return "مرحباً! شو اكدر أساعدك فيه؟"
            elif state.state == "awaiting_request":
                return "أعتذر، ما فهمت. شو اكدر أساعدك فيه؟"
            elif state.state == "order_in_progress":
                return "أعتذر، ما فهمت. شو الشيء تحب تضيفه للطلب؟"
            elif state.state == "awaiting_name":
                 return "أعتذر، شو اسمك؟"
            elif state.state == "order_summary":
                 return "أعتذر، طلبك هو {items_list}. صح هذا؟"
            else:
                return "أعتذر، ما فهمت. شو اكدر أساعدك فيه؟"


if __name__ == "__main__":
    dm = DialogueManager()
    ds = DialogueState()

    # Dummy conversation
    conversation_turns = [
        "مرحباً",
        "شو في اليوم؟",
        "شاورما دجاج",
        "أكيد",
        "اسمه أحمد",
        "أكيد",
        "ودّع"
    ]

    for turn in conversation_turns:
        response = dm.get_response(turn, ds)
        print(f"User: {turn}")
        print(f"Agent: {response}")
        print("---")