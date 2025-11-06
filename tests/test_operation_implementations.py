"""Tests for operation implementations."""

import pytest
from unittest.mock import Mock, patch
from src.mcp_server_guide.operations.collection_ops import (
    CollectionAddOperation,
    CollectionUpdateOperation,
    CollectionRemoveOperation,
    CollectionListOperation,
    AddToCollectionOperation,
    RemoveFromCollectionOperation,
    GetCollectionContentOperation,
)
from src.mcp_server_guide.operations.config_ops import (
    GetCurrentProjectOperation,
    GetProjectConfigOperation,
    SetProjectConfigOperation,
    SetProjectConfigValuesOperation,
    SwitchProjectOperation,
)
from src.mcp_server_guide.operations.content_ops import (
    GetContentOperation,
    SearchContentOperation,
    GetFileContentOperation,
)
from src.mcp_server_guide.operations.document_ops import (
    DocumentCreateOperation,
    DocumentUpdateOperation,
    DocumentDeleteOperation,
    DocumentListOperation,
)


class TestOperationInstantiation:
    """Test that operation classes can be instantiated correctly."""

    def test_collection_operations_instantiation(self):
        """Test collection operation instantiation."""
        # Test required fields
        op1 = CollectionAddOperation(name="test", categories=["cat1"])
        assert op1.name == "test"
        assert op1.categories == ["cat1"]

        op2 = CollectionUpdateOperation(name="test")
        assert op2.name == "test"

        op3 = CollectionRemoveOperation(name="test")
        assert op3.name == "test"

        op4 = CollectionListOperation()
        assert op4.verbose is False  # Default value

        op5 = AddToCollectionOperation(name="test", categories=["cat1"])
        assert op5.name == "test"

        op6 = RemoveFromCollectionOperation(name="test", categories=["cat1"])
        assert op6.name == "test"

        op7 = GetCollectionContentOperation(name="test")
        assert op7.name == "test"

    def test_config_operations_instantiation(self):
        """Test config operation instantiation."""
        GetCurrentProjectOperation()
        # No required fields

        op2 = GetProjectConfigOperation()
        assert op2.project is None  # Default value

        op3 = SetProjectConfigOperation(config_key="key", value="value")
        assert op3.config_key == "key"
        assert op3.value == "value"

        op4 = SetProjectConfigValuesOperation(config_dict={"key": "value"})
        assert op4.config_dict == {"key": "value"}

        op5 = SwitchProjectOperation(name="project")
        assert op5.name == "project"

    def test_content_operations_instantiation(self):
        """Test content operation instantiation."""
        op1 = GetContentOperation(category_or_collection="cat", document="doc")
        assert op1.category_or_collection == "cat"
        assert op1.document == "doc"

        op2 = SearchContentOperation(query="test")
        assert op2.query == "test"
        assert op2.project is None  # Default value

        op3 = GetFileContentOperation(path="/test/path")
        assert op3.path == "/test/path"
        assert op3.project is None  # Default value

    def test_document_operations_instantiation(self):
        """Test document operation instantiation."""
        op1 = DocumentCreateOperation(name="doc", category_dir="cat", content="content")
        assert op1.name == "doc"
        assert op1.category_dir == "cat"
        assert op1.content == "content"
        assert op1.source_type == "manual"  # Default value

        op2 = DocumentUpdateOperation(name="doc", category_dir="cat", content="content")
        assert op2.name == "doc"

        op3 = DocumentDeleteOperation(name="doc", category_dir="cat")
        assert op3.name == "doc"

        op4 = DocumentListOperation(category_dir="cat")
        assert op4.category_dir == "cat"
        assert op4.mime_type is None  # Default value


class TestOperationExecution:
    """Test operation execution with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_collection_add_execution(self):
        """Test CollectionAddOperation execution."""
        with patch("src.mcp_server_guide.operations.collection_ops.add_collection") as mock_add:
            mock_add.return_value = {"success": True}

            operation = CollectionAddOperation(name="test", categories=["cat1"])
            result = await operation.execute(Mock())

            assert result["success"] is True
            mock_add.assert_called_once()

    @pytest.mark.asyncio
    async def test_config_get_current_project_execution(self):
        """Test GetCurrentProjectOperation execution."""
        with patch("src.mcp_server_guide.operations.config_ops.get_current_project") as mock_get:
            mock_get.return_value = "test_project"

            operation = GetCurrentProjectOperation()
            result = await operation.execute(Mock())

            assert result["success"] is True
            assert result["project"] == "test_project"

    @pytest.mark.asyncio
    async def test_content_get_execution(self):
        """Test GetContentOperation execution."""
        with patch("src.mcp_server_guide.operations.content_ops.get_content") as mock_get:
            mock_get.return_value = "test content"

            operation = GetContentOperation(category_or_collection="cat", document="doc")
            result = await operation.execute(Mock())

            assert result["success"] is True
            assert result["content"] == "test content"

    @pytest.mark.asyncio
    async def test_document_create_execution(self):
        """Test DocumentCreateOperation execution."""
        with patch("src.mcp_server_guide.operations.document_ops.create_mcp_document") as mock_create:
            mock_create.return_value = {"success": True}

            operation = DocumentCreateOperation(name="doc", category_dir="cat", content="content")
            result = await operation.execute(Mock())

            assert result["success"] is True
            mock_create.assert_called_once()


class TestOperationValidation:
    """Test operation validation."""

    def test_required_fields_validation(self):
        """Test that required fields are validated."""
        # This should work
        CollectionAddOperation(name="test", categories=["cat1"])

        # This should raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            CollectionAddOperation()  # Missing required fields

    def test_optional_fields_defaults(self):
        """Test that optional fields have correct defaults."""
        op = CollectionListOperation()
        assert op.verbose is False

        op = GetProjectConfigOperation()
        assert op.project is None

        op = DocumentCreateOperation(name="doc", category_dir="cat", content="content")
        assert op.source_type == "manual"
        assert op.mime_type is None
