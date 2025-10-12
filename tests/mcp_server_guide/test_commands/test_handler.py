"""Tests for command handler functionality."""

import pytest
from unittest.mock import patch
from mcp_server_guide.commands.handler import CommandHandler


@pytest.mark.asyncio
async def test_execute_guide_command_all():
    """Test executing /guide command (show all guides)."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.get_all_guides") as mock_get_all:
        mock_get_all.return_value = {"guide": "content", "lang": "content"}

        result = await handler.execute_command("guide", [])

        assert result["success"] is True
        assert "guide" in result["content"]
        mock_get_all.assert_called_once()


@pytest.mark.asyncio
async def test_execute_guide_command_specific_category():
    """Test executing /guide <category> command."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_category:
        mock_get_category.return_value = {"success": True, "content": "lang content"}

        result = await handler.execute_command("guide", ["lang"])

        assert result["success"] is True
        assert result["content"] == "lang content"
        mock_get_category.assert_called_once_with("lang", None)


@pytest.mark.asyncio
async def test_execute_guide_command_all_explicit():
    """Test executing /guide all command."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.get_all_guides") as mock_get_all:
        mock_get_all.return_value = {"guide": "content", "lang": "content"}

        result = await handler.execute_command("guide", ["all"])

        assert result["success"] is True
        mock_get_all.assert_called_once()


@pytest.mark.asyncio
async def test_execute_category_shortcut_exists():
    """Test executing /<category> shortcut when category exists."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_category:
        mock_get_category.return_value = {"success": True, "content": "lang content"}

        result = await handler.execute_command("lang", [])

        assert result["success"] is True
        assert result["content"] == "lang content"
        mock_get_category.assert_called_once_with("lang", None)


@pytest.mark.asyncio
async def test_execute_category_shortcut_not_exists():
    """Test executing /<category> shortcut when category doesn't exist."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_category:
        mock_get_category.return_value = {"success": False, "error": "Category not found"}

        result = await handler.execute_command("nonexistent", [])

        assert result["success"] is False
        assert "Category not found" in result["error"]


@pytest.mark.asyncio
async def test_execute_unknown_command():
    """Test executing unknown command returns error."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_category:
        mock_get_category.return_value = {"success": False, "error": "Category not found"}

        result = await handler.execute_command("unknown", [])

        assert result["success"] is False
        assert "Category not found" in result["error"]


@pytest.mark.asyncio
async def test_execute_guide_new_with_defaults():
    """Test executing /guide-new with default values."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.add_category") as mock_add:
        mock_add.return_value = {"success": True, "message": "Category created"}

        result = await handler.execute_command("guide-new", ["typescript"], {})

        assert result["success"] is True
        mock_add.assert_called_once_with(
            name="typescript", dir="typescript", patterns=["*.md"], description="", project=None, auto_load=False
        )


@pytest.mark.asyncio
async def test_execute_guide_new_with_custom_params():
    """Test executing /guide-new with custom parameters."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.add_category") as mock_add:
        mock_add.return_value = {"success": True, "message": "Category created"}

        params = {"dir": "lang/ts", "patterns": ["*.ts", "*.tsx"], "auto-load": True}
        result = await handler.execute_command("guide-new", ["typescript"], params)

        assert result["success"] is True
        mock_add.assert_called_once_with(
            name="typescript", dir="lang/ts", patterns=["*.ts", "*.tsx"], description="", project=None, auto_load=True
        )


@pytest.mark.asyncio
async def test_execute_guide_edit():
    """Test executing /guide-edit command."""
    handler = CommandHandler()

    with (
        patch("mcp_server_guide.commands.handler.list_categories") as mock_list,
        patch("mcp_server_guide.commands.handler.update_category") as mock_update,
    ):
        mock_list.return_value = {
            "builtin_categories": {},
            "custom_categories": {
                "typescript": {
                    "dir": "lang/ts",
                    "patterns": ["*.ts"],
                    "description": "TypeScript files",
                    "auto_load": False,
                }
            },
        }
        mock_update.return_value = {"success": True, "message": "Category updated"}

        params = {"patterns": ["*.ts", "*.tsx", "*.d.ts"]}
        result = await handler.execute_command("guide-edit", ["typescript"], params)

        assert result["success"] is True
        mock_update.assert_called_once_with(
            name="typescript",
            dir="lang/ts",  # Should use existing value
            patterns=["*.ts", "*.tsx", "*.d.ts"],  # Should use new value
            description="TypeScript files",  # Should use existing value
            project=None,
            auto_load=False,  # Should use existing value
        )


@pytest.mark.asyncio
async def test_execute_guide_del():
    """Test executing /guide-del command."""
    handler = CommandHandler()

    result = await handler.execute_command("guide-del", ["typescript"], {})

    assert result["success"] is True
    assert "confirm" in result  # Should ask for confirmation
    assert "typescript" in result["confirm"]


# New colon syntax tests


@pytest.mark.asyncio
async def test_execute_guide_colon_category():
    """Test executing /guide:category command."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_category:
        mock_get_category.return_value = {"success": True, "content": "lang content"}

        result = await handler.execute_command("guide", [], {}, "lang")

        assert result["success"] is True
        assert result["content"] == "lang content"
        mock_get_category.assert_called_once_with("lang", None)


@pytest.mark.asyncio
async def test_execute_guide_colon_new():
    """Test executing /guide:new command."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.add_category") as mock_add:
        mock_add.return_value = {"success": True, "message": "Category created"}

        params = {"dir": "lang/ts", "patterns": ["*.ts", "*.tsx"]}
        result = await handler.execute_command("guide", ["typescript"], params, "new")

        assert result["success"] is True
        mock_add.assert_called_once_with(
            name="typescript", dir="lang/ts", patterns=["*.ts", "*.tsx"], description="", project=None, auto_load=False
        )


@pytest.mark.asyncio
async def test_execute_guide_help():
    """Test executing /guide:help command."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.list_categories") as mock_list:
        mock_list.return_value = {
            "builtin_categories": [{"name": "guide"}, {"name": "lang"}, {"name": "context"}],
            "custom_categories": [{"name": "typescript"}],
        }

        result = await handler.execute_command("guide", [], {}, "help")

        assert result["success"] is True
        assert "help" in result
        assert "commands" in result["help"]
        assert "categories" in result["help"]
