"""Tests for category descriptions functionality."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from mcp_server_guide.tools.category_tools import (
    add_category,
    update_category,
    list_categories,
)


@pytest.fixture
def mock_session():
    """Mock session manager."""
    with patch("mcp_server_guide.session_manager.SessionManager") as mock:
        from mcp_server_guide.project_config import ProjectConfig

        session_instance = Mock()
        mock.return_value = session_instance
        session_instance.get_project_name = Mock(return_value="test-project")
        session_instance.get_current_project_safe = Mock(return_value="test-project")

        # Create ProjectConfig with empty categories
        test_config = ProjectConfig(categories={})

        session_instance.session_state.get_project_config = Mock(return_value=test_config)
        session_instance.session_state.set_project_config = Mock()
        session_instance.get_or_create_project_config = AsyncMock(return_value=test_config)
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
    from mcp_server_guide.project_config import ProjectConfig
    from mcp_server_guide.models.category import Category

    # Setup existing category
    config_data = ProjectConfig(
        categories={"testing": Category(dir="test/", patterns=["*.md"], description="Old description")}
    )
    mock_session.session_state.get_project_config = Mock(return_value=config_data)
    mock_session.get_or_create_project_config = AsyncMock(return_value=config_data)

    result = await update_category("testing", description="New description")

    assert result["success"] is True
    assert result["category"]["description"] == "New description"


async def test_list_categories_includes_descriptions(mock_session):
    """Test that list_categories includes descriptions."""
    from mcp_server_guide.project_config import ProjectConfig
    from mcp_server_guide.models.category import Category

    # Setup categories with descriptions
    config_data = ProjectConfig(
        categories={
            "guide": Category(dir="guide/", patterns=["guidelines"], description="Development guidelines"),
            "testing": Category(dir="test/", patterns=["*.md"], description="Test documentation"),
        }
    )
    mock_session.get_or_create_project_config = AsyncMock(return_value=config_data)

    result = await list_categories()

    # Find the testing category
    testing_category = result["categories"].get("testing")
    assert testing_category is not None
    assert testing_category["description"] == "Test documentation"


async def test_list_categories_handles_missing_descriptions(mock_session):
    """Test that list_categories handles categories without descriptions."""
    from mcp_server_guide.project_config import ProjectConfig
    from mcp_server_guide.models.category import Category

    # Setup category without description (empty string is the default)
    config_data = ProjectConfig(categories={"testing": Category(dir="test/", patterns=["*.md"], description="")})
    mock_session.get_or_create_project_config = AsyncMock(return_value=config_data)

    result = await list_categories()

    testing_category = result["categories"]["testing"]
    assert testing_category.get("description", "") == ""
