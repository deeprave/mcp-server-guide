"""Tests for category management tools."""

import pytest
from unittest.mock import Mock, patch
from src.mcp_server_guide.tools.category_tools import (
    add_category,
    remove_category,
    update_category,
    list_categories,
    get_category_content,
    BUILTIN_CATEGORIES,
)


@pytest.fixture
def mock_session():
    """Mock session manager."""
    with patch("src.mcp_server_guide.tools.category_tools.SessionManager") as mock:
        session_instance = Mock()
        mock.return_value = session_instance
        session_instance.get_current_project.return_value = "test-project"
        session_instance.session_state.get_project_config.return_value = {
            "categories": {
                "guide": {"dir": "guide/", "patterns": ["guidelines.md"]},
                "lang": {"dir": "lang/", "patterns": ["python.md"]},
                "context": {"dir": "context/", "patterns": ["context.md"]},
            }
        }
        yield session_instance


def test_builtin_categories_constant():
    """Test that builtin categories are defined correctly."""
    assert BUILTIN_CATEGORIES == {"guide", "lang", "context"}


def test_add_category_success(mock_session):
    """Test successful category addition."""
    result = add_category("testing", "test/", ["*.md", "test-*.txt"])

    assert result["success"] is True
    assert result["category"]["name"] == "testing"
    assert result["category"]["dir"] == "test/"
    assert result["category"]["patterns"] == ["*.md", "test-*.txt"]


def test_add_category_builtin_rejected(mock_session):
    """Test that adding builtin categories is rejected."""
    result = add_category("guide", "test/", ["*.md"])

    assert result["success"] is False
    assert "Cannot add built-in category" in result["error"]


def test_remove_category_builtin_rejected(mock_session):
    """Test that removing builtin categories is rejected."""
    result = remove_category("guide")

    assert result["success"] is False
    assert "Cannot remove built-in category" in result["error"]


def test_list_categories_basic(mock_session):
    """Test basic category listing."""
    result = list_categories()

    assert result["project"] == "test-project"
    assert len(result["builtin_categories"]) == 3
    assert result["total_categories"] == 3


def test_update_category_nonexistent(mock_session):
    """Test updating non-existent category."""
    result = update_category("nonexistent", "test/", ["*.md"])

    assert result["success"] is False
    assert "does not exist" in result["error"]


@patch("src.mcp_server_guide.tools.category_tools.Path")
@patch("src.mcp_server_guide.tools.category_tools.glob")
def test_get_category_content_no_files(mock_glob, mock_path, mock_session):
    """Test getting category content when no files match."""
    mock_glob.glob.return_value = []
    mock_path.return_value.exists.return_value = True

    # Add categories to config
    config = mock_session.session_state.get_project_config.return_value
    config["categories"]["testing"] = {"dir": "test/", "patterns": ["*.md"]}

    result = get_category_content("testing")

    assert result["success"] is True
    assert result["content"] == ""
    assert "No files found" in result["message"]


def test_get_category_content_nonexistent_category(mock_session):
    """Test getting content from non-existent category."""
    result = get_category_content("nonexistent")

    assert result["success"] is False
    assert "does not exist" in result["error"]
