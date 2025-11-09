"""Tests for server integration with hybrid file access (Issue 003 Phase 4)."""

import tempfile
from unittest.mock import patch

from mcp_server_guide.server import create_server
from mcp_server_guide.session_manager import SessionManager


async def test_server_uses_hybrid_file_access():
    """Test that server uses hybrid file access system."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create server with cache directory
        server = await create_server(docroot=".", cache_dir=temp_dir)

        # Server should have file accessor with cache
        assert hasattr(server, "extensions")
        assert hasattr(server.extensions, "file_accessor")
        assert server.extensions.file_accessor.cache is not None


async def test_server_integration_with_session_paths():
    """Test server integration with Issue 002 session path resolution."""
    from mcp_server_guide.project_config import ProjectConfig
    from mcp_server_guide.models.category import Category

    with tempfile.TemporaryDirectory() as temp_dir:
        server = await create_server(cache_dir=temp_dir)

        try:
            session = SessionManager()
            session.set_project_name("integration-project")

            # Test different category types: local files and HTTP URLs
            config = ProjectConfig(
                categories={
                    "guide": Category(dir="./guides/", patterns=["local-guide.md"], description="Guide files"),
                    "lang": Category(dir="./lang/", patterns=["server-lang.md"], description="Language files"),
                    "context": Category(url="https://example.com/context.md", description="Context files"),
                }
            )
            session.session_state.project_config = config

            with patch.object(server.extensions, "_session_manager", session):
                # Test that category content can be retrieved
                from mcp_server_guide.tools.category_tools import get_category_content

                # Test local file categories
                guide_result = await get_category_content("guide", "integration-project")
                assert isinstance(guide_result, dict)

                lang_result = await get_category_content("lang")
                assert isinstance(lang_result, dict)

                # Test HTTP category
                context_result = await get_category_content("context")
                assert isinstance(context_result, dict)
                assert context_result.get("is_http") is True
                assert context_result.get("url") == "https://example.com/context.md"
        finally:
            # Ensure proper cleanup
            SessionManager.clear()
