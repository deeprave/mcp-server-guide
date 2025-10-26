"""Tests for command handler."""

import pytest
from unittest.mock import patch
from mcp_server_guide.commands.handler import CommandHandler


@pytest.mark.asyncio
async def test_execute_guide_command_no_args():
    """Test executing /guide command with no arguments shows all guides."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.get_all_guides") as mock_get_all:
        mock_get_all.return_value = {"guide": "content", "lang": "content"}

        result = await handler.execute_command("guide", [])

        assert result["success"] is True
        mock_get_all.assert_called_once()


@pytest.mark.asyncio
async def test_execute_guide_command_with_category():
    """Test executing /guide <category> command."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_category:
        mock_get_category.return_value = {"success": True, "content": "guide content"}

        result = await handler.execute_command("guide", ["guide"])

        assert result["success"] is True
        assert result["content"] == "guide content"


@pytest.mark.asyncio
async def test_execute_guide_command_fallback_to_collection():
    """Test executing /guide <name> falls back to collection if category not found."""
    handler = CommandHandler()

    with (
        patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_category,
        patch("mcp_server_guide.tools.collection_tools.get_collection_content") as mock_get_collection,
    ):
        mock_get_category.return_value = {"success": False, "error": "Category not found"}
        mock_get_collection.return_value = {"success": True, "content": "collection content"}

        result = await handler.execute_command("guide", ["docs"])

        assert result["success"] is True
        assert result["content"] == "collection content"


@pytest.mark.asyncio
async def test_content_shortcut_missing_both():
    """Test content shortcut when neither category nor collection exists."""
    handler = CommandHandler()

    with (
        patch("mcp_server_guide.commands.handler.get_category_content") as mock_cat,
        patch("mcp_server_guide.tools.collection_tools.get_collection_content") as mock_coll,
    ):
        # Both collection and category fail
        mock_coll.return_value = {"success": False, "error": "Collection not found"}
        mock_cat.return_value = {"success": False, "error": "Category not found"}

        result = await handler.execute_command("nonexistent", [])

        assert result["success"] is False
        assert "not found" in result["error"].lower() or "does not exist" in result["error"].lower()


@pytest.mark.asyncio
async def test_execute_category_add_command():
    """Test executing /category add command."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.add_category") as mock_add:
        mock_add.return_value = {"success": True, "message": "Category created"}

        result = await handler.execute_command("category", ["add", "typescript", "ts/", "*.ts"], {})

        assert result["success"] is True
        mock_add.assert_called_once_with("typescript", "ts/", ["*.ts"], None)


@pytest.mark.asyncio
async def test_execute_category_add_command_invalid_name():
    """Test executing /category add command with invalid category name."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.add_category") as mock_add:
        mock_add.return_value = {"success": False, "error": "Invalid category name"}

        result = await handler.execute_command("category", ["add", "invalid name!", "docs/", "*.md"], {})

        assert result["success"] is False
        assert "Invalid category name" in result["error"]
        mock_add.assert_called_once_with("invalid name!", "docs/", ["*.md"], None)


@pytest.mark.asyncio
async def test_execute_category_add_command_name_at_length_limit():
    """Test executing /category add command with category name at the length limit."""
    handler = CommandHandler()
    max_length_name = "a" * 30  # Category name length limit is 30 characters

    with patch("mcp_server_guide.commands.handler.add_category") as mock_add:
        mock_add.return_value = {"success": True, "message": "Category created"}

        result = await handler.execute_command("category", ["add", max_length_name, "docs/", "*.md"], {})
        assert result["success"] is True
        mock_add.assert_called_once_with(max_length_name, "docs/", ["*.md"], None)


@pytest.mark.asyncio
async def test_execute_category_add_command_name_above_length_limit():
    """Test executing /category add command with category name just above the length limit."""
    handler = CommandHandler()
    above_limit_name = "b" * 31  # Just above the 30 character limit

    with patch("mcp_server_guide.commands.handler.add_category") as mock_add:
        mock_add.return_value = {"success": False, "error": "Category name exceeds maximum length"}

        result = await handler.execute_command("category", ["add", above_limit_name, "docs/", "*.md"], {})
        assert result["success"] is False
        mock_add.assert_called_once_with(above_limit_name, "docs/", ["*.md"], None)


@pytest.mark.asyncio
async def test_category_add_with_pattern_edge_cases():
    """Test /category add command with edge case patterns."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.add_category") as mock_add:
        mock_add.return_value = {"success": True, "message": "Category created"}

        # Test with whitespace-only patterns and duplicates
        result = await handler.execute_command("category", ["add", "test", "test/", "*.py", "   ", "*.py", "*.js"], {})

        assert result["success"] is True
        # Verify normalize_patterns was called and handled whitespace/duplicates
        mock_add.assert_called_once()
        args = mock_add.call_args[0]
        patterns = args[2]  # Third argument is patterns
        # Should have deduplicated and removed whitespace-only patterns
        assert "*.py" in patterns
        assert "*.js" in patterns
        assert "   " not in patterns
    """Test category add with pattern edge cases."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.add_category") as mock_add:
        mock_add.return_value = {"success": True, "message": "Category created"}

        # Test with multiple patterns including empty ones (which should be filtered)
        await handler.execute_command("category", ["add", "test", "/path", "*.py", "", "*.js"], {"description": "Test"})

        # Verify normalize_patterns was called and empty patterns filtered
        mock_add.assert_called_once()
        args = mock_add.call_args[0]
        patterns = args[2]  # Third argument should be patterns
        assert "*.py" in patterns
        assert "*.js" in patterns
        assert "" not in patterns  # Empty patterns should be filtered out


@pytest.mark.asyncio
async def test_category_add_with_special_character_patterns():
    """Test /category add command with patterns containing only special characters."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.add_category") as mock_add:
        mock_add.return_value = {"success": True, "message": "Category created"}

        # Test with special character patterns
        result = await handler.execute_command("category", ["add", "test", "test/", "***", "???", "*.py"], {})

        assert result["success"] is True
        # Verify special character patterns are preserved
        mock_add.assert_called_once()
        args = mock_add.call_args[0]
        patterns = args[2]  # Third argument is patterns
        assert "***" in patterns
        assert "???" in patterns
        assert "*.py" in patterns


@pytest.mark.asyncio
async def test_category_add_with_quoted_patterns():
    """Test category add with quoted patterns containing spaces."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.add_category") as mock_add:
        mock_add.return_value = {"success": True, "message": "Category created"}

        # Test with quoted pattern containing spaces
        result = await handler.execute_command("category", ["add", "test", "/path", '"my pattern"', "*.py"], {})

        assert result["success"] is True
        # Should parse quoted pattern correctly
        args = mock_add.call_args[0]
        patterns = args[2]
        assert "my pattern" in patterns
        assert "*.py" in patterns


@pytest.mark.asyncio
async def test_execute_category_update_command():
    """Test executing /category update command."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.update_category") as mock_update:
        mock_update.return_value = {"success": True, "message": "Category updated"}

        result = await handler.execute_command(
            "category", ["update", "typescript"], {"description": "TypeScript files"}
        )

        assert result["success"] is True
        mock_update.assert_called_once_with("typescript", description="TypeScript files", dir=None, patterns=None)


@pytest.mark.asyncio
async def test_execute_category_update_conflicting_patterns():
    """Test category update with conflicting pattern options."""
    handler = CommandHandler()

    # The validation should happen before any category existence check
    result = await handler.execute_command(
        "category", ["update", "typescript"], {"patterns": "*.ts", "clear-patterns": True}
    )

    assert result["success"] is False
    assert "Conflicting pattern options" in result["error"]
    assert "Use either --clear-patterns to remove all patterns or --patterns to set new patterns" in result["error"]


@pytest.mark.asyncio
async def test_execute_category_update_clear_patterns_only():
    """Test category update with only --clear-patterns clears all patterns."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.update_category") as mock_update:
        mock_update.return_value = {"success": True, "message": "Category updated"}

        result = await handler.execute_command("category", ["update", "typescript"], {"clear-patterns": True})

        assert result["success"] is True
        assert "error" not in result
        mock_update.assert_called_once_with("typescript", description=None, dir=None, patterns=[])


@pytest.mark.asyncio
async def test_execute_category_update_patterns_empty_string():
    """Test category update with --patterns as empty string does not clear patterns."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.update_category") as mock_update:
        mock_update.return_value = {"success": True, "message": "Category updated"}

        result = await handler.execute_command("category", ["update", "typescript"], {"patterns": ""})

        assert result["success"] is True
        # Empty string should now clear patterns (documented behavior change)
        mock_update.assert_called_once_with("typescript", description=None, dir=None, patterns=[])


@pytest.mark.asyncio
async def test_execute_category_update_patterns_none():
    """Test category update with --patterns as None clears patterns."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.update_category") as mock_update:
        mock_update.return_value = {"success": True, "message": "Category updated"}

        result = await handler.execute_command("category", ["update", "typescript"], {"patterns": None})

        assert result["success"] is True
        # None should be treated as empty string and clear patterns
        mock_update.assert_called_once_with("typescript", description=None, dir=None, patterns=[])


@pytest.mark.asyncio
async def test_execute_category_update_patterns_empty_list():
    """Test category update with --patterns as an empty list clears patterns."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.update_category") as mock_update:
        mock_update.return_value = {"success": True, "message": "Category updated"}

        result = await handler.execute_command("category", ["update", "typescript"], {"patterns": []})

        assert result["success"] is True
        # Empty list should clear patterns
        mock_update.assert_called_once_with("typescript", description=None, dir=None, patterns=[])


@pytest.mark.asyncio
async def test_execute_category_update_patterns_whitespace():
    """Test category update with --patterns as whitespace string clears patterns."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.update_category") as mock_update:
        mock_update.return_value = {"success": True, "message": "Category updated"}

        result = await handler.execute_command("category", ["update", "typescript"], {"patterns": "   "})

        assert result["success"] is True
        # Whitespace string should clear patterns (same as empty string)
        mock_update.assert_called_once_with("typescript", description=None, dir=None, patterns=[])


@pytest.mark.asyncio
async def test_execute_category_update_description_only():
    """Test category update with only description field."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.update_category") as mock_update:
        mock_update.return_value = {"success": True, "message": "Category updated"}

        result = await handler.execute_command(
            "category", ["update", "typescript"], {"description": "TypeScript files"}
        )

        assert result["success"] is True
        # Only description should be updated, other fields None
        mock_update.assert_called_once_with("typescript", description="TypeScript files", dir=None, patterns=None)


@pytest.mark.asyncio
async def test_execute_unknown_command_with_args():
    """Test executing unknown command with arguments returns error."""
    handler = CommandHandler()

    with (
        patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_category,
        patch("mcp_server_guide.tools.collection_tools.get_collection_content") as mock_get_collection,
    ):
        mock_get_category.return_value = {"success": False, "error": "Category not found"}
        mock_get_collection.return_value = {"success": False, "error": "Collection not found"}

        result = await handler.execute_command("foobar", ["arg1"])

        assert result["success"] is False
        assert "Category or collection 'foobar' not found" in result["error"]


@pytest.mark.asyncio
async def test_execute_category_update_partial_fields():
    """Test category update affecting only one field."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.update_category") as mock_update:
        mock_update.return_value = {"success": True, "message": "Category updated"}

        # Test updating only directory
        result = await handler.execute_command("category", ["update", "typescript"], {"dir": "/new/path"})

        assert result["success"] is True
        mock_update.assert_called_once_with("typescript", description=None, dir="/new/path", patterns=None)


@pytest.mark.asyncio
async def test_execute_category_list_command():
    """Test executing /category list command."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.list_categories") as mock_list:
        mock_list.return_value = {"success": True, "categories": {}}

        result = await handler.execute_command("category", ["list"], {})

        assert result["success"] is True
        mock_list.assert_called_once_with(False)


@pytest.mark.asyncio
async def test_execute_collection_add_command():
    """Test executing /collection add command."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.add_collection") as mock_add:
        mock_add.return_value = {"success": True, "message": "Collection created"}

        result = await handler.execute_command("collection", ["add", "docs", "guide", "lang"], {})

        assert result["success"] is True
        mock_add.assert_called_once_with("docs", ["guide", "lang"], None)


@pytest.mark.asyncio
async def test_execute_collection_add_command_invalid_name():
    """Test executing /collection add command with invalid collection name."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.add_collection") as mock_add:
        mock_add.return_value = {"success": False, "error": "Invalid collection name"}

        result = await handler.execute_command("collection", ["add", "invalid name!", "guide", "lang"], {})

        assert result["success"] is False
        assert "Invalid collection name" in result["error"]
        mock_add.assert_called_once_with("invalid name!", ["guide", "lang"], None)


@pytest.mark.asyncio
async def test_execute_collection_add_command_duplicate_categories():
    """Test /collection add command with duplicate category names (case-insensitive)."""
    handler = CommandHandler()

    # Simulate error for duplicate categories
    with patch("mcp_server_guide.commands.handler.add_collection") as mock_add:
        mock_add.return_value = {"success": False, "message": "Duplicate category names: guide, Guide"}

        result = await handler.execute_command("collection", ["add", "docs", "guide", "Guide"], {})

        assert result["success"] is False
        assert "duplicate" in result["message"].lower()
        mock_add.assert_called_once_with("docs", ["guide", "Guide"], None)


@pytest.mark.asyncio
async def test_execute_collection_add_command_nonexistent_categories():
    """Test /collection add command with non-existent category names."""
    handler = CommandHandler()

    # Simulate error for non-existent categories
    with patch("mcp_server_guide.commands.handler.add_collection") as mock_add:
        mock_add.return_value = {"success": False, "message": "Non-existent categories: unknown"}

        result = await handler.execute_command("collection", ["add", "docs", "unknown"], {})

        assert result["success"] is False
        assert "non-existent" in result["message"].lower()
        mock_add.assert_called_once_with("docs", ["unknown"], None)


@pytest.mark.asyncio
async def test_execute_collection_add_command_mixed_categories():
    """Test /collection add command with a mix of existent and non-existent category names."""
    handler = CommandHandler()

    # Simulate error for non-existent categories, with some existing
    with patch("mcp_server_guide.commands.handler.add_collection") as mock_add:
        mock_add.return_value = {"success": False, "message": "Non-existent categories: unknown, missing"}

        result = await handler.execute_command("collection", ["add", "docs", "guide", "unknown", "missing"], {})

        assert result["success"] is False
        assert "non-existent" in result["message"].lower()
        assert "unknown" in result["message"].lower()
        assert "missing" in result["message"].lower()
        mock_add.assert_called_once_with("docs", ["guide", "unknown", "missing"], None)


@pytest.mark.asyncio
async def test_execute_collection_add_command_empty_categories():
    """Test /collection add command with empty category list."""
    handler = CommandHandler()

    # When no categories are provided, the command handler returns usage info
    result = await handler.execute_command("collection", ["add", "docs"], {})

    assert result["success"] is False
    assert "usage" in result["error"].lower()


@pytest.mark.asyncio
async def test_execute_collection_add_command_empty_string_categories():
    """Test /collection add command with categories as an empty string."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.add_collection") as mock_add:
        mock_add.return_value = {"success": False, "error": "Collection must have at least one valid category"}

        # Categories argument is an empty string
        result = await handler.execute_command("collection", ["add", "docs", ""], {})

        assert result["success"] is False
        assert "valid category" in result["error"].lower()


@pytest.mark.asyncio
async def test_execute_collection_add_command_whitespace_categories():
    """Test /collection add command with categories as whitespace."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.add_collection") as mock_add:
        mock_add.return_value = {"success": False, "error": "Collection must have at least one valid category"}

        # Categories argument is a string with only whitespace
        result = await handler.execute_command("collection", ["add", "docs", "   "], {})

        assert result["success"] is False
        assert "valid category" in result["error"].lower()


@pytest.mark.asyncio
async def test_execute_collection_add_command_none_categories():
    """Test /collection add command with categories argument as None."""
    handler = CommandHandler()

    # Simulate categories argument as None
    result = await handler.execute_command("collection", ["add", "docs", None], {})

    assert result["success"] is False
    # Accept either 'usage' or a specific error message about categories being None
    assert "usage" in result.get("error", "").lower() or "category" in result.get("error", "").lower()


@pytest.mark.asyncio
async def test_execute_collection_list_command():
    """Test executing /collection list command."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.list_collections") as mock_list:
        mock_list.return_value = {"success": True, "collections": {}}

        result = await handler.execute_command("collection", ["list"], {})

        assert result["success"] is True
        mock_list.assert_called_once_with(False)


@pytest.mark.asyncio
async def test_execute_collection_list_command_verbose():
    """Test executing /collection list command with verbose=True includes category details."""
    handler = CommandHandler()

    # Example category details for verbose output
    collections_data = {
        "success": True,
        "collections": {"docs": {"categories": ["guide", "lang"], "description": "Documentation collection"}},
    }

    with patch("mcp_server_guide.commands.handler.list_collections") as mock_list:
        mock_list.return_value = collections_data

        result = await handler.execute_command("collection", ["list", "--verbose"], {})

        assert result["success"] is True
        assert "docs" in result["collections"]
        assert "categories" in result["collections"]["docs"]
        assert result["collections"]["docs"]["categories"] == ["guide", "lang"]
        mock_list.assert_called_once_with(True)


@pytest.mark.asyncio
async def test_execute_category_shortcut_exists():
    """Test executing /<category> shortcut when category exists."""
    handler = CommandHandler()

    with patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_category:
        mock_get_category.return_value = {"success": True, "content": "lang content"}

        result = await handler.execute_command("lang", [])

        assert result["success"] is True
        assert result["content"] == "lang content"


@pytest.mark.asyncio
async def test_execute_category_shortcut_not_exists():
    """Test executing /<category> shortcut when category doesn't exist."""
    handler = CommandHandler()

    with (
        patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_category,
        patch("mcp_server_guide.tools.collection_tools.get_collection_content") as mock_get_collection,
    ):
        mock_get_category.return_value = {"success": False, "error": "Category not found"}
        mock_get_collection.return_value = {"success": False, "error": "Collection not found"}

        result = await handler.execute_command("nonexistent", [])

        assert result["success"] is False
        assert "Category or collection 'nonexistent' not found" in result["error"]


@pytest.mark.asyncio
async def test_execute_unknown_command():
    """Test executing unknown command returns error."""
    handler = CommandHandler()

    with (
        patch("mcp_server_guide.commands.handler.get_category_content") as mock_get_category,
        patch("mcp_server_guide.tools.collection_tools.get_collection_content") as mock_get_collection,
    ):
        mock_get_category.return_value = {"success": False, "error": "Category not found"}
        mock_get_collection.return_value = {"success": False, "error": "Collection not found"}

        result = await handler.execute_command("unknown", [])

        assert result["success"] is False
        assert "Category or collection 'unknown' not found" in result["error"]


@pytest.mark.asyncio
async def test_execute_category_command_missing_subcommand():
    """Test executing /category without subcommand returns error."""
    handler = CommandHandler()

    result = await handler.execute_command("category", [], {})

    assert result["success"] is False
    assert "Category subcommand required" in result["error"]


@pytest.mark.asyncio
async def test_execute_category_command_unknown_subcommand():
    """Test executing /category with unknown subcommand returns error."""
    handler = CommandHandler()

    result = await handler.execute_command("category", ["foo"], {})

    assert result["success"] is False
    assert "Unknown category subcommand" in result["error"]


@pytest.mark.asyncio
async def test_execute_collection_command_missing_subcommand():
    """Test executing /collection without subcommand returns error."""
    handler = CommandHandler()

    result = await handler.execute_command("collection", [], {})

    assert result["success"] is False
    assert "Collection subcommand required" in result["error"]
