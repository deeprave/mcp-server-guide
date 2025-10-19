"""Tests for auto_load field validation in categories."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from mcp_server_guide.tools.category_tools import add_category, update_category


@pytest.fixture
def mock_session():
    """Mock session manager."""
    with patch("mcp_server_guide.tools.category_tools.SessionManager") as mock:
        from mcp_server_guide.project_config import ProjectConfig

        session_instance = Mock()
        mock.return_value = session_instance
        session_instance.get_project_name = Mock(return_value="test-project")
        session_instance.get_current_project_safe = AsyncMock(return_value="test-project")

        # Create ProjectConfig with empty categories
        config_data = ProjectConfig(categories={})

        session_instance.session_state.get_project_config = Mock(return_value=config_data)
        session_instance.get_or_create_project_config = AsyncMock(return_value=config_data)
        session_instance.session_state.set_project_config = Mock()
        session_instance.save_session = AsyncMock()
        yield session_instance


async def test_add_category_accepts_optional_auto_load(mock_session):
    """Test that add_category accepts optional auto_load parameter."""
    # This should pass when auto_load is provided
    result = await add_category("test_cat", "test_dir/", ["*.md"], auto_load=True)
    assert result["success"] is True

    # This should pass when auto_load is not provided (defaults to False)
    result = await add_category("test_cat2", "test_dir/", ["*.md"])
    assert result["success"] is True


async def test_add_category_treats_missing_auto_load_as_false(mock_session):
    """Test that missing auto_load field is treated as False."""
    result = await add_category("test_cat", "test_dir/", ["*.md"])
    assert result["success"] is True

    # Check that set_project_config was called with the right data
    call_args = mock_session.session_state.set_project_config.call_args
    categories = call_args[0][1]  # Second argument is the categories dict

    category = categories["test_cat"]
    # auto_load=False should be stored explicitly (category is a Category object)
    assert category.auto_load is False


async def test_add_category_stores_auto_load_when_true(mock_session):
    """Test that auto_load=True is stored in category config."""
    result = await add_category("test_cat", "test_dir/", ["*.md"], auto_load=True)
    assert result["success"] is True

    # Check that set_project_config was called with the right data
    call_args = mock_session.session_state.set_project_config.call_args
    categories = call_args[0][1]  # Second argument is the categories dict

    category = categories["test_cat"]
    assert category.auto_load is True


async def test_update_category_handles_auto_load_field(mock_session):
    """Test that update_category can handle auto_load field."""
    from mcp_server_guide.project_config import ProjectConfig, Category

    # Set up existing category
    config_data = ProjectConfig(
        categories={"test_cat": Category(dir="test_dir/", patterns=["*.md"], description="", auto_load=False)}
    )
    mock_session.session_state.get_project_config = Mock(return_value=config_data)
    mock_session.get_or_create_project_config = AsyncMock(return_value=config_data)

    # Update with auto_load
    result = await update_category("test_cat", "test_dir/", ["*.md"], auto_load=True)
    assert result["success"] is True

    # Check that set_project_config was called with the right data
    call_args = mock_session.session_state.set_project_config.call_args
    categories = call_args[0][1]  # Second argument is the categories dict

    category = categories["test_cat"]
    assert category.auto_load is True


async def test_update_category_preserves_auto_load_when_not_specified(mock_session):
    """Test that update_category preserves existing auto_load setting when not specified."""
    from mcp_server_guide.project_config import ProjectConfig, Category

    # Set up existing category with auto_load=True
    config_data = ProjectConfig(
        categories={"test_cat": Category(dir="test_dir/", patterns=["*.md"], description="", auto_load=True)}
    )
    mock_session.session_state.get_project_config = Mock(return_value=config_data)
    mock_session.get_or_create_project_config = AsyncMock(return_value=config_data)

    # Update without specifying auto_load
    result = await update_category("test_cat", "test_dir2/", ["*.txt"])
    assert result["success"] is True

    # Check that set_project_config was called with the right data
    call_args = mock_session.session_state.set_project_config.call_args
    categories = call_args[0][1]  # Second argument is the categories dict

    category = categories["test_cat"]
    assert category.auto_load is True
    assert category.dir == "test_dir2/"
