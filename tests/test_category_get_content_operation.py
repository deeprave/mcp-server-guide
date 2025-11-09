"""Test category get_content operation for CRUD API consistency."""

import pytest
from unittest.mock import patch
from mcp_server_guide.operations.category_ops import CategoryGetContentOperation
from mcp_server_guide.models.category_model import CategoryModel
from mcp_server_guide.models.project_config import ProjectConfig


class TestCategoryGetContentOperation:
    """Test the CategoryGetContentOperation class."""

    @pytest.mark.asyncio
    async def test_category_get_content_operation_execution(self):
        """Test CategoryGetContentOperation executes correctly."""
        with patch("mcp_server_guide.operations.category_ops.get_category_content") as mock_get:
            mock_get.return_value = {"success": True, "content": "Test content"}

            operation = CategoryGetContentOperation(name="test_category")
            config = ProjectConfig()

            result = await operation.execute(config)

            assert result == {"success": True, "content": "Test content"}
            mock_get.assert_called_once_with(name="test_category", file=None)

    @pytest.mark.asyncio
    async def test_category_get_content_operation_with_file(self):
        """Test CategoryGetContentOperation with file parameter."""
        with patch("mcp_server_guide.operations.category_ops.get_category_content") as mock_get:
            mock_get.return_value = {"success": True, "content": "File content"}

            operation = CategoryGetContentOperation(name="test_category", file="test.md")
            config = ProjectConfig()

            result = await operation.execute(config)

            assert result == {"success": True, "content": "File content"}
            mock_get.assert_called_once_with(name="test_category", file="test.md")

    def test_category_model_has_get_content_operation(self):
        """Test that CategoryModel includes get_content operation."""
        operations = CategoryModel.get_operations()

        assert "get_content" in operations
        assert operations["get_content"] == CategoryGetContentOperation

    @pytest.mark.asyncio
    async def test_category_get_content_api_consistency(self):
        """Test that category get_content matches collection get_content format."""
        # Test that both category and collection models have get_content operation
        from mcp_server_guide.models.collection_model import CollectionModel

        category_ops = CategoryModel.get_operations()
        collection_ops = CollectionModel.get_operations()

        assert "get_content" in category_ops
        assert "get_content" in collection_ops

        # Both should have the same operation name
        assert "get_content" in category_ops
        assert "get_content" in collection_ops
