"""Test HTTP module initialization."""


def test_http_init_imports():
    """Test that HTTP module imports work correctly."""
    from mcp_server_guide.http import SecureHTTPClient

    assert SecureHTTPClient is not None
