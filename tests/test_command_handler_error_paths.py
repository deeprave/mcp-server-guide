"""Tests for command handler error conditions and edge cases."""

import pytest
from unittest.mock import patch
from mcp_server_guide.commands.handler import CommandHandler


class TestCommandHandlerErrors:
    """Tests for command handler error conditions and edge cases."""

    @pytest.fixture
    def handler(self):
        """Create a command handler instance."""
        return CommandHandler()

    @pytest.mark.asyncio
    async def test_execute_guide_command_invalid_name(self, handler):
        """Test guide command with invalid name."""
        result = await handler._execute_guide_command(["invalid@name"])

        assert result["success"] is False
        assert "Invalid category/collection name" in result["error"]
        assert "invalid@name" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_guide_command_whitespace_only_name(self, handler):
        """Test guide command with whitespace-only name."""
        result = await handler._execute_guide_command(["   "])

        assert result["success"] is False
        assert "Invalid category/collection name" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_guide_command_empty_name(self, handler):
        """Test guide command with empty name."""
        result = await handler._execute_guide_command([""])

        assert result["success"] is False
        assert "Invalid category/collection name" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_guide_command_category_success(self, handler):
        """Test guide command finding category successfully."""
        with patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_cat:
            mock_get_cat.return_value = {"success": True, "content": "Category content"}

            result = await handler._execute_guide_command(["valid-name"])

            assert result["success"] is True
            assert result["content"] == "Category content"
            mock_get_cat.assert_called_once_with("valid-name", None)

    @pytest.mark.asyncio
    async def test_execute_guide_command_collection_fallback(self, handler):
        """Test guide command falling back to collection when category fails."""
        with patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_cat:
            with patch("mcp_server_guide.tools.collection_tools.get_collection_content") as mock_get_col:
                mock_get_cat.return_value = {"success": False}
                mock_get_col.return_value = {"success": True, "content": "Collection content"}

                result = await handler._execute_guide_command(["valid-name"])

                assert result["success"] is True
                assert result["content"] == "Collection content"
                mock_get_cat.assert_called_once_with("valid-name", None)
                mock_get_col.assert_called_once_with("valid-name", None)

    @pytest.mark.asyncio
    async def test_execute_guide_command_both_fail(self, handler):
        """Test guide command when both category and collection fail."""
        with patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_cat:
            with patch("mcp_server_guide.tools.collection_tools.get_collection_content") as mock_get_col:
                mock_get_cat.return_value = {"success": False}
                mock_get_col.return_value = {"success": False}

                result = await handler._execute_guide_command(["valid-name"])

                assert result["success"] is False
                assert "not found" in result["error"]
                assert "valid-name" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_guide_command_exception(self, handler):
        """Test guide command exception handling."""
        with patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_cat:
            mock_get_cat.side_effect = Exception("Test error")

            result = await handler._execute_guide_command(["valid-name"])

            assert result["success"] is False
            assert "Error executing guide command" in result["error"]
            assert "Test error" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_category_command_update_insufficient_args(self, handler):
        """Test category update command with insufficient arguments."""
        result = await handler._execute_category_command(["update"], {})

        assert result["success"] is False
        assert "Usage: category update" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_category_command_add_to_insufficient_args(self, handler):
        """Test category add-to command with insufficient arguments."""
        result = await handler._execute_category_command(["add-to"], {})

        assert result["success"] is False
        assert "Usage: category add-to" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_category_command_add_to_missing_patterns(self, handler):
        """Test category add-to command with missing patterns."""
        result = await handler._execute_category_command(["add-to", "name"], {})

        assert result["success"] is False
        assert "Usage: category add-to" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_category_command_remove_from_insufficient_args(self, handler):
        """Test category remove-from command with insufficient arguments."""
        result = await handler._execute_category_command(["remove-from"], {})

        assert result["success"] is False
        assert "Usage: category remove-from" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_category_command_remove_insufficient_args(self, handler):
        """Test category remove command with insufficient arguments."""
        result = await handler._execute_category_command(["remove"], {})

        assert result["success"] is False
        assert "Usage: category remove" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_category_command_update_with_params(self, handler):
        """Test category update command with parameters."""
        with patch("mcp_server_guide.commands.handler.update_category") as mock_update:
            mock_update.return_value = {"success": True}

            params = {"description": "New desc", "dir": "/new/path", "patterns": "*.py,*.js"}
            result = await handler._execute_category_command(["update", "test-cat"], params)

            assert result["success"] is True
            mock_update.assert_called_once_with(
                "test-cat", description="New desc", dir="/new/path", patterns=["*.py", "*.js"]
            )

    @pytest.mark.asyncio
    async def test_execute_category_command_add_to_success(self, handler):
        """Test category add-to command success."""
        with patch("mcp_server_guide.commands.handler.add_to_category") as mock_add:
            mock_add.return_value = {"success": True}

            result = await handler._execute_category_command(["add-to", "test-cat", "*.py", "*.js"], {})

            assert result["success"] is True
            mock_add.assert_called_once_with("test-cat", ["*.py", "*.js"])

    @pytest.mark.asyncio
    async def test_execute_category_command_remove_from_success(self, handler):
        """Test category remove-from command success."""
        with patch("mcp_server_guide.commands.handler.remove_from_category") as mock_remove:
            mock_remove.return_value = {"success": True}

            result = await handler._execute_category_command(["remove-from", "test-cat", "*.py"], {})

            assert result["success"] is True
            mock_remove.assert_called_once_with("test-cat", ["*.py"])

    @pytest.mark.asyncio
    async def test_execute_collection_command_update_insufficient_args(self, handler):
        """Test collection update command with insufficient arguments."""
        result = await handler._execute_collection_command(["update"], {})

        assert result["success"] is False
        assert "Usage: collection update" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_collection_command_add_to_insufficient_args(self, handler):
        """Test collection add-to command with insufficient arguments."""
        result = await handler._execute_collection_command(["add-to"], {})

        assert result["success"] is False
        assert "Usage: collection add-to" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_collection_command_remove_from_insufficient_args(self, handler):
        """Test collection remove-from command with insufficient arguments."""
        result = await handler._execute_collection_command(["remove-from"], {})

        assert result["success"] is False
        assert "Usage: collection remove-from" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_collection_command_remove_insufficient_args(self, handler):
        """Test collection remove command with insufficient arguments."""
        result = await handler._execute_collection_command(["remove"], {})

        assert result["success"] is False
        assert "Usage: collection remove" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_collection_command_list_verbose_flag(self, handler):
        """Test collection list command with verbose flag."""
        with patch("mcp_server_guide.commands.handler.list_collections") as mock_list:
            mock_list.return_value = {"success": True}

            result = await handler._execute_collection_command(["list", "-v"], {})

            assert result["success"] is True
            mock_list.assert_called_once_with(True)

    @pytest.mark.asyncio
    async def test_execute_collection_command_list_verbose_param(self, handler):
        """Test collection list command with verbose parameter."""
        with patch("mcp_server_guide.commands.handler.list_collections") as mock_list:
            mock_list.return_value = {"success": True}

            result = await handler._execute_collection_command(["list"], {"verbose": True})

            assert result["success"] is True
            mock_list.assert_called_once_with(True)
