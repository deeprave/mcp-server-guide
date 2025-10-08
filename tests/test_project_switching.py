"""Tests for project switching and built-in category creation."""

from src.mcp_server_guide.tools.project_tools import _create_builtin_categories
from src.mcp_server_guide.session_tools import SessionManager


async def test_switch_to_new_project_creates_builtin_categories():
    """Test that switching to a new project creates built-in categories with auto_load=true."""
    # The test isolation fixture sets up ClientPath to use the test directory,
    # so we don't need to explicitly set the directory - it's already set up
    from mcp_server_guide.tools.project_tools import switch_project

    # Switch to a new project
    result = await switch_project("test-project-123")

    assert result["success"] is True
    assert result["project"] == "test-project-123"

    # Check that built-in categories were created
    from mcp_server_guide.tools.category_tools import list_categories

    categories_result = await list_categories()

    assert categories_result["success"] is True

    # Should have some built-in categories created
    builtin_categories = categories_result["builtin_categories"]
    assert len(builtin_categories) > 0, "Should have created some builtin categories"

    # Check that the created categories have auto_load=true
    for name, cat_config in builtin_categories.items():
        assert cat_config.get("auto_load", False) is True, f"Category {name} should have auto_load=true"


async def test_create_builtin_categories():
    """Test the _create_builtin_categories helper function."""
    session = SessionManager()

    await _create_builtin_categories(session, "test-helper-project")

    config = await session.session_state.get_project_config("test-helper-project")
    categories = config.get("categories", {})

    # Verify all categories created with correct defaults
    expected_categories = {"guide", "lang", "context"}
    assert set(categories.keys()) == expected_categories

    for name, cat_config in categories.items():
        assert cat_config["auto_load"] is True
        assert "dir" in cat_config
        assert "patterns" in cat_config
        assert "description" in cat_config
