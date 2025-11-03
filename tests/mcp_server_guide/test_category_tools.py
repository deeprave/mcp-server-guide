"""Tests for category management tools."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from mcp_server_guide.tools.category_tools import (
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
    with patch("mcp_server_guide.tools.category_tools.SessionManager") as mock:
        from mcp_server_guide.path_resolver import LazyPath
        from mcp_server_guide.project_config import ProjectConfig
        from mcp_server_guide.models.category import Category

        session_instance = Mock()
        mock.return_value = session_instance
        session_instance.get_project_name = Mock(return_value="test-project")

        # Create ProjectConfig with Category objects
        test_config = ProjectConfig(
            categories={
                "guide": Category(dir="guide/", patterns=["guidelines.md"], description=""),
                "lang": Category(dir="lang/", patterns=["python.md"], description=""),
                "context": Category(dir="context/", patterns=["context.md"], description=""),
            }
        )

        session_instance.session_state.get_project_config = Mock(return_value=test_config)
        session_instance.session_state.set_project_config = Mock()
        session_instance.get_or_create_project_config = AsyncMock(return_value=test_config)

        # Mock config_manager().docroot to return a LazyPath that resolves to current directory
        mock_config_manager = Mock()
        mock_config_manager.docroot = LazyPath(".")
        session_instance.config_manager = Mock(return_value=mock_config_manager)
        session_instance.save_session = AsyncMock()
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

    assert result["success"] is True
    assert "categories" in result
    assert len(result["categories"]) >= 3  # At least the built-in categories


async def test_update_category_nonexistent(mock_session):
    """Test updating non-existent category."""
    result = await update_category("nonexistent", description="test description")

    assert result["success"] is False
    assert "does not exist" in result["error"]


@pytest.mark.asyncio
async def test_update_builtin_category_error(mock_session):
    """Test updating built-in category returns error."""
    result = await update_category("guide", description="test description")

    assert result["success"] is False
    assert "Cannot modify built-in category" in result["error"]


@pytest.mark.asyncio
async def test_remove_builtin_category_error(mock_session):
    """Test removing built-in category returns error."""
    result = await remove_category("guide")

    assert result["success"] is False
    assert "Cannot remove built-in category" in result["error"]


async def test_get_category_content_no_files(mock_session):
    """Test getting category content when no files match."""
    # Create test directory in the temp dir (autouse fixture handles pwd)
    from pathlib import Path

    test_dir = Path.cwd() / "test"
    test_dir.mkdir(exist_ok=True)

    # Add categories to config
    from mcp_server_guide.project_config import ProjectConfig
    from mcp_server_guide.models.category import Category

    test_config = ProjectConfig(categories={"testing": Category(dir="test/", patterns=["*.md"], description="")})
    mock_session.get_or_create_project_config = AsyncMock(return_value=test_config)

    result = await get_category_content("testing")

    assert result["success"] is True
    assert result["content"] == ""
    assert "No files found" in result["message"]


async def test_get_category_content_nonexistent_category(mock_session):
    """Test getting content from non-existent category."""
    result = await get_category_content("nonexistent")

    assert result["success"] is False
    assert "does not exist" in result["error"]
