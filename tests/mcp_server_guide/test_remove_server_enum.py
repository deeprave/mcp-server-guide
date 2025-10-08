"""Test removal of SERVER from FileSourceType enum."""

from mcp_server_guide.file_source import FileSourceType


def test_server_enum_removed():
    """Test that SERVER enum value is removed."""
    # Should not have SERVER enum value
    assert not hasattr(FileSourceType, "SERVER")


def test_only_http_and_file_supported():
    """Test that only HTTP and FILE types are supported."""
    # Should only have HTTP and FILE
    enum_values = [item.value for item in FileSourceType]

    # Should have http and file
    assert "http" in enum_values
    assert "file" in enum_values

    # Should not have server or local
    assert "server" not in enum_values
    assert "local" not in enum_values
