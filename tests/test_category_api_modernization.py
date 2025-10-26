"""Tests for modernized category API."""

import pytest
from unittest.mock import AsyncMock, patch, Mock
from mcp_server_guide.tools.category_tools import (
    add_category,
    update_category,
    add_to_category,
    remove_from_category,
    remove_category,
    list_categories,
)
from mcp_server_guide.project_config import ProjectConfig, Category


@pytest.fixture
def mock_session():
    """Mock session manager."""
    with patch("mcp_server_guide.tools.category_tools.SessionManager") as mock:
        session_instance = Mock()  # Use regular Mock instead of AsyncMock
        mock.return_value = session_instance

        config = ProjectConfig(
            categories={
                "guide": Category(dir="guide/", patterns=["*.md"], description="Guide docs"),
                "custom": Category(dir="custom/", patterns=["*.txt"], description="Custom docs"),
            },
            collections={},
        )
        session_instance.get_or_create_project_config = AsyncMock(return_value=config)
        session_instance.save_session = AsyncMock(return_value=None)
        session_instance.get_project_name.return_value = "test-project"

        # Set up session_state as a regular Mock since set_project_config is sync
        session_state_mock = Mock()
        session_state_mock.set_project_config = Mock(return_value=None)
        session_instance.session_state = session_state_mock

        yield session_instance, config


@pytest.mark.asyncio
async def test_add_category_no_project_param(mock_session):
    """Test add_category works without project parameter."""
    session_instance, config = mock_session

    result = await add_category("test", "test/", ["*.md"], "Test category")

    assert result["success"] is True
    assert "test" in config.categories
    assert config.categories["test"].dir == "test/"
    assert config.categories["test"].patterns == ["*.md"]
    assert config.categories["test"].description == "Test category"


@pytest.mark.asyncio
async def test_add_category_missing_required_arguments(mock_session):
    """Test add_category with missing or invalid required arguments."""
    session_instance, config = mock_session

    # Missing name
    result = await add_category(None, "test/", ["*.md"], "Test category")
    assert result["success"] is False
    assert "error" in result
    assert "name" in result["error"].lower() or "missing" in result["error"].lower()

    # Missing dir
    result = await add_category("test", None, ["*.md"], "Test category")
    assert result["success"] is False
    assert "error" in result
    assert (
        "dir" in result["error"].lower()
        or "directory" in result["error"].lower()
        or "missing" in result["error"].lower()
    )

    # Empty name
    result = await add_category("", "test/", ["*.md"], "Test category")
    assert result["success"] is False
    assert "error" in result
    assert "name" in result["error"].lower() or "empty" in result["error"].lower()


@pytest.mark.asyncio
async def test_update_category_keyword_only(mock_session):
    """Test update_category uses keyword-only parameters."""
    session_instance, config = mock_session

    result = await update_category("custom", description="Updated description")

    assert result["success"] is True
    assert config.categories["custom"].description == "Updated description"
    # Other fields should remain unchanged
    assert config.categories["custom"].dir == "custom/"
    assert config.categories["custom"].patterns == ["*.txt"]


@pytest.mark.asyncio
async def test_add_to_category_success(mock_session):
    """Test adding patterns to existing category."""
    session_instance, config = mock_session

    result = await add_to_category("custom", ["*.md", "*.rst"])

    assert result["success"] is True
    # Should have original pattern plus new ones
    expected_patterns = ["*.txt", "*.md", "*.rst"]
    assert config.categories["custom"].patterns == expected_patterns


@pytest.mark.asyncio
async def test_remove_from_category_success(mock_session):
    """Test removing patterns from category."""
    session_instance, config = mock_session
    # Add multiple patterns first
    config.categories["custom"].patterns = ["*.txt", "*.md", "*.rst"]

    result = await remove_from_category("custom", ["*.md"])

    assert result["success"] is True
    assert config.categories["custom"].patterns == ["*.txt", "*.rst"]


@pytest.mark.asyncio
async def test_remove_from_category_pattern_not_found(mock_session):
    """Test removing non-existent pattern succeeds but reports not found patterns."""
    session_instance, config = mock_session

    result = await remove_from_category("custom", ["*.nonexistent"])

    assert result["success"] is True
    assert "not_found_patterns" in result
    assert "*.nonexistent" in result["not_found_patterns"]


@pytest.mark.asyncio
async def test_remove_from_category_mixed_found_and_not_found(mock_session):
    """Test removing a mix of existing and non-existing patterns reports each correctly."""
    session_instance, config = mock_session

    # Add patterns to the category
    config.categories["custom"].patterns = ["*.txt", "*.md", "*.rst"]

    # Attempt to remove one existing and one non-existing pattern
    result = await remove_from_category("custom", ["*.md", "*.nonexistent"])

    assert result["success"] is True
    assert "not_found_patterns" in result
    assert "*.nonexistent" in result["not_found_patterns"]
    assert "*.md" not in result["not_found_patterns"]
    # Ensure the existing pattern was removed
    assert "*.md" not in config.categories["custom"].patterns


@pytest.mark.asyncio
async def test_remove_from_category_empty_error(mock_session):
    """Test removing all patterns from file-based category fails."""
    session_instance, config = mock_session

    result = await remove_from_category("custom", ["*.txt"])

    assert result["success"] is False
    assert "Cannot remove all patterns" in result["error"]


@pytest.mark.asyncio
async def test_list_categories_verbose(mock_session):
    """Test list_categories with verbose mode."""
    session_instance, config = mock_session

    result = await list_categories(verbose=True)

    assert result["success"] is True
    assert "guide" in result["categories"]
    assert "custom" in result["categories"]

    # Verbose mode should include dir, patterns, url
    guide_info = result["categories"]["guide"]
    assert "dir" in guide_info
    assert "patterns" in guide_info
    assert "url" in guide_info
    assert guide_info["builtin"] is True


@pytest.mark.asyncio
async def test_list_categories_non_verbose(mock_session):
    """Test list_categories without verbose mode."""
    session_instance, config = mock_session

    result = await list_categories(verbose=False)

    assert result["success"] is True

    # Non-verbose mode should only include description and builtin flag
    guide_info = result["categories"]["guide"]
    assert "description" in guide_info
    assert "builtin" in guide_info
    assert "dir" not in guide_info
    assert "patterns" not in guide_info


@pytest.mark.asyncio
async def test_builtin_category_protection(mock_session):
    """Test that built-in categories cannot be modified or removed."""
    session_instance, config = mock_session

    # Try to update built-in category
    result = await update_category("guide", description="New description")

    assert result["success"] is False
    assert "Cannot modify built-in category" in result["error"]


@pytest.mark.asyncio
async def test_remove_builtin_category_protection(mock_session):
    """Test that built-in categories cannot be removed."""
    session_instance, config = mock_session

    # Try to remove built-in category
    result = await remove_category("guide")

    assert result["success"] is False
    assert "Cannot remove built-in category" in result["error"]


@pytest.mark.asyncio
async def test_add_to_builtin_category_protection(mock_session):
    """Test that patterns cannot be added to built-in categories."""
    session_instance, config = mock_session

    result = await add_to_category("guide", ["*.new"])

    assert result["success"] is False
    assert "Cannot modify built-in category" in result["error"]
