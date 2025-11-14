"""Text/JSON conversion utilities for enhanced CRUD operations."""

import json
from typing import List

# Maximum size for JSON payloads (1MB)
MAX_JSON_SIZE = 1024 * 1024


def text_to_json_encoded(text: str) -> str:
    """Convert text to JSON-encoded string for instruction payloads.

    Args:
        text: Text string to encode

    Returns:
        JSON-encoded string representation

    Raises:
        TypeError: If text is not a string
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    return json.dumps(text)


def json_encoded_to_text(encoded: str) -> str:
    """Convert JSON-encoded string back to text.

    Args:
        encoded: JSON-encoded string

    Returns:
        Decoded text string

    Raises:
        TypeError: If encoded is not a string
        ValueError: If JSON payload is too large
        json.JSONDecodeError: If encoded is not valid JSON
    """
    if not isinstance(encoded, str):
        raise TypeError(f"Expected str, got {type(encoded).__name__}")

    # Validate size to prevent DoS
    if len(encoded) > MAX_JSON_SIZE:
        raise ValueError(f"JSON payload too large: {len(encoded)} bytes")

    result = json.loads(encoded)
    if not isinstance(result, str):
        raise TypeError("Decoded JSON must be a string")
    return result


def encode_data_array(texts: List[str]) -> List[str]:
    """Encode array of text strings for JSON payload.

    Args:
        texts: List of text strings to encode

    Returns:
        List of JSON-encoded strings

    Raises:
        TypeError: If texts is not a list or contains non-string items
    """
    if not isinstance(texts, list):
        raise TypeError(f"Expected list, got {type(texts).__name__}")

    result = []
    for i, text in enumerate(texts):
        if not isinstance(text, str):
            raise TypeError(f"Item at index {i} is not a string: {type(text).__name__}")
        result.append(text_to_json_encoded(text))
    return result


def decode_data_array(encoded_texts: List[str]) -> List[str]:
    """Decode array of JSON-encoded strings back to text.

    Args:
        encoded_texts: List of JSON-encoded strings

    Returns:
        List of decoded text strings

    Raises:
        TypeError: If encoded_texts is not a list or contains non-string items
        json.JSONDecodeError: If any item is not valid JSON
    """
    if not isinstance(encoded_texts, list):
        raise TypeError(f"Expected list, got {type(encoded_texts).__name__}")

    result = []
    for i, encoded in enumerate(encoded_texts):
        if not isinstance(encoded, str):
            raise TypeError(f"Item at index {i} is not a string: {type(encoded).__name__}")
        try:
            result.append(json_encoded_to_text(encoded))
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Item at index {i}: {e.msg}", e.doc, e.pos) from e
    return result
