"""Tests for collection CRUD handler."""

from unittest.mock import Mock

from src.mcp_server_guide.handlers.collection_crud_handler import CollectionCrudHandler
from src.mcp_server_guide.models.enhanced_instruction import EnhancedInstruction


class TestCollectionCrudHandler:
    """Test collection CRUD handler functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.session_manager = Mock()
        self.handler = CollectionCrudHandler(self.session_manager)

    def test_handle_add_collection_valid(self):
        """Test adding a valid collection."""
        instruction = EnhancedInstruction(
            action="add", name="test-collection", categories=["docs", "guides"], description="Test collection"
        )

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "add"
        assert result["collection"]["name"] == "test-collection"
        assert result["collection"]["categories"] == ["docs", "guides"]
        assert result["collection"]["description"] == "Test collection"

    def test_handle_add_collection_missing_name(self):
        """Test adding collection without name."""
        instruction = EnhancedInstruction(action="add", categories=["docs"])

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is False
        assert "Collection name is required" in result["error"]

    def test_handle_add_collection_missing_categories(self):
        """Test adding collection without categories."""
        instruction = EnhancedInstruction(action="add", name="test-collection")

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is False
        assert "Collection categories are required" in result["error"]

    def test_handle_update_collection_valid(self):
        """Test updating a collection."""
        instruction = EnhancedInstruction(
            action="update", name="test-collection", categories=["code", "tests"], description="Updated collection"
        )

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "update"
        assert result["collection"]["name"] == "test-collection"
        assert result["collection"]["categories"] == ["code", "tests"]

    def test_handle_update_collection_missing_name(self):
        """Test updating collection without name."""
        instruction = EnhancedInstruction(action="update", categories=["docs"])

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is False
        assert "Collection name is required" in result["error"]

    def test_handle_remove_collection_valid(self):
        """Test removing a collection."""
        instruction = EnhancedInstruction(action="remove", name="test-collection")

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "remove"
        assert result["collection"] == "test-collection"

    def test_handle_remove_collection_missing_name(self):
        """Test removing collection without name."""
        instruction = EnhancedInstruction(action="remove")

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is False
        assert "Collection name is required" in result["error"]

    def test_handle_delete_collection(self):
        """Test delete collection (alias for remove)."""
        instruction = EnhancedInstruction(action="delete", name="test-collection")

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "remove"
        assert result["collection"] == "test-collection"

    def test_handle_list_collections(self):
        """Test listing collections."""
        instruction = EnhancedInstruction(action="list")

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "list"
        assert "collections" in result
        assert "count" in result
        assert isinstance(result["collections"], list)

    def test_handle_append_categories_valid(self):
        """Test appending categories to collection."""
        instruction = EnhancedInstruction(
            action="append", name="test-collection", categories=["new-category", "another-category"]
        )

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is True
        assert result["action"] == "append"
        assert result["collection"] == "test-collection"
        assert result["categories"] == ["new-category", "another-category"]

    def test_handle_append_categories_missing_name(self):
        """Test appending categories without collection name."""
        instruction = EnhancedInstruction(action="append", categories=["docs"])

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is False
        assert "Collection name is required" in result["error"]

    def test_handle_append_categories_missing_categories(self):
        """Test appending without categories."""
        instruction = EnhancedInstruction(action="append", name="test-collection")

        result = self.handler.handle_instruction(instruction)

        assert result["success"] is False
        assert "Categories to append are required" in result["error"]

    def test_validate_category_references_valid(self):
        """Test category reference validation with valid categories."""
        categories = ["docs", "guides", "tutorials"]
        result = self.handler._validate_category_references(categories)
        assert result["valid"] is True

    def test_validate_category_references_invalid_type(self):
        """Test category reference validation with invalid type."""
        categories = "docs"  # Should be list
        result = self.handler._validate_category_references(categories)
        assert result["valid"] is False
        assert "Categories must be a list" in result["error"]

    def test_validate_category_references_empty_string(self):
        """Test category reference validation with empty string."""
        categories = ["docs", "", "guides"]
        result = self.handler._validate_category_references(categories)
        assert result["valid"] is False
        assert "Category names must be non-empty strings" in result["error"]

    def test_validate_category_references_non_string_item(self):
        """Test category reference validation with non-string item."""
        categories = ["docs", 123, "guides"]
        result = self.handler._validate_category_references(categories)
        assert result["valid"] is False
        assert "Category names must be non-empty strings" in result["error"]

    def test_add_with_invalid_categories(self):
        """Test adding collection with invalid categories."""
        # Test the validation method directly since EnhancedInstruction validates categories
        result = self.handler._validate_category_references(["docs", ""])
        assert result["valid"] is False

    def test_update_with_invalid_categories(self):
        """Test updating collection with invalid categories."""
        # Test the validation method directly since EnhancedInstruction validates categories
        result = self.handler._validate_category_references("invalid")
        assert result["valid"] is False

    def test_append_with_invalid_categories(self):
        """Test appending invalid categories."""
        # Test the validation method directly since EnhancedInstruction validates categories
        result = self.handler._validate_category_references([123, 456])
        assert result["valid"] is False
