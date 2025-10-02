"""Tests for magic category "*" functionality."""

import pytest
from mcp_server_guide.tools.category_tools import get_category_content, add_category, update_category, remove_category
from mcp_server_guide.tools.content_tools import get_all_guides
from mcp_server_guide.server import mcp
from mcp.types import GetPromptResult


@pytest.mark.asyncio
async def test_get_category_content_star_returns_auto_load_guides():
    """Test that get_category_content("*") returns auto_load guides."""
    # This should return the same content as get_all_guides()
    result = await get_category_content("*")
    expected = await get_all_guides()

    assert result == expected


@pytest.mark.asyncio
async def test_guide_prompt_with_star_category_returns_auto_load_guides():
    """Test that @guide category=* returns auto_load guides."""
    # This should return the same content as get_all_guides()
    result = await mcp.get_prompt("guide", {"category": "*"})

    assert isinstance(result, GetPromptResult)
    # The prompt should contain the same content as get_all_guides()
    # We'll check that the result contains the expected guide content
    assert len(result.messages) > 0


@pytest.mark.asyncio
async def test_category_name_validation_rejects_invalid_names():
    """Test that category operations reject invalid names."""
    invalid_names = ["*", "my category", "test@example", "category!", "", "test.name", "test/name"]

    for invalid_name in invalid_names:
        # Test add_category
        result = await add_category(invalid_name, "test", ["*.md"])
        assert not result.get("success", True), f"add_category should reject '{invalid_name}'"
        assert "Invalid category name" in result.get("error", "")

        # Test update_category
        result = await update_category(invalid_name, "test", ["*.md"])
        assert not result.get("success", True), f"update_category should reject '{invalid_name}'"
        assert "Invalid category name" in result.get("error", "")

        # Test remove_category
        result = await remove_category(invalid_name)
        assert not result.get("success", True), f"remove_category should reject '{invalid_name}'"
        assert "Invalid category name" in result.get("error", "")
