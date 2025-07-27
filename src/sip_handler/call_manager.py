import logging
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallContext:
    """
    Holds context-specific information for a single SIP call.
    This can include call SID, caller number, agent state, order details, etc.
    """
    def __init__(self, call_sid: str, from_number: str, to_number: str):
        self.call_sid: str = call_sid
        self.from_number: str = from_number
        self.to_number: str = to_number
        self.is_active: bool = True
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def end_call(self):
        """Marks the call as ended and records the end time."""
        self.is_active = False
        logger.info(f"Call {self.call_sid} marked as ended.")

    def __repr__(self):
        return (f"<CallContext call_sid={self.call_sid}, "
                f"from={self.from_number}, to={self.to_number}, "
                f"is_active={self.is_active}>")


class CallManager:
    """
    Manages active SIP calls and their associated contexts.
    Provides methods to create, retrieve, update, and delete call contexts.
    This is useful for maintaining state across webhook requests for the same call.
    """
    def __init__(self):
        logger.info("Initializing Call Manager...")
        self._active_calls: Dict[str, CallContext] = {}
        logger.info("Call Manager initialized.")

    def create_call_context(self, call_sid: str, from_number: str, to_number: str) -> CallContext:
        """
        Creates a new CallContext and stores it.

        Args:
            call_sid (str): Unique identifier for the call from Twilio.
            from_number (str): Caller's phone number.
            to_number (str): Callee's phone number (your Twilio number).

        Returns:
            CallContext: The newly created call context.
        """
        if call_sid in self._active_calls:
            logger.warning(f"Call context for SID {call_sid} already exists. Overwriting.")

        call_context = CallContext(call_sid, from_number, to_number)
        self._active_calls[call_sid] = call_context
        logger.info(f"Created new call context: {call_context}")
        return call_context

    def get_call_context(self, call_sid: str) -> Optional[CallContext]:
        """
        Retrieves an existing CallContext by its SID.

        Args:
            call_sid (str): The unique call identifier.

        Returns:
            CallContext: The context if found, otherwise None.
        """
        return self._active_calls.get(call_sid)

    def update_call_context(self, call_sid: str, **kwargs):
        """
        Updates specific attributes of a CallContext.
        (This is a simple example; direct attribute access on the object is often easier).

        Args:
            call_sid (str): The call SID.
            **kwargs: Key-value pairs of attributes to update.
        """
        call_context = self.get_call_context(call_sid)
        if call_context:
            for key, value in kwargs.items():
                if hasattr(call_context, key):
                    setattr(call_context, key, value)
                    logger.debug(f"Updated {call_sid}.{key} to {value}")
                else:
                    logger.warning(f"CallContext has no attribute '{key}' to update.")
        else:
            logger.warning(f"Attempted to update non-existent call context for SID {call_sid}")

    def end_call(self, call_sid: str):
        """
        Marks a call as ended and removes its context.

        Args:
            call_sid (str): The unique call identifier.
        """
        call_context = self.get_call_context(call_sid)
        if call_context:
            call_context.end_call()
            del self._active_calls[call_sid]
            logger.info(f"Ended and removed call context for SID {call_sid}")
        else:
            logger.warning(f"Attempted to end non-existent call context for SID {call_sid}")

    def get_active_call_count(self) -> int:
        """Returns the number of currently active calls."""
        return len(self._active_calls)

    def list_active_calls(self) -> Dict[str, CallContext]:
        """Returns a dictionary of all active call contexts."""
        return self._active_calls.copy()

call_manager = CallManager()