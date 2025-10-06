"""Tests for deferred configuration functionality."""

from unittest.mock import patch, AsyncMock
from mcp_server_guide.main import configure_builtin_categories


class TestDeferredConfiguration:
    """Test deferred configuration functionality."""

    async def test_configure_builtin_categories_with_guidesdir(self):
        """Test configure_builtin_categories with guidesdir parameter."""
        config = {"guidesdir": "/custom/guides", "guide": "custom-guide"}

        mock_categories_result = {
            "builtin_categories": [
                {"name": "guide", "dir": "/default/guides", "patterns": ["*.md"], "description": "Project guidelines"}
            ]
        }

        with patch("mcp_server_guide.tools.category_tools.list_categories", new_callable=AsyncMock) as mock_list:
            with patch("mcp_server_guide.tools.category_tools.update_category", new_callable=AsyncMock) as mock_update:
                mock_list.return_value = mock_categories_result

                await configure_builtin_categories(config)

                mock_list.assert_called_once()
                mock_update.assert_called_once_with(
                    name="guide", dir="/custom/guides", patterns=["custom-guide.md"], description="Project guidelines"
                )

    async def test_configure_builtin_categories_with_langsdir(self):
        """Test configure_builtin_categories with langsdir parameter."""
        config = {"langsdir": "/custom/langs", "lang": "rust"}

        mock_categories_result = {
            "builtin_categories": [
                {"name": "lang", "dir": "/default/langs", "patterns": ["*.md"], "description": "Language guidelines"}
            ]
        }

        with patch("mcp_server_guide.tools.category_tools.list_categories", new_callable=AsyncMock) as mock_list:
            with patch("mcp_server_guide.tools.category_tools.update_category", new_callable=AsyncMock) as mock_update:
                mock_list.return_value = mock_categories_result

                await configure_builtin_categories(config)

                mock_list.assert_called_once()
                mock_update.assert_called_once_with(
                    name="lang", dir="/custom/langs", patterns=["rust.md"], description="Language guidelines"
                )

    async def test_configure_builtin_categories_with_contextdir(self):
        """Test configure_builtin_categories with contextdir parameter."""
        config = {"contextdir": "/custom/context"}

        mock_categories_result = {
            "builtin_categories": [
                {"name": "context", "dir": "/default/context", "patterns": ["*.md"], "description": "Project context"}
            ]
        }

        with patch("mcp_server_guide.tools.category_tools.list_categories", new_callable=AsyncMock) as mock_list:
            with patch("mcp_server_guide.tools.category_tools.update_category", new_callable=AsyncMock) as mock_update:
                mock_list.return_value = mock_categories_result

                await configure_builtin_categories(config)

                mock_list.assert_called_once()
                mock_update.assert_called_once_with(
                    name="context", dir="/custom/context", patterns=["*.md"], description="Project context"
                )

    async def test_configure_builtin_categories_no_matching_category(self):
        """Test configure_builtin_categories when no matching category exists."""
        config = {"guidesdir": "/custom/guides"}

        mock_categories_result = {
            "builtin_categories": []  # No matching categories
        }

        with patch("mcp_server_guide.tools.category_tools.list_categories", new_callable=AsyncMock) as mock_list:
            with patch("mcp_server_guide.tools.category_tools.update_category", new_callable=AsyncMock) as mock_update:
                mock_list.return_value = mock_categories_result

                await configure_builtin_categories(config)

                mock_list.assert_called_once()
                mock_update.assert_not_called()  # Should not update if no matching category

    async def test_configure_builtin_categories_list_categories_fails(self):
        """Test configure_builtin_categories when list_categories fails."""
        config = {"guidesdir": "/custom/guides"}

        with patch("mcp_server_guide.tools.category_tools.list_categories", new_callable=AsyncMock) as mock_list:
            with patch("mcp_server_guide.tools.category_tools.update_category", new_callable=AsyncMock) as mock_update:
                with patch("mcp_server_guide.main.logger") as mock_logger:
                    mock_list.side_effect = Exception("List failed")

                    await configure_builtin_categories(config)

                    mock_list.assert_called_once()
                    mock_update.assert_not_called()
                    mock_logger.warning.assert_called_once_with("Failed to configure category guide")

    async def test_configure_builtin_categories_empty_config(self):
        """Test configure_builtin_categories with empty config."""
        config = {}

        with patch("mcp_server_guide.tools.category_tools.list_categories", new_callable=AsyncMock) as mock_list:
            with patch("mcp_server_guide.tools.category_tools.update_category", new_callable=AsyncMock) as mock_update:
                await configure_builtin_categories(config)

                mock_list.assert_not_called()
                mock_update.assert_not_called()

    async def test_configure_builtin_categories_file_value_none(self):
        """Test configure_builtin_categories with file value set to 'none'."""
        config = {"guidesdir": "/custom/guides", "guide": "none"}

        mock_categories_result = {
            "builtin_categories": [
                {
                    "name": "guide",
                    "dir": "/default/guides",
                    "patterns": ["default.md"],
                    "description": "Project guidelines",
                }
            ]
        }

        with patch("mcp_server_guide.tools.category_tools.list_categories", new_callable=AsyncMock) as mock_list:
            with patch("mcp_server_guide.tools.category_tools.update_category", new_callable=AsyncMock) as mock_update:
                mock_list.return_value = mock_categories_result

                await configure_builtin_categories(config)

                mock_list.assert_called_once()
                mock_update.assert_called_once_with(
                    name="guide",
                    dir="/custom/guides",
                    patterns=["default.md"],  # Should use existing patterns when file is "none"
                    description="Project guidelines",
                )
