"""Tests for project switching and built-in category creation."""

from src.mcp_server_guide.tools.project_tools import switch_project, _create_builtin_categories
from src.mcp_server_guide.session_tools import SessionManager


async def test_switch_to_new_project_creates_builtin_categories():
    """Test that switching to a new project creates built-in categories with auto_load=true."""
    # Switch to a new project
    result = await switch_project("test-project-123")

    assert result["success"] is True
    assert result["project"] == "test-project-123"

    # Check that built-in categories were created
    session = SessionManager()
    config = session.session_state.get_project_config("test-project-123")
    categories = config.get("categories", {})

    # Should have all 3 built-in categories
    assert "guide" in categories
    assert "lang" in categories
    assert "context" in categories

    # Each should have auto_load = True
    assert categories["guide"]["auto_load"] is True
    assert categories["lang"]["auto_load"] is True
    assert categories["context"]["auto_load"] is True

    # Check patterns are without .md extension
    assert categories["guide"]["patterns"] == ["guidelines"]
    assert categories["lang"]["patterns"] == ["none"]
    assert categories["context"]["patterns"] == ["project-context"]


async def test_create_builtin_categories():
    """Test the _create_builtin_categories helper function."""
    session = SessionManager()

    _create_builtin_categories(session, "test-helper-project")

    config = session.session_state.get_project_config("test-helper-project")
    categories = config.get("categories", {})

    # Verify all categories created with correct defaults
    expected_categories = {"guide", "lang", "context"}
    assert set(categories.keys()) == expected_categories

    for name, cat_config in categories.items():
        assert cat_config["auto_load"] is True
        assert "dir" in cat_config
        assert "patterns" in cat_config
        assert "description" in cat_config
