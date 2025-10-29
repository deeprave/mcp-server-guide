"""Tests for resource registry module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from mcp_server_guide.resource_registry import register_resources, _register_category_resources, _register_help_resource
from mcp_server_guide.project_config import Category, Collection


@pytest.fixture
def mock_server():
    """Create a mock FastMCP server."""
    server = MagicMock()

    # Store registered resource functions
    server._resources = {}

    def mock_resource_decorator(uri, name=None, description=None, mime_type=None):
        def decorator(func):
            server._resources[uri] = {
                'func': func,
                'name': name,
                'description': description,
                'mime_type': mime_type
            }
            return func
        return decorator

    server.resource = mock_resource_decorator
    return server


@pytest.fixture
def mock_config():
    """Create a mock project config."""
    config = MagicMock()
    config.categories = {
        "test_cat": Category(
            name="test_cat",
            dir="/test",
            patterns=["*.py"],
            description="Test category"
        )
    }
    config.collections = {
        "test_coll": Collection(
            name="test_coll",
            categories=["test_cat"],
            description="Test collection"
        )
    }
    return config


@pytest.mark.asyncio
async def test_register_resources(mock_server, mock_config):
    """Test that all resources are registered."""
    with patch('mcp_server_guide.resource_registry._register_category_resources', new_callable=AsyncMock) as mock_cat, \
         patch('mcp_server_guide.resource_registry._register_help_resource', new_callable=AsyncMock) as mock_help:

        await register_resources(mock_server, mock_config)

        mock_cat.assert_called_once_with(mock_server, mock_config)
        mock_help.assert_called_once_with(mock_server)


@pytest.mark.asyncio
async def test_register_category_resources(mock_server, mock_config):
    """Test category and collection resource registration."""
    with patch('mcp_server_guide.resource_registry.get_category_content', new_callable=AsyncMock) as mock_get_cat, \
         patch('mcp_server_guide.resource_registry.get_collection_content', new_callable=AsyncMock) as mock_get_coll:

        mock_get_cat.return_value = {"success": True, "content": "category content"}
        mock_get_coll.return_value = {"success": True, "content": "collection content"}

        await _register_category_resources(mock_server, mock_config)

        # Verify resources were registered
        assert len(mock_server._resources) == 2
        assert "guide://category/test_cat" in mock_server._resources
        assert "guide://collection/test_coll" in mock_server._resources


@pytest.mark.asyncio
async def test_register_help_resource(mock_server):
    """Test help resource registration."""
    with patch('mcp_server_guide.resource_registry.format_guide_help', new_callable=AsyncMock) as mock_help:
        mock_help.return_value = "help content"

        await _register_help_resource(mock_server)

        assert len(mock_server._resources) == 1
        assert "guide://help" in mock_server._resources


@pytest.mark.asyncio
async def test_category_resource_reader_success(mock_server, mock_config):
    """Test category resource reader with successful content retrieval."""
    with patch('mcp_server_guide.resource_registry.get_category_content', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"success": True, "content": "test content"}

        await _register_category_resources(mock_server, mock_config)

        category_reader = mock_server._resources["guide://category/test_cat"]["func"]
        result = await category_reader()
        assert result == "test content"


@pytest.mark.asyncio
async def test_category_resource_reader_failure(mock_server, mock_config):
    """Test category resource reader with failed content retrieval."""
    with patch('mcp_server_guide.resource_registry.get_category_content', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"success": False, "error": "Not found"}

        await _register_category_resources(mock_server, mock_config)

        category_reader = mock_server._resources["guide://category/test_cat"]["func"]
        with pytest.raises(ValueError, match="Failed to load category 'test_cat': Not found"):
            await category_reader()


@pytest.mark.asyncio
async def test_collection_resource_reader_success(mock_server, mock_config):
    """Test collection resource reader with successful content retrieval."""
    with patch('mcp_server_guide.resource_registry.get_collection_content', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {"success": True, "content": "collection content"}

        await _register_category_resources(mock_server, mock_config)

        collection_reader = mock_server._resources["guide://collection/test_coll"]["func"]
        result = await collection_reader()
        assert result == "collection content"


@pytest.mark.asyncio
async def test_help_resource_reader(mock_server):
    """Test help resource reader."""
    with patch('mcp_server_guide.resource_registry.format_guide_help', new_callable=AsyncMock) as mock_help:
        mock_help.return_value = "comprehensive help"

        await _register_help_resource(mock_server)

        help_reader = mock_server._resources["guide://help"]["func"]
        result = await help_reader()
        assert result == "comprehensive help"
        mock_help.assert_called_once()
