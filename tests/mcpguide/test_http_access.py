"""Tests for HTTP file access (Issue 003 Phase 2)."""

import pytest
from unittest.mock import Mock, patch
from mcpguide.file_source import FileSource, FileAccessor
from mcpguide.http_client import HttpClient, HttpError


def test_http_client_creation():
    """Test creating HTTP client."""
    client = HttpClient()
    assert client.timeout == 30
    assert client.headers == {"User-Agent": "mcpguide/1.0"}


def test_http_client_custom_config():
    """Test HTTP client with custom configuration."""
    headers = {"Authorization": "Bearer token123"}
    client = HttpClient(timeout=60, headers=headers)
    assert client.timeout == 60
    assert client.headers["Authorization"] == "Bearer token123"
    assert client.headers["User-Agent"] == "mcpguide/1.0"


@patch("requests.get")
def test_http_client_get_success(mock_get):
    """Test successful HTTP GET request."""
    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "# Guide Content\nThis is a guide."
    mock_response.headers = {"content-type": "text/markdown"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    client = HttpClient()
    response = client.get("https://example.com/guide.md")

    assert response.content == "# Guide Content\nThis is a guide."
    assert response.headers["content-type"] == "text/markdown"
    mock_get.assert_called_once_with("https://example.com/guide.md", timeout=30, headers={"User-Agent": "mcpguide/1.0"})


@patch("requests.get")
def test_http_client_get_404_error(mock_get):
    """Test HTTP GET with 404 error."""
    # Mock 404 response
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")
    mock_get.return_value = mock_response

    client = HttpClient()
    with pytest.raises(HttpError) as exc_info:
        client.get("https://example.com/missing.md")

    assert "404" in str(exc_info.value)


@patch("requests.get")
def test_http_client_timeout_error(mock_get):
    """Test HTTP GET with timeout."""
    # Mock timeout
    mock_get.side_effect = Exception("Timeout")

    client = HttpClient()
    with pytest.raises(HttpError) as exc_info:
        client.get("https://example.com/guide.md")

    assert "Timeout" in str(exc_info.value)


@patch("requests.head")
def test_http_client_exists_success(mock_head):
    """Test HTTP HEAD request for file existence."""
    # Mock successful HEAD response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_head.return_value = mock_response

    client = HttpClient()
    exists = client.exists("https://example.com/guide.md")

    assert exists is True
    mock_head.assert_called_once_with(
        "https://example.com/guide.md", timeout=30, headers={"User-Agent": "mcpguide/1.0"}
    )


@patch("requests.head")
def test_http_client_exists_404(mock_head):
    """Test HTTP HEAD request for non-existent file."""
    # Mock 404 response
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")
    mock_head.return_value = mock_response

    client = HttpClient()
    exists = client.exists("https://example.com/missing.md")

    assert exists is False


def test_file_accessor_http_read_file():
    """Test FileAccessor reading HTTP files."""
    with patch("mcpguide.http_client.HttpClient") as mock_client_class:
        # Mock HTTP client
        mock_client = Mock()
        mock_client.get.return_value = "# HTTP Guide\nContent from HTTP"
        mock_client_class.return_value = mock_client

        accessor = FileAccessor()
        http_source = FileSource("http", "https://example.com/docs/")

        content = accessor.read_file("guide.md", http_source)

        assert content == "# HTTP Guide\nContent from HTTP"
        mock_client.get.assert_called_once_with("https://example.com/docs/guide.md")


def test_file_accessor_http_file_exists():
    """Test FileAccessor checking HTTP file existence."""
    with patch("mcpguide.http_client.HttpClient") as mock_client_class:
        # Mock HTTP client
        mock_client = Mock()
        mock_client.exists.return_value = True
        mock_client_class.return_value = mock_client

        accessor = FileAccessor()
        http_source = FileSource("http", "https://example.com/docs/")

        exists = accessor.file_exists("guide.md", http_source)

        assert exists is True
        mock_client.exists.assert_called_once_with("https://example.com/docs/guide.md")


def test_file_accessor_http_authentication():
    """Test FileAccessor with HTTP authentication."""
    with patch("mcpguide.http_client.HttpClient") as mock_client_class:
        # Mock HTTP client
        mock_client = Mock()
        mock_client.get.return_value = "Authenticated content"
        mock_client_class.return_value = mock_client

        # HTTP source with authentication
        http_source = FileSource("http", "https://private.example.com/docs/")
        http_source.auth_headers = {"Authorization": "Bearer secret"}

        accessor = FileAccessor()
        content = accessor.read_file("private-guide.md", http_source)

        assert content == "Authenticated content"
        # Should create client with auth headers
        mock_client_class.assert_called_once_with(timeout=30, headers={"Authorization": "Bearer secret"})
