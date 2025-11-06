"""Tests for generic category access without hardcoded builtin handlers."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from mcp_server_guide.tools.category_tools import get_category_content, add_category, remove_category


class TestGenericCategoryAccess:
    """Test that all categories are treated equally without special builtin handling."""

    @pytest.mark.asyncio
    async def test_get_any_category_content(self):
        """Should work for ANY category, not just hardcoded ones."""
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session.get_project_name.return_value = "test_project"
            mock_session_class.return_value = mock_session

            # Mock config with custom category
            mock_config = Mock()
            mock_category = Mock()
            mock_category.url = None  # Not a URL-based category
            mock_category.dir = "test/"
            mock_category.patterns = ["*.md"]
            mock_config.categories = {"custom_category": mock_category}

            # Make get_or_create_project_config async
            async def async_get_config(project):
                return mock_config

            mock_session.get_or_create_project_config = async_get_config

            # Mock config_manager and docroot
            mock_config_manager = Mock()
            mock_docroot = Mock()
            mock_docroot.resolve_sync.return_value = Path("/test")
            mock_config_manager.docroot = mock_docroot
            mock_session.config_manager.return_value = mock_config_manager

            # Mock the directory existence and file operations
            with patch("pathlib.Path.exists", return_value=True):
                with patch("mcp_server_guide.tools.category_tools._safe_glob_search", return_value=[]):
                    result = await get_category_content("custom_category")

                    # Should succeed and return expected structure
                    assert result["success"] is True
                    assert "content" in result

    @pytest.mark.asyncio
    async def test_remove_builtin_category_allowed(self):
        """Should allow removing former builtin categories."""
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session.get_project_name.return_value = "test_project"
            mock_session_class.return_value = mock_session

            # Mock config with guide category
            mock_config = Mock()
            mock_config.categories = {"guide": Mock()}
            mock_session.session_state.project_config = mock_config

            # Make get_or_create_project_config async
            async def async_get_config(project):
                return mock_config

            mock_session.get_or_create_project_config = async_get_config

            # Make save_project_config async
            async def async_save_config(config):
                return None

            mock_session.save_project_config = async_save_config

            result = await remove_category("guide")

            # Should succeed - no builtin protection
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_add_category_with_builtin_name_allowed(self):
        """Should allow creating categories with former builtin names."""
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session.get_project_name.return_value = "test_project"
            mock_session_class.return_value = mock_session

            # Mock config without guide category
            mock_config = Mock()
            mock_config.categories = {}
            mock_session.session_state.project_config = mock_config

            # Make get_or_create_project_config async
            async def async_get_config(project):
                return mock_config

            mock_session.get_or_create_project_config = async_get_config

            # Make save_project_config async
            async def async_save_config(config):
                return None

            mock_session.save_project_config = async_save_config

            result = await add_category("guide", "guide/", ["*.md"])

            # Should succeed - no builtin protection
            assert result["success"] is True
