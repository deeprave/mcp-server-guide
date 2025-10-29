"""Tests for DocumentMetadata Pydantic model."""


def test_document_metadata_model_creation():
    """Test DocumentMetadata model can be created with known fields."""
    from mcp_server_guide.models.document_metadata import DocumentMetadata

    metadata = DocumentMetadata(source_type="manual", content_hash="sha256:abc123", mime_type="text/markdown")

    assert metadata.source_type == "manual"
    assert metadata.content_hash == "sha256:abc123"
    assert metadata.mime_type == "text/markdown"


def test_document_metadata_unknown_field_preservation():
    """Test DocumentMetadata preserves unknown fields via extra='allow'."""
    from mcp_server_guide.models.document_metadata import DocumentMetadata

    data = {
        "source_type": "spec-kit",
        "content_hash": "sha256:def456",
        "mime_type": "text/plain",
        "unknown_field": "preserved_value",
        "future_field": {"nested": "data"},
    }

    metadata = DocumentMetadata(**data)

    # Known fields
    assert metadata.source_type == "spec-kit"
    assert metadata.content_hash == "sha256:def456"
    assert metadata.mime_type == "text/plain"

    # Unknown fields preserved
    assert metadata.unknown_field == "preserved_value"
    assert metadata.future_field == {"nested": "data"}


def test_document_metadata_serialization_includes_unknown_fields():
    """Test DocumentMetadata serialization includes unknown fields."""
    from mcp_server_guide.models.document_metadata import DocumentMetadata

    data = {
        "source_type": "imported",
        "content_hash": "sha256:ghi789",
        "mime_type": "application/json",
        "custom_field": "custom_value",
    }

    metadata = DocumentMetadata(**data)
    serialized = metadata.model_dump()

    assert serialized["source_type"] == "imported"
    assert serialized["content_hash"] == "sha256:ghi789"
    assert serialized["mime_type"] == "application/json"
    assert serialized["custom_field"] == "custom_value"
