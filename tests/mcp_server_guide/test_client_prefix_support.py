"""Tests for client:// prefix support in FileSource."""

from mcp_server_guide.file_source import FileSource, FileSourceType


class TestClientPrefixSupport:
    """Test client:// prefix functionality."""

    def test_client_prefix_maps_to_local(self):
        """Test that client:// prefix maps to LOCAL type."""
        source = FileSource.from_url("client://./docs/guide.md")
        assert source.type == FileSourceType.LOCAL
        assert source.base_path == "./docs/guide.md"

    def test_client_prefix_with_absolute_path(self):
        """Test client:// prefix with absolute path."""
        source = FileSource.from_url("client:///absolute/path/guide.md")
        assert source.type == FileSourceType.LOCAL
        assert source.base_path == "/absolute/path/guide.md"

    def test_client_prefix_with_relative_path(self):
        """Test client:// prefix with relative path."""
        source = FileSource.from_url("client://relative/path/guide.md")
        assert source.type == FileSourceType.LOCAL
        assert source.base_path == "relative/path/guide.md"

    def test_client_prefix_in_session_path(self):
        """Test client:// prefix in session path resolution."""
        source = FileSource.from_session_path("client://./session-guide.md", "test-project")
        assert source.type == FileSourceType.LOCAL
        assert source.base_path == "./session-guide.md"

    def test_backward_compatibility_local_prefix(self):
        """Test that local: prefix still works."""
        source = FileSource.from_url("local:./docs/guide.md")
        assert source.type == FileSourceType.LOCAL
        assert source.base_path == "./docs/guide.md"

    def test_all_prefixes_work_together(self):
        """Test that all URI prefixes work correctly."""
        # Test all supported prefixes
        local_source = FileSource.from_url("local:./local-guide.md")
        client_source = FileSource.from_url("client://./client-guide.md")
        server_source = FileSource.from_url("server:./server-guide.md")
        http_source = FileSource.from_url("https://example.com/http-guide.md")

        assert local_source.type == FileSourceType.LOCAL
        assert client_source.type == FileSourceType.LOCAL  # client maps to LOCAL
        assert server_source.type == FileSourceType.SERVER
        assert http_source.type == FileSourceType.HTTP

        # Verify paths are correctly extracted
        assert local_source.base_path == "./local-guide.md"
        assert client_source.base_path == "./client-guide.md"
        assert server_source.base_path == "./server-guide.md"
        assert http_source.base_path == "https://example.com/http-guide.md"
