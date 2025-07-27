import logging
import re
from typing import List, Dict, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Menu Items
MENU_ITEMS = [
    {"name_ar": "شاورما دجاج", "name_en": "Chicken Shawarma", "id": "shawarma_chicken"},
    {"name_ar": "مشاوي مشكلة", "name_en": "Mixed Grill", "id": "mixed_grill"},
    {"name_ar": "ساندويش فرانكي", "name_en": "Frankie Sandwich", "id": "frankie_sandwich"},
    {"name_ar": "مشروب", "name_en": "Ayran", "id": "ayran"},
    {"name_ar": "بيبسي", "name_en": "Pepsi", "id": "pepsi"},
    {"name_ar": "برجر دجاج", "name_en": "Chicken Burger", "id": "chicken_burger"},
]

def extract_menu_items(text: str) -> List[Dict[str, Any]]:
    """
    Extracts potential menu items mentioned in the text using simple keyword matching.

    Args:
        text (str): The user's input text.

    Returns:
        List[Dict]: A list of dictionaries, each containing potential item info.
                    Example: [{'name_ar': 'شاورما دجاج', 'id': 'shawarma_chicken', 'matched_text': ' Shawarma'}]
    """
    logger.debug(f"Extracting menu items from: '{text}'")
    found_items = []
    text_lower = text.lower()

    for item in MENU_ITEMS:
        name_ar = item['name_ar']
        name_en = item['name_en']
        item_id = item['id']

        # Check for Arabic name
        if name_ar in text:
             found_items.append({
                 'name_ar': name_ar,
                 'name_en': name_en,
                 'id': item_id,
                 'matched_text': name_ar
             })
        # Check for English name
        elif name_en.lower() in text_lower:
             found_items.append({
                 'name_ar': name_ar,
                 'name_en': name_en,
                 'id': item_id,
                 'matched_text': name_en
             })


    # Remove duplicates based on ID if any
    seen_ids = set()
    unique_items = []
    for item in found_items:
        if item['id'] not in seen_ids:
            seen_ids.add(item['id'])
            unique_items.append(item)

    logger.debug(f"Extracted menu items: {unique_items}")
    return unique_items

def extract_quantity(text: str) -> int:
    """
    Extracts the quantity (assumed to be the first number found) from the text.
    This is a very simple implementation.

    Args:
        text (str): The user's input text.

    Returns:
        int: The extracted quantity, defaults to 1 if none found.
    """
    logger.debug(f"Extracting quantity from: '{text}'")
    # Find all numbers in the text
    numbers = re.findall(r'\d+', text)
    if numbers:
        # Return the first number found
        quantity = int(numbers[0])
        logger.debug(f"Quantity extracted: {quantity}")
        return quantity
    else:
        # Default quantity
        logger.debug("No quantity found, defaulting to 1.")
        return 1

def extract_customer_name(text: str) -> str:
    """
    Extracts the customer's name. This is highly simplified.
    A real system would need much more robust NER (Named Entity Recognition).

    Args:
        text (str): The user's input text (potentially containing the name).

    Returns:
        str: The extracted name, or an empty string if not confidently found.
    """
    logger.debug(f"Extracting customer name from: '{text}'")
    # Simple Approach
    text_lower = text.lower()
    name_indicators = ["اسمه", "اسمي", "my name is", "is", "it's"]

    for indicator in name_indicators:
        if indicator in text_lower:
            start_pos = text_lower.find(indicator)
            if start_pos != -1:
                # Extract text after the indicator
                potential_name = text[start_pos + len(indicator):].strip()
                name_parts = potential_name.split()[:2]
                extracted_name = " ".join(name_parts).rstrip('.,!?;:')
                if extracted_name:
                    logger.debug(f"Name extracted (simple): '{extracted_name}'")
                    return extracted_name

    # Fallback
    logger.debug("Customer name not confidently extracted.")
    return ""

def extract_entities(user_input: str) -> Dict[str, Any]:
    """
    Main function to extract all relevant entities from the user input.

    Args:
        user_input (str): The transcribed text from the user.

    Returns:
        Dict[str, Any]: A dictionary containing extracted entities.
                        Example: {'items': [...], 'quantity': 1, 'name': 'أحمد'}
    """
    logger.info(f"Extracting entities from input: '{user_input}'")

    entities = {
        'items': extract_menu_items(user_input),
        'quantity': extract_quantity(user_input),
        'name': extract_customer_name(user_input)
    }

    logger.info(f"Extracted entities: {entities}")
    return entities


if __name__ == "__main__":
    test_inputs = [
        "أ хочу شاورما دجاج وانو بيبسي",
        "طلبت مشاوي مشكلة و ثلاث مشروبات",
        "اسمه أحمد محمد",
        "أكيد, طلبت شاورما",
        "محمد", # Just a name
        "القائمة فيش فيها؟"
    ]

    for inp in test_inputs:
        entities = extract_entities(inp)
        print(f"Input: '{inp}'")
        print(f"  Extracted Entities: {entities}")
        print("-" * 20)