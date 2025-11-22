"""Tests for JSON instruction tools."""

import pytest
from unittest.mock import patch, Mock, AsyncMock

from src.mcp_server_guide.tools.category_tools_json import guide_categories
from src.mcp_server_guide.tools.collection_tools_json import guide_collections
from src.mcp_server_guide.tools.document_tools_json import guide_documents
from src.mcp_server_guide.tools.content_tools_json import guide_content
from src.mcp_server_guide.tools.config_tools_json import guide_config


class TestJSONInstructionTools:
    """Test JSON instruction tools functionality."""

    @pytest.mark.asyncio
    async def test_guide_categories_add_action(self):
        """Test guide_categories with add action."""
        data = {
            "action": "add",
            "name": "test_category",
            "dir": "/test/path",
            "patterns": ["*.py", "*.md"],
            "description": "Test category",
        }

        with patch("src.mcp_server_guide.tools.category_tools.add_category") as mock_add:
            mock_add.return_value = {"success": True, "message": "Category added"}

            result = await guide_categories(data)

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_guide_categories_unknown_action(self):
        """Test guide_categories with unknown action."""
        data = {"action": "unknown_action"}

        with patch("src.mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session.get_or_create_project_config = AsyncMock(return_value=Mock())
            mock_session_class.return_value = mock_session

            with patch("src.mcp_server_guide.operations.model_base.discover_models") as mock_discover:
                mock_model = Mock()
                mock_model.__name__ = "CategoryModel"
                mock_model.get_operation_class = Mock(
                    side_effect=ValueError("Unknown action 'unknown_action' for CategoryModel")
                )
                mock_discover.return_value = [mock_model]

                result = await guide_categories(data)

                assert result["success"] is False
                assert "Unknown action 'unknown_action' for CategoryModel" in result["error"]

    @pytest.mark.asyncio
    async def test_guide_collections_add_action(self):
        """Test guide_collections with add action."""
        data = {
            "action": "add",
            "name": "test_collection",
            "categories": ["category1", "category2"],
            "description": "Test collection",
        }

        with patch("src.mcp_server_guide.operations.collection_ops.add_collection") as mock_add:
            mock_add.return_value = {"success": True, "message": "Collection added"}

            result = await guide_collections(data)

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_guide_documents_create_action(self):
        """Test guide_documents with create action."""
        data = {
            "action": "create",
            "name": "test_doc",
            "category_dir": "test_category",
            "content": "Test content",
        }

        with patch("src.mcp_server_guide.operations.document_ops.create_mcp_document") as mock_create:
            mock_create.return_value = {"success": True, "message": "Document created"}

            result = await guide_documents(data)

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_guide_content_get_action(self):
        """Test guide_content with get action."""
        data = {"action": "get", "category_or_collection": "test_category", "document": "test_doc"}

        with patch("src.mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session.get_or_create_project_config = AsyncMock(return_value=Mock())
            mock_session_class.return_value = mock_session

            with patch("src.mcp_server_guide.operations.model_base.discover_models") as mock_discover:
                mock_model = Mock()
                mock_model.__name__ = "ContentModel"
                mock_model.get_operation_class = Mock()

                mock_operation = Mock()
                mock_operation.execute = AsyncMock(return_value={"success": True, "content": "Test content"})
                mock_op_class = Mock()
                mock_op_class.model_validate.return_value = mock_operation
                mock_model.get_operation_class.return_value = mock_op_class

                mock_discover.return_value = [mock_model]

                result = await guide_content(data)

                assert result["success"] is True

    @pytest.mark.asyncio
    async def test_guide_config_get_current_project_action(self):
        """Test guide_config with get_current_project action."""
        data = {"action": "get_current_project"}
        result = await guide_config(data)

        assert result["success"] is True
        # Project name comes from PWD in test environment
        assert "project" in result
        assert isinstance(result["project"], str)
        assert len(result["project"]) > 0
