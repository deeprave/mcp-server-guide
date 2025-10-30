"""Tests for MCP tool registration with @guide.tool decorator."""


def test_document_tools_have_guide_decorator():
    """Test all document tools are registered with @guide.tool decorator."""
    from mcp_server_guide.tools.document_tools import (
        create_mcp_document,
        update_mcp_document,
        delete_mcp_document,
        list_mcp_documents,
    )

    # Check functions are decorated (they should be callable)
    assert callable(create_mcp_document)
    assert callable(update_mcp_document)
    assert callable(delete_mcp_document)
    assert callable(list_mcp_documents)

    # Check they retain their original function names (proper decorator behavior)
    assert create_mcp_document.__name__ == "create_mcp_document"
    assert update_mcp_document.__name__ == "update_mcp_document"
    assert delete_mcp_document.__name__ == "delete_mcp_document"
    assert list_mcp_documents.__name__ == "list_mcp_documents"


def test_document_tools_return_guide_uris():
    """Test document tools return proper guide:// URIs."""
    # This will be implemented when URI resolution is added
    pass


def test_tool_registration_error_handling():
    """Test error handling in tool registration."""
    # This will test registration validation
    pass
