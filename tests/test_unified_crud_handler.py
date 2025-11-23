"""Tests for unified CRUD handler."""

from unittest.mock import Mock

import pytest
from src.mcp_server_guide.handlers.unified_crud_handler import UnifiedCrudHandler
from src.mcp_server_guide.models.enhanced_instruction import EnhancedInstruction


class MockCrudHandler(UnifiedCrudHandler):
    """Mock implementation of UnifiedCrudHandler for testing."""

    def _handle_add(self, instruction):
        return {"success": True, "action": "add", "name": instruction.name}

    def _handle_update(self, instruction):
        return {"success": True, "action": "update", "name": instruction.name}

    def _handle_remove(self, instruction):
        return {"success": True, "action": "remove", "name": instruction.name}

    def _handle_delete(self, instruction):
        return {"success": True, "action": "delete", "name": instruction.name}

    def _handle_list(self, instruction):
        return {"success": True, "action": "list"}

    def _handle_append(self, instruction):
        return {"success": True, "action": "append", "name": instruction.name}


class TestUnifiedCrudHandler:
    """Test unified CRUD handler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.session_manager = Mock()
        self.handler = MockCrudHandler(self.session_manager)

    def test_handle_add_instruction(self):
        """Test handling add instruction."""
        instruction = EnhancedInstruction(action="add", name="test-item")
        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "add"
        assert result["name"] == "test-item"

    def test_handle_update_instruction(self):
        """Test handling update instruction."""
        instruction = EnhancedInstruction(action="update", name="test-item")
        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "update"
        assert result["name"] == "test-item"

    def test_handle_remove_instruction(self):
        """Test handling remove instruction."""
        instruction = EnhancedInstruction(action="remove", name="test-item")
        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "remove"
        assert result["name"] == "test-item"

    def test_handle_delete_instruction(self):
        """Test handling delete instruction."""
        instruction = EnhancedInstruction(action="delete", name="test-item")
        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "delete"
        assert result["name"] == "test-item"

    def test_handle_list_instruction(self):
        """Test handling list instruction."""
        instruction = EnhancedInstruction(action="list")
        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "list"

    def test_handle_append_instruction(self):
        """Test handling append instruction."""
        instruction = EnhancedInstruction(action="append", name="test-item")
        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "append"
        assert result["name"] == "test-item"

    def test_process_data_array_valid(self):
        """Test processing valid data array."""
        instruction = EnhancedInstruction(action="add", name="test-item", data=['"content1"', '"content2"'])

        result = self.handler._process_data_array(instruction)
        assert result == ["content1", "content2"]

    def test_process_data_array_none(self):
        """Test processing when no data array present."""
        instruction = EnhancedInstruction(action="add", name="test-item")

        result = self.handler._process_data_array(instruction)
        assert result is None

    def test_process_data_array_invalid(self):
        """Test processing invalid data array."""
        instruction = EnhancedInstruction(action="add", name="test-item", data=["invalid-json"])

        with pytest.raises(ValueError, match="Invalid data array"):
            self.handler._process_data_array(instruction)

    def test_encode_response_data_valid(self):
        """Test encoding valid response data."""
        data = ["content1", "content2"]
        result = self.handler._encode_response_data(data)
        assert result == ['"content1"', '"content2"']

    def test_encode_response_data_invalid(self):
        """Test encoding invalid response data."""
        data = [123, 456]  # Non-string items

        with pytest.raises(ValueError, match="Failed to encode response data"):
            self.handler._encode_response_data(data)
