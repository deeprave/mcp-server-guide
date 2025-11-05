"""Tests for CRUD operation base classes."""

import pytest
from typing import Dict, Any
from src.mcp_server_guide.operations.crud import AddOperation, UpdateOperation, RemoveOperation, ListOperation
from src.mcp_server_guide.models.project_config import ProjectConfig


class MockAddOperation(AddOperation[str]):
    """Mock implementation of AddOperation."""

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        """Test execute implementation."""
        return self._success_response(added=self.name)


class MockUpdateOperation(UpdateOperation[str]):
    """Mock implementation of UpdateOperation."""

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        """Test execute implementation."""
        return self._success_response(updated=self.name)


class MockRemoveOperation(RemoveOperation[str]):
    """Mock implementation of RemoveOperation."""

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        """Test execute implementation."""
        return self._success_response(removed=self.name)


class MockListOperation(ListOperation[str]):
    """Mock implementation of ListOperation."""

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        """Test execute implementation."""
        return self._success_response(verbose=self.verbose)


class TestCRUDOperations:
    """Test CRUD operation base classes."""

    def test_add_operation_validation(self):
        """Test AddOperation validation."""
        # Valid operation
        op = MockAddOperation(name="test", description="Test description")
        assert op.name == "test"
        assert op.description == "Test description"

        # Missing required field
        with pytest.raises(ValueError):
            MockAddOperation(description="Missing name")

    def test_update_operation_validation(self):
        """Test UpdateOperation validation."""
        # Valid operation
        op = MockUpdateOperation(name="test", description="Updated description")
        assert op.name == "test"
        assert op.description == "Updated description"

        # Only name required
        op2 = MockUpdateOperation(name="test")
        assert op2.name == "test"
        assert op2.description is None

    def test_remove_operation_validation(self):
        """Test RemoveOperation validation."""
        # Valid operation
        op = MockRemoveOperation(name="test")
        assert op.name == "test"

        # Missing required field
        with pytest.raises(ValueError):
            MockRemoveOperation()

    def test_list_operation_validation(self):
        """Test ListOperation validation."""
        # Valid operation with verbose
        op = MockListOperation(verbose=True)
        assert op.verbose is True

        # Default verbose should be False
        op2 = MockListOperation()
        assert op2.verbose is False

    @pytest.mark.asyncio
    async def test_add_operation_execute(self):
        """Test AddOperation execute method."""
        op = MockAddOperation(name="test_item", description="Test")
        config = ProjectConfig()

        result = await op.execute(config)

        assert result["success"] is True
        assert result["added"] == "test_item"

    @pytest.mark.asyncio
    async def test_update_operation_execute(self):
        """Test UpdateOperation execute method."""
        op = MockUpdateOperation(name="test_item")
        config = ProjectConfig()

        result = await op.execute(config)

        assert result["success"] is True
        assert result["updated"] == "test_item"

    @pytest.mark.asyncio
    async def test_remove_operation_execute(self):
        """Test RemoveOperation execute method."""
        op = MockRemoveOperation(name="test_item")
        config = ProjectConfig()

        result = await op.execute(config)

        assert result["success"] is True
        assert result["removed"] == "test_item"

    @pytest.mark.asyncio
    async def test_list_operation_execute(self):
        """Test ListOperation execute method."""
        op = MockListOperation(verbose=True)
        config = ProjectConfig()

        result = await op.execute(config)

        assert result["success"] is True
        assert result["verbose"] is True
