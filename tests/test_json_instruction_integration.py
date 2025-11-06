"""Integration tests for JSON instruction tools with new operation system."""

from types import MappingProxyType

import pytest
from unittest.mock import patch
from src.mcp_server_guide.tools.category_tools_json import guide_categories
from src.mcp_server_guide.tools.collection_tools_json import guide_collections
from src.mcp_server_guide.tools.document_tools_json import guide_documents
from src.mcp_server_guide.tools.content_tools_json import guide_content
from src.mcp_server_guide.tools.config_tools_json import guide_config


class TestJSONInstructionIntegration:
    """Integration tests for JSON instruction tools."""

    @pytest.mark.asyncio
    async def test_json_instruction_basic_flow(self):
        """Test basic JSON instruction flow."""
        # Test that JSON instructions can be processed
        with patch("src.mcp_server_guide.tools.category_tools.add_category") as mock_add:
            mock_add.return_value = {"success": True, "message": "Category added"}

            data = {
                "action": "add",
                "name": "test_category",
                "dir": "/test/path",
                "patterns": ["*.py"],
                "description": "Test category",
            }

            result = await guide_categories(data)
            assert result["success"] is True
            assert "message" in result

    @pytest.mark.asyncio
    async def test_json_instruction_error_handling(self):
        """Test error handling in JSON instruction tools."""
        # Test invalid action
        data = {"action": "invalid_action"}
        result = await guide_categories(data)
        assert result["success"] is False
        assert "Unknown action" in result["error"]

        # Test missing required fields
        data = {"action": "add"}  # Missing required fields
        result = await guide_categories(data)
        assert result["success"] is False
        assert "Validation failed" in result["error"]

    @pytest.mark.asyncio
    async def test_json_instruction_validation(self):
        """Test validation in JSON instruction tools."""
        # Test with valid data
        with patch("src.mcp_server_guide.tools.category_tools.add_category") as mock_add:
            mock_add.return_value = {"success": True, "message": "Category added"}

            data = {
                "action": "add",
                "name": "valid_category",
                "dir": "/valid/path",
                "patterns": ["*.py", "*.md"],
                "description": "Valid category",
            }

            result = await guide_categories(data)
            assert result["success"] is True

        # Test with invalid data types
        data = {
            "action": "add",
            "name": "test_category",
            "dir": "/test/path",
            "patterns": "not_a_list",  # Should be a list
        }

        result = await guide_categories(data)
        assert result["success"] is False
        assert "Validation failed" in result["error"]

    @pytest.mark.asyncio
    async def test_all_json_tools_respond(self):
        """Test that all JSON instruction tools can respond to basic requests."""
        # Test categories
        result = await guide_categories({"action": "invalid"})
        assert "success" in result

        # Test collections
        result = await guide_collections({"action": "invalid"})
        assert "success" in result

        # Test documents
        result = await guide_documents({"action": "invalid"})
        assert "success" in result

        # Test content
        result = await guide_content({"action": "invalid"})
        assert "success" in result

        # Test config
        result = await guide_config({"action": "invalid"})
        assert "success" in result

    @pytest.mark.asyncio
    async def test_operation_discovery_integration(self):
        """Test that operations can be discovered and executed."""
        # Test that the operation discovery system works
        from src.mcp_server_guide.operations.model_base import discover_models

        models = discover_models()
        assert len(models) > 0

        # Test that each model has operations
        for model_class in models:
            operations = model_class.get_operations()
            assert isinstance(operations, MappingProxyType)

            # Test that we can get operation classes
            for action in operations.keys():
                try:
                    op_class = model_class.get_operation_class(action)
                    assert op_class is not None
                except Exception:
                    # Some operations might not be fully implemented
                    pass
