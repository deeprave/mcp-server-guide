"""Tests for HTTP access functionality."""

import pytest
from unittest.mock import Mock, patch
import requests.exceptions
from mcp_server_guide.http_client import HttpClient, HttpResponse, HttpError


async def test_http_client_basic():
    """Test basic HTTP client functionality."""
    client = HttpClient()

    # Mock successful response
    mock_response = Mock()
    mock_response.text = "test content"
    mock_response.headers = {"Content-Type": "text/plain"}
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response):
        result = client.get("http://example.com")
        assert isinstance(result, HttpResponse)
        assert result.content == "test content"
        assert result.headers == {"Content-Type": "text/plain"}


async def test_http_client_error_handling():
    """Test HTTP client error handling to hit all branches."""
    client = HttpClient()

    # Test connection error
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError("Connection failed")):
        with pytest.raises(HttpError):
            client.get("http://example.com/test")

    # Test timeout error
    with patch("requests.get", side_effect=requests.exceptions.Timeout("Timeout")):
        with pytest.raises(HttpError):
            client.get("http://example.com/test")

    # Test HTTP error
    with patch("requests.get", side_effect=requests.exceptions.HTTPError("HTTP Error")):
        with pytest.raises(HttpError):
            client.get("http://example.com/test")

    # Test generic requests exception
    with patch("requests.get", side_effect=requests.exceptions.RequestException("Request error")):
        with pytest.raises(HttpError):
            client.get("http://example.com/test")


async def test_http_client_comprehensive():
    """Test HTTP client comprehensive functionality."""
    client = HttpClient()

    # Test successful GET request
    mock_response = Mock()
    mock_response.text = "response content"
    mock_response.headers = {"Content-Length": "16"}
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response) as mock_get:
        result = client.get("http://example.com/test")
        assert isinstance(result, HttpResponse)
        assert result.content == "response content"

        # Check that requests.get was called with correct parameters
        from mcp_server_guide.naming import user_agent

        mock_get.assert_called_with("http://example.com/test", timeout=30, headers={"User-Agent": user_agent()})


async def test_http_client_initialization():
    """Test HTTP client initialization."""
    # Test default initialization
    client1 = HttpClient()
    assert client1.timeout == 30
    from mcp_server_guide.naming import user_agent

    assert client1.headers == {"User-Agent": user_agent()}

    # Test initialization with custom values
    custom_headers = {"Authorization": "Bearer token"}
    client2 = HttpClient(timeout=60, headers=custom_headers)
    assert client2.timeout == 60
    # Should merge with default headers
    expected_headers = {"User-Agent": user_agent(), "Authorization": "Bearer token"}
    assert client2.headers == expected_headers


async def test_http_response():
    """Test HttpResponse class."""
    response = HttpResponse(content="test content", headers={"Content-Type": "text/plain"})

    assert response.content == "test content"
    assert response.headers == {"Content-Type": "text/plain"}


async def test_http_error():
    """Test HttpError exception."""
    error = HttpError("Test error message")
    assert str(error) == "Test error message"
    assert isinstance(error, Exception)


async def test_http_client_exists():
    """Test HTTP client exists method."""
    client = HttpClient()

    # Mock successful HEAD response
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None

    with patch("requests.head", return_value=mock_response):
        result = client.exists("http://example.com")
        assert result is True

    # Test HEAD request failure
    with patch("requests.head", side_effect=requests.exceptions.RequestException("Not found")):
        result = client.exists("http://example.com")
        assert result is False
