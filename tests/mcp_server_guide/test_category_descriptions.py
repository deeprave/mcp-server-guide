"""Tests for category descriptions functionality."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.mcp_server_guide.tools.category_tools import (
    add_category,
    update_category,
    list_categories,
)


@pytest.fixture
def mock_session():
    """Mock session manager."""
    with patch("src.mcp_server_guide.tools.category_tools.SessionManager") as mock:
        session_instance = Mock()
        mock.return_value = session_instance
        session_instance.get_current_project.return_value = "test-project"
        session_instance.session_state.get_project_config.return_value = {"categories": {}}
        session_instance.save_to_file = AsyncMock()
        session_instance.save_to_file = AsyncMock()
        yield session_instance


async def test_add_category_with_description(mock_session):
    """Test adding category with description."""
    result = await add_category("testing", "test/", ["*.md"], description="Test documentation")

    assert result["success"] is True
    assert result["category"]["description"] == "Test documentation"


async def test_add_category_without_description_defaults_empty(mock_session):
    """Test adding category without description defaults to empty string."""
    result = await add_category("testing", "test/", ["*.md"])

    assert result["success"] is True
    assert result["category"]["description"] == ""


async def test_update_category_with_description(mock_session):
    """Test updating category with description."""
    # Setup existing category
    config = mock_session.session_state.get_project_config.return_value
    config["categories"]["testing"] = {"dir": "test/", "patterns": ["*.md"], "description": "Old description"}

    result = await update_category("testing", "test/", ["*.md"], description="New description")

    assert result["success"] is True
    assert result["category"]["description"] == "New description"


async def test_list_categories_includes_descriptions(mock_session):
    """Test that list_categories includes descriptions."""
    # Setup categories with descriptions
    config = mock_session.session_state.get_project_config.return_value
    config["categories"] = {
        "guide": {"dir": "guide/", "patterns": ["guidelines"], "description": "Development guidelines"},
        "testing": {"dir": "test/", "patterns": ["*.md"], "description": "Test documentation"},
    }

    result = list_categories()

    # Find the testing category
    testing_category = result["custom_categories"].get("testing")
    assert testing_category is not None
    assert testing_category["description"] == "Test documentation"


async def test_list_categories_handles_missing_descriptions(mock_session):
    """Test that list_categories handles categories without descriptions."""
    # Setup category without description
    config = mock_session.session_state.get_project_config.return_value
    config["categories"] = {
        "testing": {
            "dir": "test/",
            "patterns": ["*.md"],
            # No description field
        }
    }

    result = list_categories()

    testing_category = result["custom_categories"]["testing"]
    assert testing_category.get("description", "") == ""
