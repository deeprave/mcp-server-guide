"""Tests for category CRUD handler."""

from unittest.mock import Mock

from src.mcp_server_guide.handlers.category_crud_handler import CategoryCrudHandler
from src.mcp_server_guide.models.enhanced_instruction import EnhancedInstruction


class TestCategoryCrudHandler:
    """Test category CRUD handler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.session_manager = Mock()
        self.handler = CategoryCrudHandler(self.session_manager)

    def test_handle_add_category_valid(self):
        """Test adding a valid category."""
        instruction = EnhancedInstruction(
            action="add", name="test-category", dir="./test", patterns=["*.md", "*.txt"], description="Test category"
        )

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "add"
        assert result["category"]["name"] == "test-category"
        assert result["category"]["dir"] == "./test"
        assert result["category"]["patterns"] == ["*.md", "*.txt"]
        assert result["category"]["description"] == "Test category"

    def test_handle_add_category_missing_name(self):
        """Test adding category without name."""
        instruction = EnhancedInstruction(action="add", dir="./test", patterns=["*.md"])

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is False
        assert "Category name is required" in result["error"]

    def test_handle_add_category_missing_dir(self):
        """Test adding category without directory."""
        instruction = EnhancedInstruction(action="add", name="test-category", patterns=["*.md"])

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is False
        assert "Category directory is required" in result["error"]

    def test_handle_add_category_missing_patterns(self):
        """Test adding category without patterns."""
        instruction = EnhancedInstruction(action="add", name="test-category", dir="./test")

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is False
        assert "Category patterns are required" in result["error"]

    def test_handle_update_category_valid(self):
        """Test updating a category."""
        instruction = EnhancedInstruction(
            action="update",
            name="test-category",
            dir="./updated",
            patterns=["*.py", "*.js"],
            description="Updated category",
        )

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "update"
        assert result["category"]["name"] == "test-category"
        assert result["category"]["dir"] == "./updated"
        assert result["category"]["patterns"] == ["*.py", "*.js"]

    def test_handle_update_category_missing_name(self):
        """Test updating category without name."""
        instruction = EnhancedInstruction(action="update", dir="./test")

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is False
        assert "Category name is required" in result["error"]

    def test_handle_remove_category_valid(self):
        """Test removing a category."""
        instruction = EnhancedInstruction(action="remove", name="test-category")

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "remove"
        assert result["category"] == "test-category"

    def test_handle_remove_category_missing_name(self):
        """Test removing category without name."""
        instruction = EnhancedInstruction(action="remove")

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is False
        assert "Category name is required" in result["error"]

    def test_handle_delete_category(self):
        """Test delete category (alias for remove)."""
        instruction = EnhancedInstruction(action="delete", name="test-category")

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "remove"
        assert result["category"] == "test-category"

    def test_handle_list_categories(self):
        """Test listing categories."""
        instruction = EnhancedInstruction(action="list")

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "list"
        assert "categories" in result
        assert "count" in result
        assert isinstance(result["categories"], list)

    def test_handle_append_patterns_valid(self):
        """Test appending patterns to category."""
        instruction = EnhancedInstruction(action="append", name="test-category", patterns=["*.json", "*.yaml"])

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "append"
        assert result["category"] == "test-category"
        assert result["patterns"] == ["*.json", "*.yaml"]

    def test_handle_append_patterns_missing_name(self):
        """Test appending patterns without category name."""
        instruction = EnhancedInstruction(action="append", patterns=["*.json"])

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is False
        assert "Category name is required" in result["error"]

    def test_handle_append_patterns_missing_patterns(self):
        """Test appending without patterns."""
        instruction = EnhancedInstruction(action="append", name="test-category")

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is False
        assert "Patterns to append are required" in result["error"]

    def test_validate_patterns_valid(self):
        """Test pattern validation with valid patterns."""
        patterns = ["*.md", "*.txt", "**/*.py"]
        result = self.handler._validate_patterns(patterns)
        assert result is True

    def test_validate_patterns_invalid_type(self):
        """Test pattern validation with invalid type."""
        patterns = "*.md"  # Should be list
        result = self.handler._validate_patterns(patterns)
        assert result is False

    def test_validate_patterns_empty_string(self):
        """Test pattern validation with empty string."""
        patterns = ["*.md", "", "*.txt"]
        result = self.handler._validate_patterns(patterns)
        assert result is False

    def test_validate_patterns_non_string_item(self):
        """Test pattern validation with non-string item."""
        patterns = ["*.md", 123, "*.txt"]
        result = self.handler._validate_patterns(patterns)
        assert result is False

    def test_update_with_invalid_patterns(self):
        """Test updating category with invalid patterns."""
        # Test the validation method directly since EnhancedInstruction validates patterns
        result = self.handler._validate_patterns(["*.md", ""])
        assert result is False
