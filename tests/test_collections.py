"""Tests for collections functionality."""

from unittest.mock import Mock, patch

import pytest

from mcp_server_guide.models.category import Category
from mcp_server_guide.models.collection import Collection
from mcp_server_guide.project_config import ProjectConfig
from mcp_server_guide.tools.collection_tools import (
    add_collection,
    add_to_collection,
    get_collection_content,
    list_collections,
    remove_collection,
    remove_from_collection,
    update_collection,
)


@pytest.fixture
def mock_session():
    """Mock session manager."""
    with patch("mcp_server_guide.session_manager.SessionManager") as mock:
        session_instance = Mock()  # Use regular Mock instead of AsyncMock
        mock.return_value = session_instance

        # Mock config with categories
        config = ProjectConfig(
            categories={
                "guide": Category(dir="guide/", patterns=["*.md"], description="Guide docs"),
                "lang": Category(dir="lang/", patterns=["*.md"], description="Language docs"),
                "context": Category(dir="context/", patterns=["*.md"], description="Context docs"),
            },
            collections={},
        )

        async def mock_get_config(project=None):
            return config

        async def mock_save_session():
            pass

        session_instance.get_or_create_project_config = mock_get_config
        session_instance.safe_save_session = mock_save_session
        session_instance.get_project_name.return_value = "test-project"

        yield session_instance, config


@pytest.mark.asyncio
async def test_add_collection_success(mock_session):
    """Test successful collection creation."""
    session_instance, config = mock_session

    result = await add_collection("docs", ["guide", "lang"], "Documentation collection")

    assert result["success"] is True
    assert result["message"] == "Collection 'docs' created successfully"
    assert "docs" in config.collections
    assert config.collections["docs"].categories == ["guide", "lang"]
    assert config.collections["docs"].description == "Documentation collection"


@pytest.mark.asyncio
async def test_add_collection_invalid_name(mock_session):
    """Test collection creation with invalid name."""
    session_instance, config = mock_session

    # Test empty name
    result = await add_collection("", ["guide"], "Test collection")
    assert result["success"] is False
    assert "invalid" in result["error"].lower() or "name" in result["error"].lower()

    # Test name with invalid characters
    result = await add_collection("test@collection", ["guide"], "Test collection")
    assert result["success"] is False
    assert "invalid" in result["error"].lower() or "name" in result["error"].lower()

    # Test name with only whitespace
    result = await add_collection("   ", ["guide"], "Test collection")
    assert result["success"] is False
    assert "invalid" in result["error"].lower() or "name" in result["error"].lower()


@pytest.mark.asyncio
async def test_add_collection_duplicate_categories_in_list(mock_session):
    """Test collection creation with duplicate categories in the list."""
    session_instance, config = mock_session

    result = await add_collection("docs", ["guide", "guide", "lang"], "Documentation collection")
    assert result["success"] is False
    assert "duplicate" in result["error"].lower()


@pytest.mark.asyncio
async def test_add_collection_case_insensitive_duplicates(mock_session):
    """Test collection creation with case-insensitive duplicate categories."""
    session_instance, config = mock_session

    result = await add_collection("docs", ["Guide", "guide", "lang"], "Documentation collection")
    assert result["success"] is False
    assert "duplicate" in result["error"].lower()


@pytest.mark.asyncio
async def test_add_collection_whitespace_duplicate_categories(mock_session):
    """Test collection creation with duplicate categories that have leading/trailing whitespace.

    This test checks that category names are normalized (trimmed) before checking for duplicates.
    """
    session_instance, config = mock_session

    # "Guide" and " guide " should be considered duplicates after trimming whitespace
    result = await add_collection("docs", ["Guide", " guide ", "lang"], "Documentation collection")
    assert result["success"] is False
    assert "duplicate" in result["error"].lower()


@pytest.mark.asyncio
async def test_add_collection_edge_case_names(mock_session):
    """Test collection creation with edge case names."""
    session_instance, config = mock_session

    # Test maximum length name (30 characters)
    long_name = "a" * 30
    result = await add_collection(long_name, ["guide"], "Test collection")
    assert result["success"] is True

    # Test name with all valid special characters
    special_name = "test_collection-123"
    result = await add_collection(special_name, ["guide"], "Test collection")
    assert result["success"] is True

    # Test minimum length name (single character)
    min_length_name = "x"
    result = await add_collection(min_length_name, ["guide"], "Test collection")
    assert result["success"] is True

    # Test name starting with letter followed by numbers
    numeric_name = "a123456"
    result = await add_collection(numeric_name, ["guide"], "Test collection")
    assert result["success"] is True

    # Test name with underscores and dashes
    mixed_name = "test_collection-with_dashes"
    result = await add_collection(mixed_name, ["guide"], "Test collection")
    assert result["success"] is True


@pytest.mark.asyncio
async def test_add_collection_duplicate(mock_session):
    """Test adding duplicate collection."""
    session_instance, config = mock_session
    config.collections["existing"] = Collection(categories=["guide"], description="Existing")

    result = await add_collection("existing", ["lang"], "New description")

    assert result["success"] is False
    assert "already exists" in result["error"]


@pytest.mark.asyncio
async def test_add_collection_invalid_category(mock_session):
    """Test adding collection with non-existent category."""
    session_instance, config = mock_session

    result = await add_collection("docs", ["nonexistent"], "Test collection")

    assert result["success"] is False
    assert "does not exist" in result["error"]


@pytest.mark.asyncio
async def test_add_collection_empty_category_list(mock_session):
    """Test adding collection with an empty category list."""
    session_instance, config = mock_session

    result = await add_collection("emptycat", [], "Collection with no categories")

    assert result["success"] is False
    assert "category list" in result["error"] or "at least one category" in result["error"]


@pytest.mark.asyncio
async def test_add_collection_none_category_list(mock_session):
    """Test adding collection with None as category list."""
    session_instance, config = mock_session

    result = await add_collection("nonecat", None, "Collection with None categories")

    assert result["success"] is False
    assert "category list" in result["error"] or "at least one category" in result["error"]


@pytest.mark.asyncio
async def test_update_collection_success(mock_session):
    """Test successful collection update."""
    session_instance, config = mock_session
    config.collections["docs"] = Collection(categories=["guide"], description="Old description")

    result = await update_collection("docs", description="New description")

    assert result["success"] is True
    assert config.collections["docs"].description == "New description"


@pytest.mark.asyncio
async def test_add_to_collection_success(mock_session):
    """Test adding categories to collection."""
    session_instance, config = mock_session
    config.collections["docs"] = Collection(categories=["guide"], description="Test")

    result = await add_to_collection("docs", ["lang", "context"])

    assert result["success"] is True
    assert set(config.collections["docs"].categories) == {"guide", "lang", "context"}


@pytest.mark.asyncio
async def test_remove_from_collection_success(mock_session):
    """Test removing categories from collection."""
    session_instance, config = mock_session
    config.collections["docs"] = Collection(categories=["guide", "lang", "context"], description="Test")

    result = await remove_from_collection("docs", ["lang"])

    assert result["success"] is True
    assert config.collections["docs"].categories == ["guide", "context"]


@pytest.mark.asyncio
async def test_remove_from_collection_nonexistent_category(mock_session):
    """Test removing a category that does not exist in the collection."""
    session_instance, config = mock_session
    config.collections["docs"] = Collection(categories=["guide", "lang"], description="Test")

    result = await remove_from_collection("docs", ["not_in_collection"])

    assert result["success"] is False
    assert "error" in result
    assert config.collections["docs"].categories == ["guide", "lang"]


@pytest.mark.asyncio
async def test_remove_from_collection_empty_error(mock_session):
    """Test removing all categories from collection fails."""
    session_instance, config = mock_session
    config.collections["docs"] = Collection(categories=["guide"], description="Test")

    result = await remove_from_collection("docs", ["guide"])

    assert result["success"] is False
    assert "Cannot remove all categories" in result["error"]


@pytest.mark.asyncio
async def test_remove_collection_success(mock_session):
    """Test successful collection removal."""
    session_instance, config = mock_session
    config.collections["docs"] = Collection(categories=["guide"], description="Test")

    result = await remove_collection("docs")

    assert result["success"] is True
    assert "docs" not in config.collections


@pytest.mark.asyncio
async def test_list_collections_verbose(mock_session):
    """Test listing collections with verbose output."""
    session_instance, config = mock_session
    config.collections["docs"] = Collection(categories=["guide", "lang"], description="Test collection")

    result = await list_collections(verbose=True)

    assert result["success"] is True
    assert "docs" in result["collections"]
    assert "category_details" in result["collections"]["docs"]


@pytest.mark.asyncio
async def test_get_collection_content():
    """Test getting collection content."""
    with (
        patch("mcp_server_guide.session_manager.SessionManager") as mock_session,
        patch("mcp_server_guide.tools.collection_tools.get_category_content") as mock_get_cat,
    ):
        # Setup mocks
        session_instance = Mock()
        mock_session.return_value = session_instance

        config = ProjectConfig(
            categories={"guide": Category(dir="guide/", patterns=["*.md"])},
            collections={"docs": Collection(categories=["guide"], description="Test")},
        )

        async def mock_get_config(project=None):
            return config

        session_instance.get_or_create_project_config = mock_get_config

        mock_get_cat.return_value = {"success": True, "content": "Guide content here"}

        result = await get_collection_content("docs")

        assert result["success"] is True
        assert "Guide content here" in result["content"]
        assert result["collection_name"] == "docs"
