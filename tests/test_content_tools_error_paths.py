"""Tests for content tools error paths."""

from mcp_server_guide.tools.content_tools import _extract_document_from_content


class TestContentToolsErrorPaths:
    """Tests for content tools error paths."""

    def test_extract_document_from_content_no_match(self):
        """Test _extract_document_from_content with no match."""
        content = "# Some content\nNo matching document here"
        result = _extract_document_from_content(content, "nonexistent")
        assert result is None

    def test_extract_document_from_content_with_match(self):
        """Test _extract_document_from_content with match."""
        content = "# Some content\n## test.md\nThis is test content"
        result = _extract_document_from_content(content, "test")
        assert result == "This is test content"
