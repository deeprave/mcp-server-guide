"""Document data array processing utilities."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from .text_conversion import decode_data_array, encode_data_array


class DocumentDataProcessor:
    """Processor for document content data arrays with metadata handling."""

    @staticmethod
    def process_document_data(data_array: List[str]) -> List[Dict[str, Any]]:
        """Process document data array into structured content with metadata."""
        if not data_array:
            return []

        decoded_content = decode_data_array(data_array)
        processed_items = []

        for i, content in enumerate(decoded_content):
            item = {
                "index": i,
                "content": content,
                "length": len(content),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "type": "text",
            }
            processed_items.append(item)

        return processed_items

    @staticmethod
    def create_document_data_array(content_items: List[str]) -> List[str]:
        """Create document data array from content items."""
        if not content_items:
            return []

        return encode_data_array(content_items)

    @staticmethod
    def merge_document_data(existing_data: Optional[List[str]], new_data: List[str]) -> List[str]:
        """Merge new document data with existing data."""
        if not existing_data:
            return new_data

        if not new_data:
            return existing_data

        # Decode both arrays
        existing_content = decode_data_array(existing_data)
        new_content = decode_data_array(new_data)

        # Merge content
        merged_content = existing_content + new_content

        # Re-encode
        return encode_data_array(merged_content)

    @staticmethod
    def validate_document_data(data_array: List[str]) -> Dict[str, Any]:
        """Validate document data array and return validation results."""
        result: Dict[str, Any] = {"valid": True, "errors": [], "warnings": [], "item_count": 0, "total_length": 0}

        if not data_array:
            result["warnings"].append("Empty data array")
            return result

        try:
            decoded_content = decode_data_array(data_array)
            result["item_count"] = len(decoded_content)

            for i, content in enumerate(decoded_content):
                if not isinstance(content, str):
                    result["valid"] = False
                    result["errors"].append(f"Item {i} is not a string: {type(content)}")
                else:
                    result["total_length"] = result["total_length"] + len(content)

                    if len(content) == 0:
                        result["warnings"].append(f"Item {i} is empty")
                    elif len(content) > 10000:  # Arbitrary large content warning
                        result["warnings"].append(f"Item {i} is very large ({len(content)} chars)")

        except (TypeError, ValueError) as e:
            result["valid"] = False
            result["errors"].append(f"Failed to decode data array: {e}")

        return result

    @staticmethod
    def extract_document_metadata(data_array: List[str]) -> Dict[str, Any]:
        """Extract metadata from document data array."""
        if not data_array:
            return {
                "item_count": 0,
                "total_length": 0,
                "average_length": 0,
                "empty_items": 0,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }

        try:
            decoded_content = decode_data_array(data_array)
            total_length = sum(len(content) for content in decoded_content)
            empty_items = sum(1 for content in decoded_content if len(content) == 0)

            return {
                "item_count": len(decoded_content),
                "total_length": total_length,
                "average_length": total_length / len(decoded_content) if decoded_content else 0,
                "empty_items": empty_items,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }

        except (TypeError, ValueError) as e:
            return {"error": f"Failed to process metadata: {e}", "processed_at": datetime.now(timezone.utc).isoformat()}
