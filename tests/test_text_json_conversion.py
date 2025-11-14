"""Tests for text/JSON conversion utilities."""

import json
import pytest
from mcp_server_guide.utils.text_conversion import (
    text_to_json_encoded,
    json_encoded_to_text,
    encode_data_array,
    decode_data_array,
)


class TestTextJsonConversion:
    """Test text to JSON encoding and decoding."""

    def test_text_to_json_encoded_simple(self):
        """Test encoding simple text to JSON string."""
        text = "Hello, world!"
        result = text_to_json_encoded(text)
        assert result == '"Hello, world!"'

    def test_text_to_json_encoded_with_quotes(self):
        """Test encoding text with quotes to JSON string."""
        text = 'Here is an "overview", with some quoted text'
        result = text_to_json_encoded(text)
        assert result == '"Here is an \\"overview\\", with some quoted text"'

    def test_text_to_json_encoded_multiline(self):
        """Test encoding multiline text to JSON string."""
        text = "# Some Document Type\n## Overview\nHere is content\n"
        result = text_to_json_encoded(text)
        assert result == '"# Some Document Type\\n## Overview\\nHere is content\\n"'

    def test_text_to_json_encoded_type_error(self):
        """Test encoding non-string raises TypeError."""
        with pytest.raises(TypeError, match="Expected str, got int"):
            text_to_json_encoded(123)

    def test_json_encoded_to_text_simple(self):
        """Test decoding simple JSON string to text."""
        encoded = '"Hello, world!"'
        result = json_encoded_to_text(encoded)
        assert result == "Hello, world!"

    def test_json_encoded_to_text_with_quotes(self):
        """Test decoding JSON string with escaped quotes to text."""
        encoded = '"Here is an \\"overview\\", with some quoted text"'
        result = json_encoded_to_text(encoded)
        assert result == 'Here is an "overview", with some quoted text'

    def test_json_encoded_to_text_multiline(self):
        """Test decoding multiline JSON string to text."""
        encoded = '"# Some Document Type\\n## Overview\\nHere is content\\n"'
        result = json_encoded_to_text(encoded)
        assert result == "# Some Document Type\n## Overview\nHere is content\n"

    def test_json_encoded_to_text_type_error(self):
        """Test decoding non-string raises TypeError."""
        with pytest.raises(TypeError, match="Expected str, got int"):
            json_encoded_to_text(123)

    def test_json_encoded_to_text_invalid_json(self):
        """Test decoding invalid JSON raises JSONDecodeError."""
        with pytest.raises(json.JSONDecodeError):
            json_encoded_to_text("invalid json")

    def test_roundtrip_conversion(self):
        """Test that text -> JSON -> text preserves original."""
        original = "# Getting Started\n\nWelcome to our system...\n"
        encoded = text_to_json_encoded(original)
        decoded = json_encoded_to_text(encoded)
        assert decoded == original


class TestDataArrayEncoding:
    """Test data array encoding and decoding."""

    def test_encode_data_array_single(self):
        """Test encoding single text item to data array."""
        texts = ["# Some Document Type\n## Overview\nHere is content\n"]
        result = encode_data_array(texts)
        expected = ['"# Some Document Type\\n## Overview\\nHere is content\\n"']
        assert result == expected

    def test_encode_data_array_multiple(self):
        """Test encoding multiple text items to data array."""
        texts = ["# Getting Started\n\nWelcome to our system...\n", "\n## Advanced Usage\n\nFor advanced features...\n"]
        result = encode_data_array(texts)
        expected = [
            '"# Getting Started\\n\\nWelcome to our system...\\n"',
            '"\\n## Advanced Usage\\n\\nFor advanced features...\\n"',
        ]
        assert result == expected

    def test_encode_data_array_type_error_not_list(self):
        """Test encoding non-list raises TypeError."""
        with pytest.raises(TypeError, match="Expected list, got str"):
            encode_data_array("not a list")

    def test_encode_data_array_type_error_non_string_item(self):
        """Test encoding list with non-string item raises TypeError."""
        with pytest.raises(TypeError, match="Item at index 1 is not a string: int"):
            encode_data_array(["valid", 123])

    def test_decode_data_array_single(self):
        """Test decoding single encoded item from data array."""
        encoded_texts = ['"# Some Document Type\\n## Overview\\nHere is content\\n"']
        result = decode_data_array(encoded_texts)
        expected = ["# Some Document Type\n## Overview\nHere is content\n"]
        assert result == expected

    def test_decode_data_array_multiple(self):
        """Test decoding multiple encoded items from data array."""
        encoded_texts = [
            '"# Getting Started\\n\\nWelcome to our system...\\n"',
            '"\\n## Advanced Usage\\n\\nFor advanced features...\\n"',
        ]
        result = decode_data_array(encoded_texts)
        expected = [
            "# Getting Started\n\nWelcome to our system...\n",
            "\n## Advanced Usage\n\nFor advanced features...\n",
        ]
        assert result == expected

    def test_decode_data_array_type_error_not_list(self):
        """Test decoding non-list raises TypeError."""
        with pytest.raises(TypeError, match="Expected list, got str"):
            decode_data_array("not a list")

    def test_decode_data_array_type_error_non_string_item(self):
        """Test decoding list with non-string item raises TypeError."""
        with pytest.raises(TypeError, match="Item at index 0 is not a string: int"):
            decode_data_array([123])

    def test_decode_data_array_invalid_json_item(self):
        """Test decoding list with invalid JSON item raises JSONDecodeError."""
        with pytest.raises(json.JSONDecodeError, match="Item at index 1"):
            decode_data_array(['"valid"', "invalid json"])

    def test_data_array_roundtrip(self):
        """Test that data array encoding/decoding preserves original."""
        original = [
            "# Getting Started\n\nWelcome to our API...\n## Installation\n\nRun the following command:\n```bash\nnpm install\n```\n",
            "\n## Advanced Usage\n\nFor advanced features...\n",
        ]
        encoded = encode_data_array(original)
        decoded = decode_data_array(encoded)
        assert decoded == original

    def test_encode_empty_array(self):
        """Test encoding empty data array."""
        texts = []
        result = encode_data_array(texts)
        assert result == []

    def test_decode_empty_array(self):
        """Test decoding empty data array."""
        encoded_texts = []
        result = decode_data_array(encoded_texts)
        assert result == []
