"""Tests for path_resolver module."""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from mcp_server_guide.path_resolver import LazyPath


class TestLazyPath:
    """Test LazyPath class functionality."""

    def test_init(self):
        """Test LazyPath initialization."""
        lazy_path = LazyPath("/test/path")
        assert lazy_path.path_str == "/test/path"
        assert lazy_path._resolved_path is None
        assert lazy_path._client_root is None

    def test_str_repr(self):
        """Test string representations."""
        lazy_path = LazyPath("test/path")
        assert str(lazy_path) == "test/path"
        assert repr(lazy_path) == "LazyPath('test/path')"

    @pytest.mark.asyncio
    async def test_resolve_server_path(self):
        """Test resolving server-side paths."""
        lazy_path = LazyPath("test/path")
        resolved = lazy_path.resolve()

        expected = Path("test/path").expanduser().resolve()
        assert resolved == expected
        assert lazy_path._resolved_path == expected

    @pytest.mark.asyncio
    async def test_resolve_server_path_with_tilde(self):
        """Test resolving paths with ~ expansion."""
        lazy_path = LazyPath("~/test/path")
        resolved = lazy_path.resolve()

        expected = Path("~/test/path").expanduser().resolve()
        assert resolved == expected

    @pytest.mark.asyncio
    async def test_resolve_relative_path_success(self):
        """Test resolving relative paths successfully."""
        import os
        from pathlib import Path

        # Change to a test directory
        original_cwd = Path.cwd()
        test_dir = Path("/tmp/test_client_path").resolve()  # Resolve symlinks
        test_dir.mkdir(exist_ok=True)
        os.chdir(test_dir)

        try:
            lazy_path = LazyPath("relative/path")
            resolved = lazy_path.resolve()

            expected = test_dir / "relative/path"
            assert resolved == expected
        finally:
            os.chdir(original_cwd)
            if test_dir.exists():
                test_dir.rmdir()

    @pytest.mark.asyncio
    async def test_resolve_caching(self):
        """Test that resolution is cached."""
        import os
        from pathlib import Path

        # Change to a test directory
        original_cwd = Path.cwd()
        test_dir = Path("/tmp/test_caching")
        test_dir.mkdir(exist_ok=True)
        os.chdir(test_dir)

        try:
            lazy_path = LazyPath("client:test")

            # First resolution
            result1 = lazy_path.resolve()
            # Second resolution should use cache
            result2 = lazy_path.resolve()

            assert result1 == result2
            assert result1 is result2  # Same object reference (cached)
        finally:
            os.chdir(original_cwd)
            if test_dir.exists():
                test_dir.rmdir()

    def test_resolve_cached(self):
        """Test sync resolution when already cached."""
        lazy_path = LazyPath("test/path")
        cached_path = Path("/cached/path")
        lazy_path._resolved_path = cached_path

        result = lazy_path.resolve()
        assert result == cached_path

    def test_init_from_string(self):
        """Test creating LazyPath from string."""
        result = LazyPath("test/path")
        assert isinstance(result, LazyPath)
        assert result.path_str == "test/path"

    def test_init_from_path(self):
        """Test creating LazyPath from Path object."""
        path_obj = Path("test/path")
        result = LazyPath(path_obj)
        assert isinstance(result, LazyPath)
        assert result.path_str == "test/path"


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_empty_path(self):
        """Test handling of empty path."""
        lazy_path = LazyPath("")
        result = lazy_path.resolve()
        expected = Path("").expanduser().resolve()
        assert result == expected

    @pytest.mark.asyncio
    async def test_current_directory_path(self):
        """Test current directory path resolution."""
        import os
        from pathlib import Path

        # Change to a test directory
        original_cwd = Path.cwd()
        test_dir = Path("/tmp/test_empty_relative").resolve()  # Resolve symlinks
        test_dir.mkdir(exist_ok=True)
        os.chdir(test_dir)

        try:
            lazy_path = LazyPath(".")
            resolved = lazy_path.resolve()

            expected = test_dir  # Current directory
            assert resolved == expected
        finally:
            os.chdir(original_cwd)
            if test_dir.exists():
                test_dir.rmdir()

    def test_sync_fallback_with_file_uri(self):
        """Test sync fallback resolution for file:// URI."""
        mock_loop = Mock()
        mock_loop.is_running.return_value = True

        with patch("asyncio.get_event_loop", return_value=mock_loop):
            lazy_path = LazyPath("file://test/path")
            result = lazy_path.resolve()

            # Should resolve using sync fallback
            expected = Path.cwd() / "test/path"
            assert result == expected

    def test_sync_fallback_with_http_uri(self):
        """Test sync fallback resolution for http:// URI."""
        mock_loop = Mock()
        mock_loop.is_running.return_value = True

        with patch("asyncio.get_event_loop", return_value=mock_loop):
            lazy_path = LazyPath("http://example.com/path")
            result = lazy_path.resolve()

            # Should resolve to itself as Path
            assert result == Path("http://example.com/path")

    def test_sync_fallback_with_absolute_path(self):
        """Test sync fallback resolution for absolute path in URI context."""
        mock_loop = Mock()
        mock_loop.is_running.return_value = True

        with patch("asyncio.get_event_loop", return_value=mock_loop):
            # Create a file:// URI that results in absolute path
            lazy_path = LazyPath("file:///absolute/path")
            result = lazy_path.resolve()

            # Should resolve to absolute path
            assert result == Path("/absolute/path")

    def test_sync_fallback_cached_path(self):
        """Test sync fallback when path is already cached."""
        mock_loop = Mock()
        mock_loop.is_running.return_value = True

        lazy_path = LazyPath("test/path")
        cached_path = Path("/cached/result")
        lazy_path._resolved_path = cached_path

        with patch("asyncio.get_event_loop", return_value=mock_loop):
            result = lazy_path.resolve()

            # Should return cached path without re-resolving
            assert result == cached_path


class TestFromFileSource:
    """Test LazyPath.from_file_source class method."""

    def test_from_file_source_with_file_type(self):
        """Test creating LazyPath from FileSource with FILE type."""
        from mcp_server_guide.file_source import FileSource, FileSourceType

        file_source = FileSource(type=FileSourceType.FILE, base_path="test/path")
        lazy_path = LazyPath.from_file_source(file_source)

        assert lazy_path.path_str == "test/path"
        assert lazy_path._file_source == file_source

    def test_from_file_source_with_http_type(self):
        """Test creating LazyPath from FileSource with HTTP type."""
        from mcp_server_guide.file_source import FileSource, FileSourceType

        file_source = FileSource(type=FileSourceType.HTTP, base_path="http://example.com")
        lazy_path = LazyPath.from_file_source(file_source)

        assert lazy_path.path_str == "http://example.com"
        assert lazy_path._file_source == file_source

    def test_from_file_source_with_unknown_type(self):
        """Test creating LazyPath from FileSource with unknown type (fallback case)."""
        from mcp_server_guide.file_source import FileSource, FileSourceType

        # Create a mock FileSource with a different type (tests the else branch)
        file_source = FileSource(type=FileSourceType.FILE, base_path="fallback/path")
        # Override the type to simulate unknown type
        file_source.type = "UNKNOWN"

        lazy_path = LazyPath.from_file_source(file_source)

        # Should use base_path as fallback
        assert lazy_path.path_str == "fallback/path"


class TestLazyPathExpansion:
    """Test LazyPath expansion methods."""

    def test_expanduser_with_tilde(self):
        """Test expanduser with ~ expansion."""
        lazy_path = LazyPath("~/test/path")
        expanded = lazy_path.expanduser()

        # Should expand ~ to home directory
        expected = str(Path("~/test/path").expanduser())
        # Convert to posix for consistent comparison
        assert expanded == Path(expected).as_posix()

    def test_expanduser_without_tilde(self):
        """Test expanduser without ~ (no change)."""
        lazy_path = LazyPath("/absolute/path")
        expanded = lazy_path.expanduser()

        assert expanded == "/absolute/path"

    def test_expandvars_with_env_var(self):
        """Test expandvars with environment variable."""
        # Set a test environment variable
        os.environ["TEST_VAR"] = "/test/value"
        try:
            lazy_path = LazyPath("${TEST_VAR}/path")
            expanded = lazy_path.expandvars()

            assert expanded == "/test/value/path"
        finally:
            del os.environ["TEST_VAR"]

    def test_expandvars_without_env_var(self):
        """Test expandvars without environment variables (no change)."""
        lazy_path = LazyPath("/absolute/path")
        expanded = lazy_path.expandvars()

        assert expanded == "/absolute/path"

    def test_expandvars_with_dollar_sign(self):
        """Test expandvars with $VAR format."""
        os.environ["MYVAR"] = "myvalue"
        try:
            lazy_path = LazyPath("$MYVAR/path")
            expanded = lazy_path.expandvars()

            assert expanded == "myvalue/path"
        finally:
            del os.environ["MYVAR"]


class TestLazyPathIsAbsolute:
    """Test LazyPath is_absolute method."""

    def test_is_absolute_with_absolute_path(self):
        """Test is_absolute with absolute path."""
        lazy_path = LazyPath("/absolute/path")
        assert lazy_path.is_absolute() is True

    def test_is_absolute_with_relative_path(self):
        """Test is_absolute with relative path."""
        lazy_path = LazyPath("relative/path")
        assert lazy_path.is_absolute() is False

    def test_is_absolute_with_tilde(self):
        """Test is_absolute with ~ (should be absolute after expansion)."""
        lazy_path = LazyPath("~/test/path")
        assert lazy_path.is_absolute() is True

    def test_is_absolute_with_env_var_absolute(self):
        """Test is_absolute with env var that expands to absolute path."""
        os.environ["TEST_ABS"] = "/absolute"
        try:
            lazy_path = LazyPath("${TEST_ABS}/path")
            assert lazy_path.is_absolute() is True
        finally:
            del os.environ["TEST_ABS"]

    def test_is_absolute_with_env_var_relative(self):
        """Test is_absolute with env var that expands to relative path."""
        os.environ["TEST_REL"] = "relative"
        try:
            lazy_path = LazyPath("${TEST_REL}/path")
            assert lazy_path.is_absolute() is False
        finally:
            del os.environ["TEST_REL"]

    def test_is_absolute_current_directory(self):
        """Test is_absolute with current directory."""
        lazy_path = LazyPath(".")
        assert lazy_path.is_absolute() is False


class TestLazyPathResolveOptions:
    """Test LazyPath resolve with strict and expand options."""

    @pytest.mark.asyncio
    async def test_resolve_with_expand_true(self):
        """Test resolve with expand=True (default)."""
        os.environ["TEST_DIR"] = "test"
        try:
            lazy_path = LazyPath("${TEST_DIR}/path")
            resolved = lazy_path.resolve(expand=True)

            # Should expand env var and resolve
            expected = Path("test/path").resolve()
            assert resolved == expected
        finally:
            del os.environ["TEST_DIR"]

    @pytest.mark.asyncio
    async def test_resolve_with_expand_false(self):
        """Test resolve with expand=False."""
        os.environ["TEST_DIR"] = "test"
        try:
            lazy_path = LazyPath("${TEST_DIR}/path")
            # Clear cached resolution to force re-resolve
            lazy_path._resolved_path = None

            resolved = lazy_path.resolve(expand=False)

            # Should NOT expand env var, just resolve literal path
            # This will resolve ${TEST_DIR}/path as a literal directory name
            expected = Path("${TEST_DIR}/path").resolve()
            assert resolved == expected
        finally:
            del os.environ["TEST_DIR"]

    @pytest.mark.asyncio
    async def test_resolve_with_strict_false_nonexistent(self):
        """Test resolve with strict=False on non-existent path (default behavior)."""
        lazy_path = LazyPath("/nonexistent/path/that/does/not/exist")

        # Should not raise error with strict=False (default)
        resolved = lazy_path.resolve(strict=False)
        assert resolved == Path("/nonexistent/path/that/does/not/exist")

    @pytest.mark.asyncio
    async def test_resolve_with_strict_true_nonexistent(self):
        """Test resolve with strict=True on non-existent path."""
        lazy_path = LazyPath("/nonexistent/path/that/does/not/exist")

        # Should raise FileNotFoundError with strict=True
        with pytest.raises(FileNotFoundError):
            lazy_path.resolve(strict=True)

    @pytest.mark.asyncio
    async def test_resolve_tilde_expansion(self):
        """Test resolve with tilde expansion."""
        lazy_path = LazyPath("~/test/path")
        resolved = lazy_path.resolve(expand=True)

        expected = Path.home() / "test" / "path"
        assert resolved == expected

    @pytest.mark.asyncio
    async def test_resolve_combined_expansions(self):
        """Test resolve with both tilde and env var expansion."""
        os.environ["SUBDIR"] = "mydir"
        try:
            # Note: This creates a path like /home/user/mydir/file
            # The ~ expands first, then we append the expanded env var
            lazy_path = LazyPath("~/${SUBDIR}/file")
            resolved = lazy_path.resolve(expand=True)

            expected = Path.home() / "mydir" / "file"
            assert resolved == expected
        finally:
            del os.environ["SUBDIR"]
