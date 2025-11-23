"""Tests for project switching and built-in category creation."""

from mcp_server_guide.session_manager import SessionManager
from mcp_server_guide.tools.project_tools import switch_project


async def test_switch_to_new_project_creates_builtin_categories(isolated_config_file):
    """Test that switching to a new project creates built-in categories with auto_load=true."""
    session_manager = SessionManager()
    session_manager._set_config_filename(isolated_config_file)

    # Switch to a new project
    result = await switch_project("test-project-123")

    assert result["success"] is True
    assert result["project"] == "test-project-123"

    # Verify the switch worked by checking session state directly
    session = SessionManager()
    assert session.session_state.project_name == "test-project-123"

    # Check that built-in categories were created in session state
    config = session.session_state.get_project_config()
    categories = config.categories

    # Should have the 4 built-in categories
    assert len(categories) == 4, f"Should have 4 default categories, got {len(categories)}"
    assert "guide" in categories
    assert "lang" in categories
    assert "context" in categories
    assert "prompt" in categories

    # Check that default categories are created for new projects
    default_categories = ["guide", "lang", "context", "prompt"]  # These are just defaults
    for name in default_categories:
        assert name in categories


async def test_builtin_categories_structure(isolated_config_file):
    """Test that builtin_categories returns correct structure."""
    session_manager = SessionManager()
    session_manager._set_config_filename(isolated_config_file)

    # Get builtin categories from SessionManager
    builtin_cats = SessionManager.default_categories()

    # Verify default categories created with correct defaults
    default_categories = {"guide", "lang", "context", "prompt"}
    assert set(builtin_cats.keys()) == default_categories

    for name, cat_config in builtin_cats.items():
        # cat_config is a Category object
        assert hasattr(cat_config, "dir")
        assert hasattr(cat_config, "patterns")
        assert hasattr(cat_config, "description")
        assert cat_config.dir.endswith("/")  # All dirs should end with /
