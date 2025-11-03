"""Tests for orphaned metadata handling."""

import json


def test_discovery_ignores_orphaned_metadata(temp_project_dir):
    """Test discovery ignores orphaned metadata files for various document types."""
    from mcp_server_guide.services.document_discovery import get_category_documents
    from mcp_server_guide.models.category import Category

    category_dir = temp_project_dir
    docs_dir = category_dir / "__docs__"
    docs_dir.mkdir()

    # Create valid documents with sidecars
    valid_docs = [
        ("valid.md", "text/markdown", "# Valid Document"),
        ("config.yaml", "application/yaml", "key: value"),
    ]

    for filename, mime_type, content in valid_docs:
        doc_path = docs_dir / filename
        sidecar_path = docs_dir / f"{filename}_.json"

        doc_path.write_text(content)
        sidecar_path.write_text(
            json.dumps({"source_type": "manual", "content_hash": f"sha256:{filename}", "mime_type": mime_type})
        )

    # Create orphaned metadata files (no corresponding document files)
    orphaned_sidecars = ["orphaned.md_.json", "missing.pdf_.json", "gone.yaml_.json"]

    for sidecar_name in orphaned_sidecars:
        orphaned_sidecar = docs_dir / sidecar_name
        orphaned_sidecar.write_text(
            json.dumps({"source_type": "manual", "content_hash": "sha256:orphaned", "mime_type": "text/markdown"})
        )

    category = Category(name="test", dir=str(category_dir), patterns=["*"])

    documents = get_category_documents(category)

    # Should only find the valid documents, not the orphaned metadata
    assert len(documents) == 2
    assert "valid" in documents
    assert "config" in documents
    assert "orphaned" not in documents
    assert "missing" not in documents
    assert "gone" not in documents
