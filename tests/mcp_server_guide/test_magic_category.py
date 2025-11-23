"""Tests for category name validation (formerly magic category tests)."""

import pytest

from mcp_server_guide.tools.category_tools import add_category, remove_category, update_category


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
        result = await update_category(invalid_name, description="test")
        assert not result.get("success", True), f"update_category should reject '{invalid_name}'"
        assert "Invalid category name" in result.get("error", "")

        # Test remove_category
        result = await remove_category(invalid_name)
        assert not result.get("success", True), f"remove_category should reject '{invalid_name}'"
        assert "Invalid category name" in result.get("error", "")
