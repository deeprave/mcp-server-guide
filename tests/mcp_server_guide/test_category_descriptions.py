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
        session_instance.get_current_project_safe = AsyncMock(return_value="test-project")
        session_instance.session_state.get_project_config = Mock(return_value={"categories": {}})
        session_instance.session_state.set_project_config = Mock()
        session_instance.get_or_create_project_config = AsyncMock(return_value={"categories": {}})
        session_instance.save_session = AsyncMock()
        yield session_instance


async def test_add_category_with_description(mock_session):
    """Test adding category with description."""
    result = await add_category("testing", "test/", ["*.md"], description="Test documentation")

    assert result["success"] is True
    assert result["category"]["description"] == "Test documentation"


async def test_add_category_without_description_defaults_empty(mock_session):
    """Test adding category without description gets a default description."""
    result = await add_category("testing", "test/", ["*.md"])

    assert result["success"] is True
    assert result["category"]["description"] == "Custom category: testing"


async def test_update_category_with_description(mock_session):
    """Test updating category with description."""
    # Setup existing category
    config_data = {"categories": {"testing": {"dir": "test/", "patterns": ["*.md"], "description": "Old description"}}}
    mock_session.session_state.get_project_config = Mock(return_value=config_data)
    mock_session.get_or_create_project_config = AsyncMock(return_value=config_data)

    result = await update_category("testing", "test/", ["*.md"], description="New description")

    assert result["success"] is True
    assert result["category"]["description"] == "New description"


async def test_list_categories_includes_descriptions(mock_session):
    """Test that list_categories includes descriptions."""
    # Setup categories with descriptions
    config_data = {
        "categories": {
            "guide": {"dir": "guide/", "patterns": ["guidelines"], "description": "Development guidelines"},
            "testing": {"dir": "test/", "patterns": ["*.md"], "description": "Test documentation"},
        }
    }
    mock_session.get_or_create_project_config = AsyncMock(return_value=config_data)

    result = await list_categories()

    # Find the testing category
    testing_category = result["custom_categories"].get("testing")
    assert testing_category is not None
    assert testing_category["description"] == "Test documentation"


async def test_list_categories_handles_missing_descriptions(mock_session):
    """Test that list_categories handles categories without descriptions."""
    # Setup category without description
    config_data = {
        "categories": {
            "testing": {
                "dir": "test/",
                "patterns": ["*.md"],
                # No description field
            }
        }
    }
    mock_session.get_or_create_project_config = AsyncMock(return_value=config_data)

    result = await list_categories()

    testing_category = result["custom_categories"]["testing"]
    assert testing_category.get("description", "") == ""
