"""Tests for category management tools."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
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
        session_instance.get_current_project_safe = AsyncMock(return_value="test-project")
        session_instance.session_state.get_project_config.return_value = {
            "categories": {
                "guide": {"dir": "guide/", "patterns": ["guidelines.md"]},
                "lang": {"dir": "lang/", "patterns": ["python.md"]},
                "context": {"dir": "context/", "patterns": ["context.md"]},
            }
        }
        session_instance.save_to_file = AsyncMock()
        yield session_instance


async def test_builtin_categories_constant():
    """Test that builtin categories are defined correctly."""
    assert BUILTIN_CATEGORIES == {"guide", "lang", "context"}


async def test_add_category_success(mock_session):
    """Test successful category addition."""
    result = await add_category("testing", "test/", ["*.md", "test-*.txt"])

    assert result["success"] is True
    assert result["category"]["name"] == "testing"
    assert result["category"]["dir"] == "test/"
    assert result["category"]["patterns"] == ["*.md", "test-*.txt"]


async def test_add_category_builtin_rejected(mock_session):
    """Test that adding builtin categories is rejected."""
    result = await add_category("guide", "test/", ["*.md"])

    assert result["success"] is False
    assert "Cannot override built-in category" in result["error"]


async def test_remove_category_builtin_rejected(mock_session):
    """Test that removing builtin categories is rejected."""
    result = await remove_category("guide")

    assert result["success"] is False
    assert "Cannot remove built-in category" in result["error"]


async def test_list_categories_basic(mock_session):
    """Test basic category listing."""
    result = await list_categories()

    assert result["project"] == "test-project"
    assert len(result["builtin_categories"]) == 3
    assert result["total_categories"] == 3


async def test_update_category_nonexistent(mock_session):
    """Test updating non-existent category."""
    result = await update_category("nonexistent", "test/", ["*.md"])

    assert result["success"] is False
    assert "does not exist" in result["error"]


@patch("src.mcp_server_guide.tools.category_tools.Path")
@patch("src.mcp_server_guide.tools.category_tools.glob")
async def test_get_category_content_no_files(mock_glob, mock_path, mock_session):
    """Test getting category content when no files match."""
    mock_glob.glob.return_value = []
    mock_path.return_value.exists.return_value = True

    # Add categories to config
    config = mock_session.session_state.get_project_config.return_value
    config["categories"]["testing"] = {"dir": "test/", "patterns": ["*.md"]}

    result = await get_category_content("testing")

    assert result["success"] is True
    assert result["content"] == ""
    assert "No files found" in result["message"]


async def test_get_category_content_nonexistent_category(mock_session):
    """Test getting content from non-existent category."""
    result = await get_category_content("nonexistent")

    assert result["success"] is False
    assert "does not exist" in result["error"]
