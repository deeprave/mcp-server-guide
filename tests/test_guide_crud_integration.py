"""Tests for guide CRUD integration functionality."""

from unittest.mock import patch

import pytest
from src.mcp_server_guide.guide_integration import GuidePromptHandler


class TestGuideCRUDIntegration:
    """Test guide CRUD integration functionality."""

    @pytest.fixture
    def handler(self):
        """Create a guide prompt handler."""
        return GuidePromptHandler()

    def _wrap_expected_output(self, content: str) -> str:
        """Helper to wrap expected output with display markers."""
        return f"=== DISPLAY CONTENT FOR USER ===\n{content}\n=== END DISPLAY CONTENT ===\n\n**Instruction**: Stop immediately and return to prompt. Do nothing.\n"

    @pytest.mark.asyncio
    async def test_category_list_crud_operation(self, handler):
        """Test category list CRUD operation."""
        with patch("src.mcp_server_guide.operations.base.execute_json_operation") as mock_execute:
            mock_execute.return_value = {"success": True, "categories": {}}

            result = await handler.handle_guide_request(["category", "list"])

            expected = self._wrap_expected_output("No categories found.")
            assert result == expected
            mock_execute.assert_called_once_with("category", {"verbose": False, "action": "list"})

    @pytest.mark.asyncio
    async def test_category_list_with_items(self, handler):
        """Test category list with items."""
        with patch("src.mcp_server_guide.operations.base.execute_json_operation") as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "categories": {"docs": {"description": "Documentation files"}, "code": {"description": "Source code"}},
            }

            result = await handler.handle_guide_request(["category", "list"])

            expected_content = "Categories:\n  - docs\n  - code"
            expected = self._wrap_expected_output(expected_content)
            assert result == expected

    @pytest.mark.asyncio
    async def test_category_list_verbose(self, handler):
        """Test category list with verbose output."""
        with patch("src.mcp_server_guide.operations.base.execute_json_operation") as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "categories": {"docs": {"description": "Documentation files"}, "code": {"description": "Source code"}},
            }

            result = await handler.handle_guide_request(["category", "list", "--verbose"])

            expected_content = "Categories:\n  - docs: Documentation files\n  - code: Source code"
            expected = self._wrap_expected_output(expected_content)
            assert result == expected

    @pytest.mark.asyncio
    async def test_collection_list_crud_operation(self, handler):
        """Test collection list CRUD operation."""
        with patch("src.mcp_server_guide.operations.base.execute_json_operation") as mock_execute:
            mock_execute.return_value = {"success": True, "items": []}

            result = await handler.handle_guide_request(["collection", "list"])

            expected = self._wrap_expected_output("No collections found.")
            assert result == expected
            mock_execute.assert_called_once_with("collection", {"verbose": False, "action": "list"})

    @pytest.mark.asyncio
    async def test_document_list_crud_operation(self, handler):
        """Test document list CRUD operation."""
        with patch("src.mcp_server_guide.operations.base.execute_json_operation") as mock_execute:
            mock_execute.return_value = {"success": True, "items": []}

            result = await handler.handle_guide_request(["document", "list"])

            expected = self._wrap_expected_output("No documents found.")
            assert result == expected
            mock_execute.assert_called_once_with("document", {"action": "list"})

    @pytest.mark.asyncio
    async def test_category_add_crud_operation(self, handler):
        """Test category add CRUD operation."""
        with patch("src.mcp_server_guide.operations.base.execute_json_operation") as mock_execute:
            mock_execute.return_value = {"success": True, "message": "Category added successfully"}

            result = await handler.handle_guide_request(
                ["category", "add", "test", "*.md", "--description", "Test category"]
            )

            expected = self._wrap_expected_output("Category added successfully")
            assert result == expected
            mock_execute.assert_called_once_with(
                "category", {"action": "add", "name": "test", "patterns": ["*.md"], "description": "Test category"}
            )

    @pytest.mark.asyncio
    async def test_crud_operation_error(self, handler):
        """Test CRUD operation error handling."""
        with patch("src.mcp_server_guide.operations.base.execute_json_operation") as mock_execute:
            mock_execute.return_value = {"success": False, "error": "Category not found"}

            result = await handler.handle_guide_request(["category", "remove", "nonexistent"])

            expected = self._wrap_expected_output("Error: Category not found")
            assert result == expected

    @pytest.mark.asyncio
    async def test_crud_operation_exception(self, handler):
        """Test CRUD operation exception handling."""
        with patch("src.mcp_server_guide.operations.base.execute_json_operation") as mock_execute:
            mock_execute.side_effect = Exception("Database error")

            result = await handler.handle_guide_request(["category", "list"])

            assert "Error executing list on category: Database error" in result

    @pytest.mark.asyncio
    async def test_crud_operation_success_without_message(self, handler):
        """Test CRUD operation success without explicit message."""
        with patch("src.mcp_server_guide.operations.base.execute_json_operation") as mock_execute:
            mock_execute.return_value = {"success": True}

            result = await handler.handle_guide_request(["category", "remove", "test"])

            expected = self._wrap_expected_output("Remove operation completed successfully.")
            assert result == expected
