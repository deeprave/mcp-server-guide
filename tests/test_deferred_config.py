"""Tests for deferred configuration functionality."""

from unittest.mock import patch
from mcp_server_guide.main import configure_builtin_categories


class TestDeferredConfiguration:
    """Test deferred configuration functionality."""

    async def test_configure_builtin_categories_with_guidesdir(self):
        """Test configure_builtin_categories with guidesdir parameter."""
        config = {"guidesdir": "/custom/guides", "guide": "custom-guide"}

        mock_categories_result = {
            "success": True,
            "categories": {
                "builtin_categories": [
                    {
                        "name": "guide",
                        "dir": "/default/guides",
                        "patterns": ["*.md"],
                        "description": "Project guidelines",
                    }
                ]
            },
        }

        async def mock_list_categories():
            return mock_categories_result

        async def mock_update_category(**kwargs):
            pass

        with patch(
            "mcp_server_guide.tools.category_tools.list_categories", side_effect=mock_list_categories
        ) as mock_list:
            with patch(
                "mcp_server_guide.tools.category_tools.update_category", side_effect=mock_update_category
            ) as mock_update:
                await configure_builtin_categories(config)

                mock_list.assert_called_once()
                mock_update.assert_called_once_with(
                    name="guide", dir="/custom/guides", patterns=["custom-guide.md"], description="Project guidelines"
                )

    async def test_configure_builtin_categories_with_langsdir(self):
        """Test configure_builtin_categories with langsdir parameter."""
        config = {"langsdir": "/custom/langs", "lang": "rust"}

        mock_categories_result = {
            "success": True,
            "categories": {
                "builtin_categories": [
                    {
                        "name": "lang",
                        "dir": "/default/langs",
                        "patterns": ["*.md"],
                        "description": "Language guidelines",
                    }
                ]
            },
        }

        async def mock_list_categories():
            return mock_categories_result

        async def mock_update_category(**kwargs):
            pass

        with patch(
            "mcp_server_guide.tools.category_tools.list_categories", side_effect=mock_list_categories
        ) as mock_list:
            with patch(
                "mcp_server_guide.tools.category_tools.update_category", side_effect=mock_update_category
            ) as mock_update:
                await configure_builtin_categories(config)

                mock_list.assert_called_once()
                mock_update.assert_called_once_with(
                    name="lang", dir="/custom/langs", patterns=["rust.md"], description="Language guidelines"
                )

    async def test_configure_builtin_categories_with_contextdir(self):
        """Test configure_builtin_categories with contextdir parameter."""
        config = {"contextdir": "/custom/context"}

        mock_categories_result = {
            "success": True,
            "categories": {
                "builtin_categories": [
                    {
                        "name": "context",
                        "dir": "/default/context",
                        "patterns": ["*.md"],
                        "description": "Project context",
                    }
                ]
            },
        }

        async def mock_list_categories():
            return mock_categories_result

        async def mock_update_category(**kwargs):
            pass

        with patch(
            "mcp_server_guide.tools.category_tools.list_categories", side_effect=mock_list_categories
        ) as mock_list:
            with patch(
                "mcp_server_guide.tools.category_tools.update_category", side_effect=mock_update_category
            ) as mock_update:
                await configure_builtin_categories(config)

                mock_list.assert_called_once()
                mock_update.assert_called_once_with(
                    name="context", dir="/custom/context", patterns=["*.md"], description="Project context"
                )

    async def test_configure_builtin_categories_no_matching_category(self):
        """Test configure_builtin_categories when no matching category exists."""
        config = {"guidesdir": "/custom/guides"}

        mock_categories_result = {
            "success": True,
            "categories": {
                "builtin_categories": []  # No matching categories
            },
        }

        async def mock_list_categories():
            return mock_categories_result

        with patch(
            "mcp_server_guide.tools.category_tools.list_categories", side_effect=mock_list_categories
        ) as mock_list:
            await configure_builtin_categories(config)

            mock_list.assert_called_once()
            # No update_category call should happen when no categories match

    async def test_configure_builtin_categories_list_categories_fails(self):
        """Test configure_builtin_categories when list_categories fails."""
        config = {"guidesdir": "/custom/guides"}

        async def failing_list_categories():
            raise Exception("List failed")

        with patch("mcp_server_guide.tools.category_tools.list_categories", new=failing_list_categories):
            with patch("mcp_server_guide.main.logger") as mock_logger:
                await configure_builtin_categories(config)

                # update_category should never be called when list_categories fails
                mock_logger.warning.assert_called_once_with("Failed to configure category guide")

    async def test_configure_builtin_categories_empty_config(self):
        """Test configure_builtin_categories with empty config."""
        config = {}

        # With empty config, no functions should be called
        await configure_builtin_categories(config)
        # No assertions needed - just verify it doesn't crash

    async def test_configure_builtin_categories_file_value_none(self):
        """Test configure_builtin_categories with file value set to 'none'."""
        config = {"guidesdir": "/custom/guides", "guide": "none"}

        mock_categories_result = {
            "success": True,
            "categories": {
                "builtin_categories": [
                    {
                        "name": "guide",
                        "dir": "/default/guides",
                        "patterns": ["default.md"],
                        "description": "Project guidelines",
                    }
                ]
            },
        }

        async def mock_list_categories():
            return mock_categories_result

        async def mock_update_category(**kwargs):
            pass

        with patch(
            "mcp_server_guide.tools.category_tools.list_categories", side_effect=mock_list_categories
        ) as mock_list:
            with patch(
                "mcp_server_guide.tools.category_tools.update_category", side_effect=mock_update_category
            ) as mock_update:
                await configure_builtin_categories(config)

                mock_list.assert_called_once()
                mock_update.assert_called_once_with(
                    name="guide",
                    dir="/custom/guides",
                    patterns=["default.md"],  # Should use existing patterns when file is "none"
                    description="Project guidelines",
                )

    async def test_configure_builtin_categories_with_file_only(self):
        """Test configure_builtin_categories with file parameter only."""
        config = {"guide": "custom-guide"}

        mock_categories_result = {
            "success": True,
            "categories": {
                "builtin_categories": [
                    {
                        "name": "guide",
                        "dir": "/default/guides",
                        "patterns": ["*.md"],
                        "description": "Project guidelines",
                    }
                ]
            },
        }

        async def mock_list_categories():
            return mock_categories_result

        async def mock_update_category(**kwargs):
            pass

        with patch(
            "mcp_server_guide.tools.category_tools.list_categories", side_effect=mock_list_categories
        ) as mock_list:
            with patch(
                "mcp_server_guide.tools.category_tools.update_category", side_effect=mock_update_category
            ) as mock_update:
                await configure_builtin_categories(config)

                mock_list.assert_called_once()
                mock_update.assert_called_once_with(
                    name="guide", dir="/default/guides", patterns=["custom-guide.md"], description="Project guidelines"
                )

    async def test_configure_builtin_categories_with_dir_only(self):
        """Test configure_builtin_categories with dir parameter only."""
        config = {"guidesdir": "/custom/guides"}

        mock_categories_result = {
            "success": True,
            "categories": {
                "builtin_categories": [
                    {
                        "name": "guide",
                        "dir": "/default/guides",
                        "patterns": ["*.md"],
                        "description": "Project guidelines",
                    }
                ]
            },
        }

        async def mock_list_categories():
            return mock_categories_result

        async def mock_update_category(**kwargs):
            pass

        with patch(
            "mcp_server_guide.tools.category_tools.list_categories", side_effect=mock_list_categories
        ) as mock_list:
            with patch(
                "mcp_server_guide.tools.category_tools.update_category", side_effect=mock_update_category
            ) as mock_update:
                await configure_builtin_categories(config)

                mock_list.assert_called_once()
                mock_update.assert_called_once_with(
                    name="guide", dir="/custom/guides", patterns=["*.md"], description="Project guidelines"
                )

    async def test_configure_builtin_categories_multiple_mappings(self):
        """Test configure_builtin_categories with multiple CLI mappings."""
        config = {"guidesdir": "/custom/guides", "langsdir": "/custom/langs", "contextdir": "/custom/context"}

        mock_categories_result = {
            "success": True,
            "categories": {
                "builtin_categories": [
                    {
                        "name": "guide",
                        "dir": "/default/guides",
                        "patterns": ["*.md"],
                        "description": "Project guidelines",
                    },
                    {
                        "name": "lang",
                        "dir": "/default/langs",
                        "patterns": ["*.md"],
                        "description": "Language guidelines",
                    },
                    {
                        "name": "context",
                        "dir": "/default/context",
                        "patterns": ["*.md"],
                        "description": "Project context",
                    },
                ]
            },
        }

        async def mock_list_categories():
            return mock_categories_result

        async def mock_update_category(**kwargs):
            pass

        with patch(
            "mcp_server_guide.tools.category_tools.list_categories", side_effect=mock_list_categories
        ) as mock_list:
            with patch(
                "mcp_server_guide.tools.category_tools.update_category", side_effect=mock_update_category
            ) as mock_update:
                await configure_builtin_categories(config)

                # Should be called once for each mapping
                assert mock_list.call_count == 3
                assert mock_update.call_count == 3

    async def test_configure_builtin_categories_category_not_found(self):
        """Test configure_builtin_categories when category doesn't exist in builtin_categories."""
        config = {"guidesdir": "/custom/guides"}

        mock_categories_result = {
            "success": True,
            "categories": {
                "builtin_categories": [
                    {
                        "name": "different_category",
                        "dir": "/default/other",
                        "patterns": ["*.md"],
                        "description": "Other category",
                    }
                ]
            },
        }

        async def mock_list_categories():
            return mock_categories_result

        async def mock_update_category(**kwargs):
            pass

        with patch(
            "mcp_server_guide.tools.category_tools.list_categories", side_effect=mock_list_categories
        ) as mock_list:
            with patch(
                "mcp_server_guide.tools.category_tools.update_category", side_effect=mock_update_category
            ) as mock_update:
                await configure_builtin_categories(config)

                mock_list.assert_called_once()
                # Should not call update_category when no matching category is found
                mock_update.assert_not_called()
