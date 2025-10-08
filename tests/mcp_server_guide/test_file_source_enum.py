"""Tests for FileSourceType enum."""

import pytest
from mcp_server_guide.file_source import FileSourceType


class TestFileSourceType:
    """Test FileSourceType enum functionality."""

    def test_enum_values(self):
        """Test that enum has expected values."""
        assert FileSourceType.FILE
        assert FileSourceType.FILE
        assert FileSourceType.HTTP

    def test_enum_string_representation(self):
        """Test enum string representation."""
        assert str(FileSourceType.FILE) == "file"
        assert str(FileSourceType.HTTP) == "http"

    def test_enum_value_access(self):
        """Test accessing enum values."""
        assert FileSourceType.FILE.value == "file"
        assert FileSourceType.HTTP.value == "http"

    def test_enum_comparison(self):
        """Test enum comparison operations."""
        assert FileSourceType.FILE == FileSourceType.FILE
        assert FileSourceType.FILE != FileSourceType.HTTP

    def test_enum_from_string(self):
        """Test creating enum from string values."""
        assert FileSourceType("file") == FileSourceType.FILE
        assert FileSourceType("http") == FileSourceType.HTTP

    def test_enum_invalid_string_raises_error(self):
        """Test that passing an invalid string to FileSourceType raises a ValueError."""
        with pytest.raises(ValueError):
            FileSourceType("invalid_value")

    def test_enum_iteration(self):
        """Test iterating over enum values."""
        values = list(FileSourceType)
        assert FileSourceType.FILE in values
        assert FileSourceType.HTTP in values
        # CLIENT should not appear as separate value since it's an alias
