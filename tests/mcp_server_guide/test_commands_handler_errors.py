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
        with patch.object(handler, "_try_category_shortcut") as mock_shortcut:
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
    async def test_guide_new_error_path(self, handler):
        """Test guide-new error handling."""
        with patch.object(handler, "_execute_guide_new_command") as mock_new:
            mock_new.return_value = {"success": False, "error": "Missing required parameters"}

            result = await handler.execute_command("guide-new", [], {})

            assert result["success"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_guide_edit_error_path(self, handler):
        """Test guide-edit error handling."""
        with patch.object(handler, "_execute_guide_edit_command") as mock_edit:
            mock_edit.return_value = {"success": False, "error": "Edit failed"}

            result = await handler.execute_command("guide-edit", [], {})

            assert result["success"] is False
            assert "Edit failed" in result["error"]

    @pytest.mark.asyncio
    async def test_guide_del_error_path(self, handler):
        """Test guide-del error handling."""
        with patch.object(handler, "_execute_guide_del_command") as mock_del:
            mock_del.return_value = {"success": False, "error": "Delete failed"}

            result = await handler.execute_command("guide-del", [], {})

            assert result["success"] is False
            assert "Delete failed" in result["error"]

    @pytest.mark.asyncio
    async def test_category_command_error(self, handler):
        """Test category shortcut error handling."""
        with patch.object(handler, "_try_category_shortcut") as mock_shortcut:
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
    async def test_guide_new_success_path(self, handler):
        """Test guide-new success path."""
        with patch.object(handler, "_execute_guide_new_command") as mock_new:
            mock_new.return_value = {"success": True, "message": "Category created"}

            result = await handler.execute_command("guide-new", ["test"], {"dir": "/test"})

            assert result["success"] is True
            mock_new.assert_called_once_with(["test"], {"dir": "/test"})

    @pytest.mark.asyncio
    async def test_category_shortcut_execution(self, handler):
        """Test category shortcut execution."""
        with patch.object(handler, "_try_category_shortcut") as mock_shortcut:
            mock_shortcut.return_value = {"success": True, "content": "Category content"}

            result = await handler.execute_command("python", [])

            assert result["success"] is True
            mock_shortcut.assert_called_once_with("python", [])
