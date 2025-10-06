"""Tests for path_resolver module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from mcp_server_guide.path_resolver import LazyPath, create_lazy_path


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
        resolved = await lazy_path.resolve()

        expected = Path("test/path").expanduser().resolve()
        assert resolved == expected
        assert lazy_path._resolved_path == expected

    @pytest.mark.asyncio
    async def test_resolve_server_path_with_tilde(self):
        """Test resolving paths with ~ expansion."""
        lazy_path = LazyPath("~/test/path")
        resolved = await lazy_path.resolve()

        expected = Path("~/test/path").expanduser().resolve()
        assert resolved == expected

    @pytest.mark.asyncio
    async def test_resolve_client_path_success(self):
        """Test resolving client: prefixed paths successfully."""
        with patch("mcp_server_guide.path_resolver.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            lazy_path = LazyPath("client:relative/path")
            resolved = await lazy_path.resolve()

            expected = Path("/client/root/relative/path")
            assert resolved == expected
            assert lazy_path._client_root == Path("/client/root")

    @pytest.mark.asyncio
    async def test_resolve_client_path_no_root(self):
        """Test error when no client root available."""
        with patch("mcp_server_guide.path_resolver.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = None

            lazy_path = LazyPath("client:relative/path")

            with pytest.raises(ValueError, match="Cannot resolve client path.*no client working directory"):
                await lazy_path.resolve()

    @pytest.mark.asyncio
    async def test_resolve_caching(self):
        """Test that resolution is cached."""
        with patch("mcp_server_guide.path_resolver.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            lazy_path = LazyPath("client:test")

            # First resolution
            result1 = await lazy_path.resolve()
            # Second resolution should use cache
            result2 = await lazy_path.resolve()

            assert result1 == result2
            assert mock_root.call_count == 1  # Only called once due to caching

    def test_resolve_sync_cached(self):
        """Test sync resolution when already cached."""
        lazy_path = LazyPath("test/path")
        cached_path = Path("/cached/path")
        lazy_path._resolved_path = cached_path

        result = lazy_path.resolve_sync()
        assert result == cached_path

    def test_resolve_sync_no_loop(self):
        """Test sync resolution when no event loop is running."""
        with patch("asyncio.get_event_loop") as mock_get_loop:
            mock_get_loop.side_effect = RuntimeError("No loop")

            with patch("asyncio.run") as mock_run:
                expected_path = Path("/test/path").resolve()
                mock_run.return_value = expected_path

                lazy_path = LazyPath("test/path")
                result = lazy_path.resolve_sync()

                assert result == expected_path
                mock_run.assert_called_once()

    def test_resolve_sync_loop_not_running(self):
        """Test sync resolution when loop exists but not running."""
        mock_loop = Mock()
        mock_loop.is_running.return_value = False

        with patch("asyncio.get_event_loop", return_value=mock_loop):
            with patch("asyncio.run") as mock_run:
                expected_path = Path("/test/path").resolve()
                mock_run.return_value = expected_path

                lazy_path = LazyPath("test/path")
                result = lazy_path.resolve_sync()

                assert result == expected_path
                mock_run.assert_called_once()

    def test_resolve_sync_loop_running_server_path(self):
        """Test sync resolution fallback when loop is running - server path."""
        mock_loop = Mock()
        mock_loop.is_running.return_value = True

        with patch("asyncio.get_event_loop", return_value=mock_loop):
            lazy_path = LazyPath("test/path")
            result = lazy_path.resolve_sync()

            expected = Path("test/path").expanduser().resolve()
            assert result == expected

    def test_resolve_sync_loop_running_client_path(self):
        """Test sync resolution fallback when loop is running - client path."""
        mock_loop = Mock()
        mock_loop.is_running.return_value = True

        with patch("asyncio.get_event_loop", return_value=mock_loop):
            with patch("pathlib.Path.cwd", return_value=Path("/current")):
                lazy_path = LazyPath("client:relative/path")
                result = lazy_path.resolve_sync()

                expected = Path("/current/relative/path")
                assert result == expected


class TestCreateLazyPath:
    """Test create_lazy_path factory function."""

    def test_create_from_string(self):
        """Test creating LazyPath from string."""
        result = create_lazy_path("test/path")
        assert isinstance(result, LazyPath)
        assert result.path_str == "test/path"

    def test_create_from_path(self):
        """Test creating LazyPath from Path object."""
        path_obj = Path("test/path")
        result = create_lazy_path(path_obj)
        assert isinstance(result, LazyPath)
        assert result.path_str == "test/path"


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    def test_empty_path(self):
        """Test handling of empty path."""
        lazy_path = LazyPath("")
        result = lazy_path.resolve_sync()
        expected = Path("").expanduser().resolve()
        assert result == expected

    @pytest.mark.asyncio
    async def test_client_path_empty_relative(self):
        """Test client path with empty relative part."""
        with patch("mcp_server_guide.path_resolver.ClientPath.get_primary_root") as mock_root:
            mock_root.return_value = Path("/client/root")

            lazy_path = LazyPath("client:")
            resolved = await lazy_path.resolve()

            expected = Path("/client/root/")
            assert resolved == expected

    def test_resolve_sync_runtime_error_fallback(self):
        """Test RuntimeError handling in resolve_sync."""
        with patch("asyncio.get_event_loop") as mock_get_loop:
            # First call raises RuntimeError, second call in except block succeeds
            mock_get_loop.side_effect = [RuntimeError("No loop"), Mock()]

            with patch("asyncio.run") as mock_run:
                expected_path = Path("/test/path").resolve()
                mock_run.return_value = expected_path

                lazy_path = LazyPath("test/path")
                result = lazy_path.resolve_sync()

                assert result == expected_path
                assert mock_run.call_count == 1
