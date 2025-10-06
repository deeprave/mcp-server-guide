"""Test security module initialization."""


def test_security_init_imports():
    """Test that security module imports work correctly."""
    from mcp_server_guide.security import PathValidator, sanitize_filename

    assert PathValidator is not None
    assert sanitize_filename is not None
