"""Tests for corrupted JSON handling."""

import json


def test_discovery_handles_corrupted_json_gracefully(temp_project_dir):
    """Test discovery handles corrupted JSON gracefully for various document types."""
    from mcp_server_guide.models.category import Category
    from mcp_server_guide.services.document_discovery import get_category_documents

    category_dir = temp_project_dir
    docs_dir = category_dir / "__docs__"
    docs_dir.mkdir()

    # Create valid documents with sidecars
    valid_docs = [
        ("valid.md", "text/markdown", "# Valid Document"),
        ("config.yaml", "application/yaml", "key: value"),
        ("data.json", "application/json", '{"valid": true}'),
    ]

    for filename, mime_type, content in valid_docs:
        doc_path = docs_dir / filename
        sidecar_path = docs_dir / f"{filename}_.json"

        doc_path.write_text(content)
        sidecar_path.write_text(
            json.dumps({"source_type": "manual", "content_hash": f"sha256:{filename}", "mime_type": mime_type})
        )

    # Create documents with corrupted JSON sidecars
    corrupted_docs = [
        ("corrupted.md", "# Corrupted Document"),
        ("bad.pdf", "PDF content"),
    ]

    for filename, content in corrupted_docs:
        doc_path = docs_dir / filename
        sidecar_path = docs_dir / f"{filename}_.json"

        doc_path.write_text(content)
        sidecar_path.write_text("{ invalid json content")

    category = Category(name="test", dir=str(category_dir), patterns=["*"])

    documents = get_category_documents(category)

    # Should only find the valid documents, skip the corrupted ones
    assert len(documents) == 3
    assert "valid" in documents
    assert "config" in documents
    assert "data" in documents
    assert "corrupted" not in documents
    assert "bad" not in documents
