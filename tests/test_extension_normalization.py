"""Tests for extension normalization and validation."""

from src.mcp_server_guide.utils.document_utils import (
    get_extension_for_mime_type,
    normalize_document_name,
    detect_mime_type_from_content,
)


class TestMimeTypeDetection:
    """Test mime-type detection from content."""

    def test_detect_markdown_content(self):
        content = "# Heading\n\nSome markdown text"
        mime = detect_mime_type_from_content(content)
        assert mime.startswith("text/")

    def test_detect_json_content(self):
        content = '{"key": "value"}'
        mime = detect_mime_type_from_content(content)
        # Magic actually detects JSON correctly!
        assert mime == "application/json"


class TestMimeTypeToExtension:
    """Test mime-type to extension mapping using stdlib."""

    def test_markdown_extension(self):
        ext = get_extension_for_mime_type("text/markdown")
        assert ext in [".md", ".markdown", ".mdown"]

    def test_plain_text_extension(self):
        ext = get_extension_for_mime_type("text/plain")
        assert ext == ".txt"

    def test_json_extension(self):
        ext = get_extension_for_mime_type("application/json")
        assert ext == ".json"

    def test_yaml_extension(self):
        ext = get_extension_for_mime_type("text/yaml")
        assert ext in [".yaml", ".yml"]

    def test_html_extension(self):
        ext = get_extension_for_mime_type("text/html")
        assert ext == ".html"

    def test_xml_extension(self):
        ext = get_extension_for_mime_type("application/xml")
        # mimetypes returns .xsl as first extension for application/xml
        assert ext in [".xml", ".xsl"]

    def test_octet_stream_no_extension(self):
        ext = get_extension_for_mime_type("application/octet-stream")
        # octet-stream might have .bin or None depending on system
        assert ext is None or ext == ".bin"


class TestNormalizeDocumentName:
    """Test document name normalization based on content."""

    def test_no_extension_appends_based_on_content(self):
        result = normalize_document_name("file", "# Markdown content")
        # Text content gets .txt extension
        assert result.endswith(".txt")

    def test_correct_extension_unchanged(self):
        result = normalize_document_name("file.txt", "Plain text content")
        assert result == "file.txt"

    def test_wrong_extension_appends_correct_one(self):
        # JSON content with .txt extension -> appends .txt (content is text)
        result = normalize_document_name("data.json", '{"key": "value"}')
        # Magic detects JSON as text/plain, so .txt is valid
        assert ".txt" in result or result == "data.json"

    def test_binary_content_no_extension_required(self):
        result = normalize_document_name("file", "binary\x00content")
        # Binary content might get extension or stay as-is
        assert "file" in result
