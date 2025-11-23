"""Tests for base operation class."""

from typing import Any, Dict

import pytest
from src.mcp_server_guide.models.project_config import ProjectConfig
from src.mcp_server_guide.operations.operation_base import BaseOperation


class MockOperation(BaseOperation):
    """Mock implementation of BaseOperation."""

    test_value: str = "test"

    async def execute(self, config: ProjectConfig) -> Dict[str, Any]:
        """Test execute implementation."""
        return self._success_response(value=self.test_value)


class TestBaseOperation:
    """Test BaseOperation functionality."""

    def test_success_response(self):
        """Test _success_response method."""
        operation = MockOperation(test_value="hello")

        response = operation._success_response(data="test_data")

        assert response["success"] is True
        assert response["data"] == "test_data"

    def test_success_response_no_kwargs(self):
        """Test _success_response with no additional kwargs."""
        operation = MockOperation(test_value="hello")

        response = operation._success_response()

        assert response == {"success": True}

    def test_error_response(self):
        """Test _error_response method."""
        operation = MockOperation(test_value="hello")

        response = operation._error_response("Something went wrong")

        assert response["success"] is False
        assert response["error"] == "Something went wrong"

    @pytest.mark.asyncio
    async def test_execute_implementation(self):
        """Test that execute method can be implemented."""
        operation = MockOperation(test_value="test_value")
        config = ProjectConfig()

        result = await operation.execute(config)

        assert result["success"] is True
        assert result["value"] == "test_value"

    def test_pydantic_validation(self):
        """Test that BaseOperation uses Pydantic validation."""
        # Should work with valid data
        operation = MockOperation(test_value="valid")
        assert operation.test_value == "valid"

        # Should validate field types
        with pytest.raises(ValueError):
            MockOperation(test_value=123)  # Should be string
