"""Tests for SSE mode implementation (Issue 006 Phase 3)."""

import pytest
from unittest.mock import patch
from mcp_server_guide.main import validate_mode, start_mcp_server


def test_sse_url_parsing_basic():
    """Test basic SSE URL parsing."""
    mode_type, mode_config = validate_mode("sse=http://localhost:8080/sse")

    assert mode_type == "sse"
    assert mode_config == "http://localhost:8080/sse"


def test_sse_url_parsing_https():
    """Test HTTPS SSE URL parsing."""
    mode_type, mode_config = validate_mode("sse=https://myserver.com:9000/mcp/sse")

    assert mode_type == "sse"
    assert mode_config == "https://myserver.com:9000/mcp/sse"


def test_sse_url_parsing_no_port():
    """Test SSE URL parsing without explicit port."""
    mode_type, mode_config = validate_mode("sse=http://example.com/api/sse")

    assert mode_type == "sse"
    assert mode_config == "http://example.com/api/sse"


def test_sse_url_parsing_ip_address():
    """Test SSE URL parsing with IP address."""
    mode_type, mode_config = validate_mode("sse=http://192.168.1.100:3000/sse")

    assert mode_type == "sse"
    assert mode_config == "http://192.168.1.100:3000/sse"


def test_invalid_sse_url_no_protocol():
    """Test that invalid SSE URL (no protocol) raises error."""
    import click

    with pytest.raises(click.BadParameter) as exc_info:
        validate_mode("sse=localhost:8080/sse")

    assert "Invalid SSE URL format" in str(exc_info.value)


def test_invalid_sse_url_wrong_protocol():
    """Test that invalid SSE URL (wrong protocol) raises error."""
    import click

    with pytest.raises(click.BadParameter) as exc_info:
        validate_mode("sse=ftp://localhost:8080/sse")

    assert "Invalid SSE URL format" in str(exc_info.value)


def test_sse_server_startup_parses_url():
    """Test that SSE server startup correctly parses URL components."""
    config = {"docroot": ".", "project": "test", "mode_config": "https://myserver.com:9000/mcp/sse"}

    with patch("uvicorn.run") as mock_uvicorn_run:
        start_mcp_server("sse", config)

        # Should call uvicorn.run with correct host and port
        mock_uvicorn_run.assert_called_once()
        call_args = mock_uvicorn_run.call_args

        # Check that host and port are extracted correctly
        assert call_args[1]["host"] == "myserver.com"
        assert call_args[1]["port"] == 9000


def test_sse_server_startup_default_ports():
    """Test that SSE server uses default ports when not specified."""
    # Test HTTP default port (80)
    config_http = {"docroot": ".", "project": "test", "mode_config": "http://example.com/sse"}

    with patch("uvicorn.run") as mock_uvicorn_run:
        start_mcp_server("sse", config_http)

        call_args = mock_uvicorn_run.call_args
        assert call_args[1]["host"] == "example.com"
        assert call_args[1]["port"] == 80

    # Test HTTPS default port (443)
    config_https = {"docroot": ".", "project": "test", "mode_config": "https://secure.com/sse"}

    with patch("uvicorn.run") as mock_uvicorn_run:
        start_mcp_server("sse", config_https)

        call_args = mock_uvicorn_run.call_args
        assert call_args[1]["host"] == "secure.com"
        assert call_args[1]["port"] == 443


def test_sse_server_startup_fallback_defaults():
    """Test SSE server uses fallback defaults when no URL provided."""
    config = {
        "docroot": ".",
        "project": "test",
        # No mode_config
    }

    with patch("uvicorn.run") as mock_uvicorn_run:
        start_mcp_server("sse", config)

        call_args = mock_uvicorn_run.call_args
        assert call_args[1]["host"] == "localhost"
        assert call_args[1]["port"] == 8080
