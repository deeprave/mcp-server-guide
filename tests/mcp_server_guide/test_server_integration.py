"""Tests for server integration with hybrid file access (Issue 003 Phase 4)."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from mcp_server_guide.server import create_server
from mcp_server_guide.session_manager import SessionManager


async def test_server_uses_hybrid_file_access():
    """Test that server uses hybrid file access system."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create server with cache directory
        server = create_server(docroot=".", cache_dir=temp_dir)

        # Server should have file accessor with cache
        assert hasattr(server, "file_accessor")
        assert server.file_accessor.cache is not None


async def test_server_resolves_http_resources() -> None:
    """Test server can resolve HTTP resources."""
    import mcp_server_guide.project_config

    with tempfile.TemporaryDirectory() as temp_dir:
        server = create_server(cache_dir=temp_dir)

        # Mock session with HTTP guide in categories
        session = SessionManager()
        session.set_project_name("test-project")
        config = mcp_server_guide.project_config.ProjectConfig(
            categories={
                "guide": mcp_server_guide.project_config.Category(
                    url="https://example.com/guide.md", description="Guide files", auto_load=False
                )
            }
        )
        session.session_state.project_config = config

        with patch.object(server, "_session_manager", session):
            with patch("mcp_server_guide.http.async_client.AsyncHTTPClient") as mock_client_class:
                # Mock HTTP response
                mock_client = Mock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_response = Mock()
                mock_response.content = "# HTTP Guide\nRemote content"
                mock_response.headers = {"last-modified": "Wed, 21 Oct 2015 07:28:00 GMT"}
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                # Server should be able to read HTTP guide
                content = await server.read_guide("test-project")
                assert content == "# HTTP Guide\nRemote content"

                # Should have used HTTP client
                assert mock_client.get.call_count == 1


async def test_server_caches_http_resources():
    """Test server caches HTTP resources."""
    from mcp_server_guide.project_config import ProjectConfig, Category

    with tempfile.TemporaryDirectory() as temp_dir:
        server = create_server(cache_dir=temp_dir)

        session = SessionManager()
        session.set_project_name("test-project")
        config = ProjectConfig(
            categories={
                "guide": Category(url="https://example.com/guide.md", description="Guide files", auto_load=False)
            }
        )
        session.session_state.project_config = config

        with patch.object(server, "_session_manager", session):
            with patch("mcp_server_guide.http.async_client.AsyncHTTPClient") as mock_client_class:
                mock_client = Mock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_response = Mock()
                mock_response.content = "# Cached Guide"
                mock_response.headers = {"last-modified": "Wed, 21 Oct 2015 07:28:00 GMT"}
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client.get_conditional = AsyncMock(return_value=None)  # 304 Not Modified
                mock_client_class.return_value = mock_client

                # First read - should cache
                content1 = await server.read_guide("test-project")
                assert content1 == "# Cached Guide"
                assert mock_client.get.call_count == 1

                # Mock cache entry to need validation
                with patch.object(server.file_accessor.cache, "get") as mock_cache_get:
                    from mcp_server_guide.file_cache import CacheEntry

                    cached_entry = CacheEntry(
                        "# Cached Guide",
                        {"last-modified": "Wed, 21 Oct 2015 07:28:00 GMT"},
                        cached_at=0,  # Very old cache entry
                    )
                    mock_cache_get.return_value = cached_entry

                    # Second read - should use conditional request
                    content2 = await server.read_guide("test-project")
                    assert content2 == "# Cached Guide"
                    assert mock_client.get_conditional.call_count == 1


async def test_server_handles_mixed_sources():
    """Test server handles mixed local and HTTP sources."""
    from mcp_server_guide.project_config import ProjectConfig, Category

    with tempfile.TemporaryDirectory() as temp_dir:
        server = create_server(cache_dir=temp_dir, docroot=temp_dir)

        # Create a test README file
        readme_path = Path(temp_dir) / "README.md"
        readme_path.write_text("# Local Guide")

        session = SessionManager()
        session.set_project_name("mixed-project")
        config = ProjectConfig(
            categories={
                "guide": Category(dir=".", patterns=["README.md"], description="Guide files", auto_load=False),
                "lang": Category(url="https://example.com/lang.md", description="Language files", auto_load=False),
            }
        )
        session.session_state.project_config = config

        with patch.object(server, "_session_manager", session):
            with patch("mcp_server_guide.http.async_client.AsyncHTTPClient") as mock_client_class:
                mock_client = Mock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_response = Mock()
                mock_response.content = "# HTTP Language"
                mock_response.headers = {}
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                # Should read local guide without HTTP
                guide_content = await server.read_guide("mixed-project")
                assert isinstance(guide_content, str)  # Should read README.md
                assert mock_client.get.call_count == 0  # No HTTP for local file

                # Should read HTTP language with HTTP client
                lang_content = await server.read_language("mixed-project")
                assert lang_content == "# HTTP Language"
                assert mock_client.get.call_count == 1  # HTTP for remote file


async def test_server_fallback_on_http_error():
    """Test server falls back to cache on HTTP errors."""
    from mcp_server_guide.project_config import ProjectConfig, Category

    with tempfile.TemporaryDirectory() as temp_dir:
        server = create_server(cache_dir=temp_dir)

        session = SessionManager()
        session.set_project_name("fallback-project")
        config = ProjectConfig(
            categories={
                "guide": Category(url="https://example.com/guide.md", description="Guide files", auto_load=False)
            }
        )
        session.session_state.project_config = config

        with patch.object(server, "_session_manager", session):
            with patch("mcp_server_guide.http.async_client.AsyncHTTPClient") as mock_client_class:
                from mcp_server_guide.http_client import HttpError

                mock_client = Mock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)

                # First request succeeds and caches
                mock_response = Mock()
                mock_response.content = "# Cached Guide"
                mock_response.headers = {"last-modified": "Wed, 21 Oct 2015 07:28:00 GMT"}
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                # First read - populates cache
                content1 = await server.read_guide("fallback-project")
                assert content1 == "# Cached Guide"

                # Second request fails
                mock_client.get_conditional.side_effect = HttpError("Network error")

                # Force cache validation
                with patch("time.time", return_value=1000000000):  # Far future
                    # Should fall back to cache
                    content2 = await server.read_guide("fallback-project")
                    assert content2 == "# Cached Guide"


async def test_server_integration_with_session_paths():
    """Test server integration with Issue 002 session path resolution."""
    from mcp_server_guide.project_config import ProjectConfig, Category

    with tempfile.TemporaryDirectory() as temp_dir:
        server = create_server(cache_dir=temp_dir)

        session = SessionManager()
        session.set_project_name("integration-project")

        # Test different category types: local files and HTTP URLs
        config = ProjectConfig(
            categories={
                "guide": Category(
                    dir="./guides/", patterns=["local-guide.md"], description="Guide files", auto_load=False
                ),
                "lang": Category(
                    dir="./lang/", patterns=["server-lang.md"], description="Language files", auto_load=False
                ),
                "context": Category(url="https://example.com/context.md", description="Context files", auto_load=False),
            }
        )
        session.session_state.project_config = config

        with patch.object(server, "_session_manager", session):
            # Should create appropriate file sources
            guide_source = await server._get_file_source("guide", "integration-project")
            from mcp_server_guide.file_source import FileSourceType

            assert guide_source.type == FileSourceType.FILE

            lang_source = await server._get_file_source("lang", "integration-project")
            assert lang_source.type == FileSourceType.FILE

            context_source = await server._get_file_source("context", "integration-project")
            assert context_source.type == FileSourceType.HTTP
            assert context_source.base_path == "https://example.com/context.md"


async def test_server_respects_cache_settings():
    """Test server respects cache enable/disable settings."""
    from mcp_server_guide.project_config import ProjectConfig, Category

    with tempfile.TemporaryDirectory() as temp_dir:
        server = create_server(cache_dir=temp_dir)

        session = SessionManager()
        session.set_project_name("cache-test")
        config = ProjectConfig(
            categories={
                "guide": Category(url="https://example.com/guide.md", description="Guide files", auto_load=False)
            }
        )
        session.session_state.project_config = config

        with patch.object(server, "_session_manager", session):
            with patch("mcp_server_guide.http.async_client.AsyncHTTPClient") as mock_client_class:
                mock_client = Mock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_response = Mock()
                mock_response.content = "# Guide Content"
                mock_response.headers = {}
                mock_client.get = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                # Test with caching enabled (default)
                source = await server._get_file_source("guide", "cache-test")
                assert source.cache_enabled is True

                # Read should cache
                content = await server.read_guide("cache-test")
                assert content == "# Guide Content"

                # Cache file should exist
                cache_files = list(server.file_accessor.cache.cache_dir.glob("*.json"))
                assert len(cache_files) > 0
