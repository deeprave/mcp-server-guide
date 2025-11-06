"""Tests for schema generation functionality."""

import pytest
import json
from unittest.mock import Mock, patch
from src.mcp_server_guide.operations.schema_generator import (
    generate_tool_description,
    get_all_schemas,
    get_schema_for_context,
    _extract_schema_info,
    _generate_example_data,
)
from src.mcp_server_guide.tools.schema_tools import (
    guide_get_schemas,
    guide_get_schema,
    generate_description,
)


class TestSchemaGenerator:
    """Test schema generation functions."""

    def test_extract_schema_info(self):
        """Test _extract_schema_info function."""
        # Mock operation class
        mock_operation = Mock()
        mock_operation.model_json_schema.return_value = {
            "required": ["action", "name", "description"],
            "properties": {"action": {"type": "string"}, "name": {"type": "string"}, "description": {"type": "string"}},
        }

        operations = {"add": mock_operation}
        mock_model = Mock()

        result = _extract_schema_info(operations, mock_model)

        assert len(result) == 1
        assert "add: name, description" in result[0]

    def test_extract_schema_info_no_required_fields(self):
        """Test _extract_schema_info with no required fields."""
        mock_operation = Mock()
        mock_operation.model_json_schema.return_value = {
            "required": ["action"],
            "properties": {"action": {"type": "string"}},
        }

        operations = {"list": mock_operation}
        mock_model = Mock()

        result = _extract_schema_info(operations, mock_model)

        assert len(result) == 1
        assert "list: (no additional fields)" in result[0]

    def test_extract_schema_info_exception(self):
        """Test _extract_schema_info with exception."""
        mock_operation = Mock()
        mock_operation.model_json_schema.side_effect = Exception("Schema error")

        operations = {"error": mock_operation}
        mock_model = Mock()

        result = _extract_schema_info(operations, mock_model)

        assert len(result) == 1
        assert "error: (schema unavailable)" in result[0]

    def test_generate_example_data(self):
        """Test _generate_example_data function."""
        mock_operation = Mock()
        mock_operation.model_json_schema.return_value = {
            "required": ["action", "name"],
            "properties": {
                "action": {"type": "string"},
                "name": {"type": "string"},
                "categories": {"type": "array"},
                "enabled": {"type": "boolean"},
            },
        }

        mock_model = Mock()
        mock_model.get_operations.return_value = {"add": mock_operation}

        result = _generate_example_data("test", mock_model)

        # Parse the JSON to verify structure
        example = json.loads(result)
        assert example["action"] == "add"
        assert "name" in example
        assert example["name"] == "example_name"

    def test_generate_example_data_no_operations(self):
        """Test _generate_example_data with no operations."""
        mock_model = Mock()
        mock_model.get_operations.return_value = {}

        result = _generate_example_data("test", mock_model)

        example = json.loads(result)
        assert example["action"] == "example"

    @patch("src.mcp_server_guide.operations.schema_generator.discover_models")
    def test_generate_tool_description(self, mock_discover):
        """Test generate_tool_description function."""
        # Mock model class
        mock_model = Mock()
        mock_model.__name__ = "CategoryModel"
        mock_operation = Mock()
        mock_operation.model_json_schema.return_value = {
            "required": ["action", "name"],
            "properties": {"action": {"type": "string"}, "name": {"type": "string"}},
        }
        mock_model.get_operations.return_value = {"add": mock_operation}

        mock_discover.return_value = [mock_model]

        result = generate_tool_description("category")

        assert "Handle category operations via JSON instructions" in result
        assert "SCHEMA - Valid actions and arguments for category:" in result
        assert "add: name" in result
        assert "EXAMPLE:" in result

    @patch("src.mcp_server_guide.operations.schema_generator.discover_models")
    def test_generate_tool_description_no_model(self, mock_discover):
        """Test generate_tool_description with no matching model."""
        mock_discover.return_value = []

        result = generate_tool_description("nonexistent")

        assert result == "Handle nonexistent operations via JSON instructions."

    @patch("src.mcp_server_guide.operations.schema_generator.discover_models")
    def test_get_all_schemas(self, mock_discover):
        """Test get_all_schemas function."""
        # Mock model class
        mock_model = Mock()
        mock_model.__name__ = "CategoryModel"
        mock_operation = Mock()
        mock_operation.model_json_schema.return_value = {
            "required": ["action", "name"],
            "properties": {"action": {"type": "string"}, "name": {"type": "string"}},
        }
        mock_model.get_operations.return_value = {"add": mock_operation}

        mock_discover.return_value = [mock_model]

        result = get_all_schemas()

        assert "category" in result
        assert result["category"]["entity_type"] == "category"
        assert "actions" in result["category"]
        assert "add" in result["category"]["actions"]

    @patch("src.mcp_server_guide.operations.schema_generator.get_all_schemas")
    def test_get_schema_for_context(self, mock_get_all):
        """Test get_schema_for_context function."""
        mock_get_all.return_value = {"category": {"entity_type": "category", "actions": {"add": {}}}}

        result = get_schema_for_context("category")

        assert result["entity_type"] == "category"
        assert "actions" in result

    @patch("src.mcp_server_guide.operations.schema_generator.get_all_schemas")
    def test_get_schema_for_context_not_found(self, mock_get_all):
        """Test get_schema_for_context with non-existent context."""
        mock_get_all.return_value = {}

        result = get_schema_for_context("nonexistent")

        assert result == {}


class TestSchemaTools:
    """Test schema tools functions."""

    @pytest.mark.asyncio
    @patch("src.mcp_server_guide.tools.schema_tools.get_all_schemas")
    async def test_guide_get_schemas_success(self, mock_get_all):
        """Test guide_get_schemas success case."""
        mock_get_all.return_value = {"category": {"entity_type": "category"}}

        result = await guide_get_schemas()

        assert result["success"] is True
        assert "schemas" in result
        assert result["total_contexts"] == 1

    @pytest.mark.asyncio
    @patch("src.mcp_server_guide.tools.schema_tools.get_all_schemas")
    async def test_guide_get_schemas_error(self, mock_get_all):
        """Test guide_get_schemas error case."""
        mock_get_all.side_effect = Exception("Schema error")

        result = await guide_get_schemas()

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    @patch("src.mcp_server_guide.tools.schema_tools.get_schema_for_context")
    async def test_guide_get_schema_success(self, mock_get_schema):
        """Test guide_get_schema success case."""
        mock_get_schema.return_value = {"entity_type": "category"}

        result = await guide_get_schema("category")

        assert result["success"] is True
        assert result["context"] == "category"
        assert "schema" in result

    @pytest.mark.asyncio
    @patch("src.mcp_server_guide.tools.schema_tools.get_schema_for_context")
    async def test_guide_get_schema_not_found(self, mock_get_schema):
        """Test guide_get_schema with non-existent context."""
        mock_get_schema.return_value = {}

        result = await guide_get_schema("nonexistent")

        assert result["success"] is False
        assert "No schema found for context" in result["error"]

    @pytest.mark.asyncio
    @patch("src.mcp_server_guide.tools.schema_tools.generate_tool_description")
    async def test_generate_description_success(self, mock_generate):
        """Test generate_description success case."""
        mock_generate.return_value = "Test description"

        result = await generate_description("category")

        assert result["success"] is True
        assert result["entity_type"] == "category"
        assert result["description"] == "Test description"

    @pytest.mark.asyncio
    @patch("src.mcp_server_guide.tools.schema_tools.generate_tool_description")
    async def test_generate_description_error(self, mock_generate):
        """Test generate_description error case."""
        mock_generate.side_effect = Exception("Generation error")

        result = await generate_description("category")

        assert result["success"] is False
        assert "error" in result
