"""Tests to improve HTTP client coverage."""

import pytest
import requests
from unittest.mock import patch
from mcp_server_guide.http_client import HttpClient, HttpError


async def test_get_conditional_exception():
    """Test get_conditional exception handling."""
    client = HttpClient()

    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")

        with pytest.raises(HttpError) as exc_info:
            client.get_conditional("http://example.com", if_none_match="etag123")

        assert "HTTP conditional GET failed" in str(exc_info.value)


async def test_exists_exception():
    """Test exists method exception handling."""
    client = HttpClient()

    with patch("requests.head") as mock_head:
        mock_head.side_effect = requests.RequestException("Network error")

        result = client.exists("http://example.com")
        assert result is False
