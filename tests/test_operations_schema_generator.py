"""Tests for operations schema generator."""

import json
from src.mcp_server_guide.operations.schema_generator import generate_tool_description
from src.mcp_server_guide.operations.registry import OPERATION_REGISTRY


class TestSchemaGenerator:
    """Test schema generation functionality."""

    def test_generate_tool_description_with_valid_entity(self):
        """Test generating tool description for valid entity type."""
        description = generate_tool_description("category")

        assert "Handle category operations via JSON instructions" in description
        assert "SCHEMA - Valid actions and arguments for category:" in description
        assert "add:" in description
        assert "Example JSON:" in description

        # Verify it contains valid JSON
        lines = description.split("\n")
        json_start = None
        for i, line in enumerate(lines):
            if line.strip() == "Example JSON:":
                json_start = i + 1
                break

        assert json_start is not None
        json_lines = lines[json_start:]
        json_text = "\n".join(json_lines)

        # Should be valid JSON
        parsed = json.loads(json_text)
        assert "action" in parsed

    def test_generate_tool_description_with_invalid_entity(self):
        """Test generating tool description for invalid entity type."""
        description = generate_tool_description("nonexistent")

        assert description == "Handle nonexistent operations via JSON instructions."

    def test_generate_tool_description_includes_required_fields(self):
        """Test that description includes required fields for actions."""
        description = generate_tool_description("category")

        # Should show required fields for add action
        assert "add:" in description
        assert "name" in description

    def test_generate_tool_description_handles_no_additional_fields(self):
        """Test description for actions with no additional required fields."""
        description = generate_tool_description("config")

        # Config operations like get_current_project have no additional fields
        assert "get_current_project: (no additional fields)" in description

    def test_generate_tool_description_example_json_structure(self):
        """Test that example JSON has proper structure."""
        description = generate_tool_description("category")

        # Extract JSON from description
        lines = description.split("\n")
        json_start = None
        for i, line in enumerate(lines):
            if line.strip() == "Example JSON:":
                json_start = i + 1
                break

        json_lines = lines[json_start:]
        json_text = "\n".join(json_lines)
        parsed = json.loads(json_text)

        assert "action" in parsed
        assert isinstance(parsed["action"], str)

        # Should have example values for required fields
        if "name" in parsed:
            assert parsed["name"] == "example_value"

    def test_generate_tool_description_handles_different_field_types(self):
        """Test that example generation handles different field types correctly."""
        # This tests the field type handling in the example generation
        description = generate_tool_description("category")

        lines = description.split("\n")
        json_start = None
        for i, line in enumerate(lines):
            if line.strip() == "Example JSON:":
                json_start = i + 1
                break

        json_lines = lines[json_start:]
        json_text = "\n".join(json_lines)
        parsed = json.loads(json_text)

        # Check that string fields get string values
        for key, value in parsed.items():
            if key != "action" and isinstance(value, str):
                assert value in ["example_value", "value"]

    def test_generate_tool_description_with_all_registered_entities(self):
        """Test description generation for all registered entity types."""
        for entity_type in OPERATION_REGISTRY.keys():
            description = generate_tool_description(entity_type)

            assert f"Handle {entity_type} operations via JSON instructions" in description
            assert "SCHEMA" in description or description.endswith("operations via JSON instructions.")
