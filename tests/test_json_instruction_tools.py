"""Tests for JSON instruction-based tools."""

import pytest
from unittest.mock import patch, Mock, AsyncMock
from src.mcp_server_guide.tools.category_tools_json import guide_categories
from src.mcp_server_guide.tools.collection_tools_json import guide_collections
from src.mcp_server_guide.tools.document_tools_json import guide_documents
from src.mcp_server_guide.tools.content_tools_json import guide_content
from src.mcp_server_guide.tools.config_tools_json import guide_config


class TestJSONInstructionTools:
    """Test JSON instruction-based tool operations."""

    @pytest.mark.asyncio
    async def test_guide_categories_add_action(self):
        """Test guide_categories with add action."""
        data = {
            "action": "add",
            "name": "test_category",
            "dir": "test_dir",
            "patterns": ["*.md"],
            "description": "Test category",
        }

        with patch("src.mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session.get_or_create_project_config = AsyncMock(return_value=Mock())
            mock_session_class.return_value = mock_session

            with patch("src.mcp_server_guide.operations.registry.get_operation_class") as mock_get_op:
                mock_operation = Mock()
                mock_operation.execute = AsyncMock(return_value={"success": True, "message": "Category added"})
                mock_op_class = Mock()
                mock_op_class.model_validate.return_value = mock_operation
                mock_get_op.return_value = mock_op_class

                result = await guide_categories(data)

                assert result["success"] is True
                assert "message" in result
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_guide_categories_invalid_instruction(self):
        """Test guide_categories with invalid instruction format."""
        data = {"invalid_field": "value"}

        result = await guide_categories(data)

        assert result["success"] is False
        assert "No action specified" in result["error"]

    @pytest.mark.asyncio
    async def test_guide_categories_unknown_action(self):
        """Test guide_categories with unknown action."""
        data = {"action": "unknown_action"}

        result = await guide_categories(data)

        assert result["success"] is False
        assert "Unknown action 'unknown_action' for context 'category'" in result["error"]

    @pytest.mark.asyncio
    async def test_guide_collections_add_action(self):
        """Test guide_collections with add action."""
        data = {
            "action": "add",
            "name": "test_collection",
            "categories": ["cat1", "cat2"],
            "description": "Test collection",
        }

        with patch("src.mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session.get_or_create_project_config = AsyncMock(return_value=Mock())
            mock_session_class.return_value = mock_session

            with patch("src.mcp_server_guide.operations.registry.get_operation_class") as mock_get_op:
                mock_operation = Mock()
                mock_operation.execute = AsyncMock(return_value={"success": True, "message": "Collection added"})
                mock_op_class = Mock()
                mock_op_class.model_validate.return_value = mock_operation
                mock_get_op.return_value = mock_op_class

                result = await guide_collections(data)

                assert result["success"] is True

    @pytest.mark.asyncio
    async def test_guide_documents_create_action(self):
        """Test guide_documents with create action."""
        data = {"action": "create", "category_dir": "test_category", "name": "test_doc", "content": "Test content"}

        with patch("src.mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session.get_or_create_project_config = AsyncMock(return_value=Mock())
            mock_session_class.return_value = mock_session

            with patch("src.mcp_server_guide.operations.registry.get_operation_class") as mock_get_op:
                mock_operation = Mock()
                mock_operation.execute = AsyncMock(return_value={"success": True, "message": "Document created"})
                mock_op_class = Mock()
                mock_op_class.model_validate.return_value = mock_operation
                mock_get_op.return_value = mock_op_class

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

            with patch("src.mcp_server_guide.operations.registry.get_operation_class") as mock_get_op:
                mock_operation = Mock()
                mock_operation.execute = AsyncMock(return_value={"success": True, "content": "Test content"})
                mock_op_class = Mock()
                mock_op_class.model_validate.return_value = mock_operation
                mock_get_op.return_value = mock_op_class

                result = await guide_content(data)

                assert result["success"] is True

    @pytest.mark.asyncio
    async def test_guide_config_get_current_project_action(self):
        """Test guide_config with get_current_project action."""
        data = {"action": "get_current_project"}

        with patch("src.mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session.get_or_create_project_config = AsyncMock(return_value=Mock())
            mock_session_class.return_value = mock_session

            with patch("src.mcp_server_guide.operations.registry.get_operation_class") as mock_get_op:
                mock_operation = Mock()
                mock_operation.execute = AsyncMock(return_value={"success": True, "project": "test_project"})
                mock_op_class = Mock()
                mock_op_class.model_validate.return_value = mock_operation
                mock_get_op.return_value = mock_op_class

                result = await guide_config(data)

                assert result["success"] is True

    @pytest.mark.asyncio
    async def test_all_tools_handle_invalid_instructions(self):
        """Test that all JSON tools handle invalid instructions properly."""
        invalid_instruction = {"invalid": "data"}

        tools = [guide_categories, guide_collections, guide_documents, guide_content, guide_config]

        for tool in tools:
            result = await tool(invalid_instruction)
            assert result["success"] is False
            assert "No action specified" in result["error"]
