"""Tests for DocumentInfo model."""

from pathlib import Path


def test_document_info_model_creation():
    """Test DocumentInfo model can be created with required fields."""
    from mcp_server_guide.models.document_info import DocumentInfo

    doc_info = DocumentInfo(
        path=Path("test.md"), metadata_path=Path("test.md_.json"), metadata={"source_type": "manual"}
    )

    assert doc_info.path == Path("test.md")
    assert doc_info.metadata_path == Path("test.md_.json")
    assert doc_info.metadata == {"source_type": "manual"}


def test_document_info_model_fields():
    """Test DocumentInfo model has correct field types."""
    from mcp_server_guide.models.document_info import DocumentInfo

    doc_info = DocumentInfo(path=Path("doc.md"), metadata_path=Path("doc.md_.json"), metadata={})

    assert isinstance(doc_info.path, Path)
    assert isinstance(doc_info.metadata_path, Path)
    assert isinstance(doc_info.metadata, dict)
