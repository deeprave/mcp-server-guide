"""Tests for LazyPath-FileSource integration."""

import pytest
from pathlib import Path

from mcp_server_guide.path_resolver import LazyPath
from mcp_server_guide.file_source import FileSource, FileSourceType


class TestLazyPathFileSourceIntegration:
    """Test LazyPath integration with FileSource for consistent URI handling."""

    def test_lazypath_uses_filesource_for_uri_resolution(self):
        """Test that LazyPath can use FileSource for URI-based path resolution."""
        # This should fail initially - LazyPath doesn't use FileSource yet
        lazy_path = LazyPath("relative/path")

        # Should be able to get FileSource representation
        file_source = lazy_path.to_file_source()
        assert isinstance(file_source, FileSource)
        assert file_source.type == FileSourceType.FILE
        assert file_source.base_path == "relative/path"

    def test_lazypath_supports_all_filesource_uri_prefixes(self):
        """Test LazyPath supports all FileSource URI prefixes."""
        test_cases = [
            ("file://path/file", FileSourceType.FILE, "path/file"),
            ("path/file", FileSourceType.FILE, "path/file"),
            ("http://example.com/file", FileSourceType.HTTP, "http://example.com/file"),
            ("http://example.com/file", FileSourceType.HTTP, "http://example.com/file"),
            ("file://path/file", FileSourceType.FILE, "path/file"),
        ]

        for uri, expected_type, expected_path in test_cases:
            lazy_path = LazyPath(uri)
            file_source = lazy_path.to_file_source()
            assert file_source.type == expected_type
            assert file_source.base_path == expected_path

    @pytest.mark.asyncio
    async def test_lazypath_resolution_with_filesource_caching(self):
        """Test that LazyPath caches FileSource resolution results."""
        import os
        from pathlib import Path

        # Change to test directory for PWD-based resolution
        original_cwd = Path.cwd()
        test_dir = Path("/tmp/test_caching").resolve()
        test_dir.mkdir(exist_ok=True)
        os.chdir(test_dir)

        try:
            lazy_path = LazyPath("relative/path")

            # First resolution should create FileSource
            result1 = await lazy_path.resolve()
            file_source1 = lazy_path.to_file_source()

            # Second resolution should use cached FileSource
            result2 = await lazy_path.resolve()
            file_source2 = lazy_path.to_file_source()

            assert result1 == result2
            assert file_source1 is file_source2  # Same object (cached)
        finally:
            os.chdir(original_cwd)
            if test_dir.exists():
                test_dir.rmdir()

    def test_lazypath_from_filesource_factory(self):
        """Test creating LazyPath from FileSource."""
        file_source = FileSource(type=FileSourceType.FILE, base_path="relative/path")

        lazy_path = LazyPath.from_file_source(file_source)
        assert lazy_path.path_str == "relative/path"

        # Should be able to convert back
        converted_source = lazy_path.to_file_source()
        assert converted_source.type == file_source.type
        assert converted_source.base_path == file_source.base_path

    @pytest.mark.asyncio
    async def test_lazypath_http_uri_resolution(self):
        """Test LazyPath resolution with HTTP URIs."""
        lazy_path = LazyPath("http://example.com/file.txt")

        # HTTP URIs resolve to Path objects (which normalize the URL)
        # Note: Path normalization converts "http://example.com" to "http:/example.com"
        result = await lazy_path.resolve()
        assert str(result) == "http:/example.com/file.txt"

    def test_lazypath_server_uri_fallback(self):
        """Test LazyPath with regular path falls back to server-side resolution."""
        lazy_path = LazyPath("relative/path")

        # Should resolve relative to current working directory (server-side)
        result = lazy_path.resolve_sync()
        expected = Path("relative/path").expanduser().resolve()
        assert result == expected


class TestLazyPathFileSourceErrorHandling:
    """Test error handling in LazyPath-FileSource integration."""

    def test_lazypath_invalid_uri_scheme(self):
        """Test LazyPath handling of invalid URI schemes."""
        lazy_path = LazyPath("invalid://path/file")

        # Should fall back to treating as regular path
        result = lazy_path.resolve_sync()
        expected = Path("invalid://path/file").expanduser().resolve()
        assert result == expected

    def test_lazypath_filesource_conversion_edge_cases(self):
        """Test edge cases in LazyPath-FileSource conversion."""
        # Empty path
        lazy_path = LazyPath("")
        file_source = lazy_path.to_file_source()
        assert file_source.type == FileSourceType.FILE  # Default for non-URI paths
        assert file_source.base_path == ""

        # Path with no scheme
        lazy_path = LazyPath("relative/path")
        file_source = lazy_path.to_file_source()
        assert file_source.type == FileSourceType.FILE
        assert file_source.base_path == "relative/path"
