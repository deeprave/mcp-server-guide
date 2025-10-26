"""Tests for commands/handler.py error scenarios and edge cases."""

import pytest
from unittest.mock import patch

from mcp_server_guide.commands.handler import CommandHandler


class TestCommandHandlerErrors:
    """Test error handling in CommandHandler."""

    @pytest.fixture
    def handler(self):
        """Create CommandHandler instance."""
        return CommandHandler()

    @pytest.mark.asyncio
    async def test_unknown_command_error(self, handler):
        """Test unknown command error path."""
        with patch.object(handler, "_try_content_shortcut") as mock_shortcut:
            mock_shortcut.return_value = {"success": False, "error": "Category not found: unknown"}

            result = await handler.execute_command("unknown", [], {})

            assert result["success"] is False
            assert "Category not found" in result["error"]

    @pytest.mark.asyncio
    async def test_help_command_execution(self, handler):
        """Test help command execution."""
        with patch.object(handler, "_execute_help_command") as mock_help:
            mock_help.return_value = {"success": True, "help": {"commands": {}}}

            result = await handler._execute_help_command()

            assert result["success"]

    @pytest.mark.asyncio
    async def test_category_add_error_path(self, handler):
        """Test category add error handling."""
        with patch("mcp_server_guide.commands.handler.add_category") as mock_add:
            mock_add.return_value = {"success": False, "error": "Missing required parameters"}

            result = await handler.execute_command("category", ["add"], {})

            assert result["success"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_category_update_error_path(self, handler):
        """Test category update error handling."""
        with patch("mcp_server_guide.commands.handler.update_category") as mock_update:
            mock_update.return_value = {"success": False, "error": "Update failed"}

            result = await handler.execute_command("category", ["update", "test"], {})

            assert result["success"] is False
            assert "Update failed" in result["error"]

    @pytest.mark.asyncio
    async def test_category_remove_error_path(self, handler):
        """Test category remove error handling."""
        with patch("mcp_server_guide.commands.handler.remove_category") as mock_remove:
            mock_remove.return_value = {"success": False, "error": "Remove failed"}

            result = await handler.execute_command("category", ["remove", "test"], {})

            assert result["success"] is False
            assert "Remove failed" in result["error"]

    @pytest.mark.asyncio
    async def test_category_command_error(self, handler):
        """Test category shortcut error handling."""
        with patch.object(handler, "_try_content_shortcut") as mock_shortcut:
            mock_shortcut.return_value = {"success": False, "error": "Category not found"}

            result = await handler.execute_command("nonexistent", [])

            assert result["success"] is False
            assert "Category not found" in result["error"]

    @pytest.mark.asyncio
    async def test_guide_command_with_args(self, handler):
        """Test /guide with arguments."""
        with patch.object(handler, "_execute_guide_command") as mock_guide:
            mock_guide.return_value = {"success": True, "content": "All guides"}

            result = await handler.execute_command("guide", ["all"], {})

            assert result["success"] is True
            mock_guide.assert_called_once_with(["all"])

    @pytest.mark.asyncio
    async def test_guide_command_no_args(self, handler):
        """Test /guide with no arguments."""
        with patch.object(handler, "_execute_guide_command") as mock_guide:
            mock_guide.return_value = {"success": True, "content": "Default guide"}

            result = await handler.execute_command("guide", [], {})

            assert result["success"] is True
            mock_guide.assert_called_once_with([])

    @pytest.mark.asyncio
    async def test_category_add_success_path(self, handler):
        """Test category add success path."""
        with patch("mcp_server_guide.commands.handler.add_category") as mock_add:
            mock_add.return_value = {"success": True, "message": "Category created"}

            result = await handler.execute_command("category", ["add", "test", "test/", "*.md"], {})

            assert result["success"] is True
            mock_add.assert_called_once_with("test", "test/", ["*.md"], None)

    @pytest.mark.asyncio
    async def test_category_shortcut_execution(self, handler):
        """Test category shortcut execution."""
        with patch.object(handler, "_try_content_shortcut") as mock_shortcut:
            mock_shortcut.return_value = {"success": True, "content": "Category content"}

            result = await handler.execute_command("python", [])

            assert result["success"] is True
            mock_shortcut.assert_called_once_with("python", [])
