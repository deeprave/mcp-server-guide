"""Tests for enhanced instruction model with flexible action placement."""

import pytest
from pydantic import ValidationError

from mcp_server_guide.models.enhanced_instruction import EnhancedInstruction


class TestActionExtraction:
    """Test action extraction from root or args level."""

    def test_action_at_root_level(self):
        """Test extracting action from root level."""
        data = {"action": "add", "name": "my-category", "dir": "docs/guides", "patterns": ["*.md", "*.txt"]}
        instruction = EnhancedInstruction(**data)
        assert instruction.action == "add"
        assert instruction.name == "my-category"
        assert instruction.dir == "docs/guides"
        assert instruction.patterns == ["*.md", "*.txt"]

    def test_action_in_args_extracted(self):
        """Test extracting action from args level."""
        data = {"name": "my-category", "dir": "docs/guides", "patterns": ["*.md", "*.txt"], "action": "add"}
        instruction = EnhancedInstruction(**data)
        assert instruction.action == "add"
        assert instruction.name == "my-category"

    def test_action_priority_root_over_args(self):
        """Test that root level action takes priority over args level."""
        data = {
            "action": "update",
            "name": "my-category",
            "dir": "docs/guides",
            "patterns": ["*.md"],
            "args": {"action": "add"},
        }
        instruction = EnhancedInstruction(**data)
        assert instruction.action == "update"

    def test_missing_action_raises_error(self):
        """Test that missing action raises validation error."""
        data = {"name": "my-category", "dir": "docs/guides", "patterns": ["*.md"]}
        with pytest.raises(ValidationError, match="Field required"):
            EnhancedInstruction(**data)

    def test_invalid_action_raises_error(self):
        """Test that invalid action raises validation error."""
        data = {"action": "invalid_action", "name": "my-category"}
        with pytest.raises(ValidationError, match="Invalid action"):
            EnhancedInstruction(**data)

    def test_valid_actions_accepted(self):
        """Test that all valid actions are accepted."""
        valid_actions = ["add", "delete", "update", "append", "remove", "list"]
        for action in valid_actions:
            data = {"action": action, "name": "test-category"}
            instruction = EnhancedInstruction(**data)
            assert instruction.action == action


class TestDataArrayHandling:
    """Test data array processing for document content."""

    def test_data_array_present(self):
        """Test instruction with data array."""
        data = {
            "action": "add",
            "name": "getting-started",
            "category": "guides",
            "data": ["# Getting Started\n\nWelcome to our API...\n"],
        }
        instruction = EnhancedInstruction(**data)
        assert instruction.data == ["# Getting Started\n\nWelcome to our API...\n"]

    def test_data_array_empty(self):
        """Test instruction with empty data array."""
        data = {"action": "add", "name": "test-doc", "data": []}
        instruction = EnhancedInstruction(**data)
        assert instruction.data == []

    def test_data_array_optional(self):
        """Test instruction without data array."""
        data = {"action": "list", "entity": "categories"}
        instruction = EnhancedInstruction(**data)
        assert instruction.data is None


class TestFlexibleFields:
    """Test flexible field handling for different entity types."""

    def test_category_fields(self):
        """Test instruction with category-specific fields."""
        data = {
            "action": "add",
            "name": "api-docs",
            "dir": "docs/api",
            "patterns": ["*.md", "*.yaml"],
            "description": "API documentation",
        }
        instruction = EnhancedInstruction(**data)
        assert instruction.name == "api-docs"
        assert instruction.dir == "docs/api"
        assert instruction.patterns == ["*.md", "*.yaml"]
        assert instruction.description == "API documentation"

    def test_collection_fields(self):
        """Test instruction with collection-specific fields."""
        data = {
            "action": "add",
            "name": "development",
            "categories": ["api-docs", "guides", "tutorials"],
            "description": "Development resources",
        }
        instruction = EnhancedInstruction(**data)
        assert instruction.name == "development"
        assert instruction.categories == ["api-docs", "guides", "tutorials"]
        assert instruction.description == "Development resources"

    def test_document_fields(self):
        """Test instruction with document-specific fields."""
        data = {
            "action": "add",
            "name": "getting-started",
            "category": "guides",
            "data": ["# Getting Started\n\nContent here...\n"],
        }
        instruction = EnhancedInstruction(**data)
        assert instruction.name == "getting-started"
        assert instruction.category == "guides"
        assert instruction.data == ["# Getting Started\n\nContent here...\n"]

    def test_list_operation_fields(self):
        """Test instruction with list operation fields."""
        data = {"action": "list", "entity": "categories", "verbose": True}
        instruction = EnhancedInstruction(**data)
        assert instruction.action == "list"
        assert instruction.entity == "categories"
        assert instruction.verbose is True
