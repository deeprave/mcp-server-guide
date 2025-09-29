"""Tests for auto_load field validation in categories."""

import pytest
from unittest.mock import Mock, patch
from mcp_server_guide.tools.category_tools import add_category, update_category


@pytest.fixture
def mock_session():
    """Mock session manager."""
    with patch("mcp_server_guide.tools.category_tools.SessionManager") as mock:
        session_instance = Mock()
        mock.return_value = session_instance
        session_instance.get_current_project.return_value = "test-project"
        session_instance.session_state.get_project_config.return_value = {"categories": {}}
        yield session_instance


def test_add_category_accepts_optional_auto_load(mock_session):
    """Test that add_category accepts optional auto_load parameter."""
    # This should pass when auto_load is provided
    result = add_category("test_cat", "test_dir/", ["*.md"], auto_load=True)
    assert result["success"] is True

    # This should pass when auto_load is not provided (defaults to False)
    result = add_category("test_cat2", "test_dir/", ["*.md"])
    assert result["success"] is True


def test_add_category_treats_missing_auto_load_as_false(mock_session):
    """Test that missing auto_load field is treated as False."""
    result = add_category("test_cat", "test_dir/", ["*.md"])
    assert result["success"] is True

    # Check that set_project_config was called with the right data
    call_args = mock_session.session_state.set_project_config.call_args
    categories = call_args[0][2]  # Third argument is the categories dict

    category = categories["test_cat"]
    # Missing auto_load should not be stored (treated as False)
    assert "auto_load" not in category


def test_add_category_stores_auto_load_when_true(mock_session):
    """Test that auto_load=True is stored in category config."""
    result = add_category("test_cat", "test_dir/", ["*.md"], auto_load=True)
    assert result["success"] is True

    # Check that set_project_config was called with the right data
    call_args = mock_session.session_state.set_project_config.call_args
    categories = call_args[0][2]  # Third argument is the categories dict

    category = categories["test_cat"]
    assert category.get("auto_load", False) is True


def test_update_category_handles_auto_load_field(mock_session):
    """Test that update_category can handle auto_load field."""
    # Set up existing category
    mock_session.session_state.get_project_config.return_value = {
        "categories": {"test_cat": {"dir": "test_dir/", "patterns": ["*.md"], "description": ""}}
    }

    # Update with auto_load
    result = update_category("test_cat", "test_dir/", ["*.md"], auto_load=True)
    assert result["success"] is True

    # Check that set_project_config was called with the right data
    call_args = mock_session.session_state.set_project_config.call_args
    categories = call_args[0][2]  # Third argument is the categories dict

    category = categories["test_cat"]
    assert category.get("auto_load", False) is True


def test_update_category_preserves_auto_load_when_not_specified(mock_session):
    """Test that update_category preserves existing auto_load setting when not specified."""
    # Set up existing category with auto_load=True
    mock_session.session_state.get_project_config.return_value = {
        "categories": {"test_cat": {"dir": "test_dir/", "patterns": ["*.md"], "description": "", "auto_load": True}}
    }

    # Update without specifying auto_load
    result = update_category("test_cat", "test_dir2/", ["*.txt"])
    assert result["success"] is True

    # Check that set_project_config was called with the right data
    call_args = mock_session.session_state.set_project_config.call_args
    categories = call_args[0][2]  # Third argument is the categories dict

    category = categories["test_cat"]
    assert category.get("auto_load", False) is True
    assert category["dir"] == "test_dir2/"
