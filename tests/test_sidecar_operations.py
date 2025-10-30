"""Tests for sidecar metadata operations."""

import json
import tempfile
import os
from pathlib import Path


def test_create_sidecar_metadata():
    """Test creating sidecar metadata file."""
    from mcp_server_guide.utils.sidecar_operations import create_sidecar_metadata
    from mcp_server_guide.models.document_metadata import DocumentMetadata

    with tempfile.TemporaryDirectory() as temp_dir:
        doc_path = Path(temp_dir) / "test.md"
        metadata = DocumentMetadata(source_type="manual", content_hash="sha256:abc123", mime_type="text/markdown")

        create_sidecar_metadata(doc_path, metadata)

        # Check sidecar file was created
        sidecar_path = Path(temp_dir) / "test.md_.json"
        assert sidecar_path.exists()

        # Check content
        with open(sidecar_path) as f:
            data = json.load(f)

        assert data["source_type"] == "manual"
        assert data["content_hash"] == "sha256:abc123"
        assert data["mime_type"] == "text/markdown"


def test_read_sidecar_metadata():
    """Test reading sidecar metadata file."""
    from mcp_server_guide.utils.sidecar_operations import read_sidecar_metadata

    with tempfile.TemporaryDirectory() as temp_dir:
        doc_path = Path(temp_dir) / "test.md"
        sidecar_path = Path(temp_dir) / "test.md_.json"

        # Create sidecar file
        metadata_data = {
            "source_type": "spec-kit",
            "content_hash": "sha256:def456",
            "mime_type": "text/plain",
            "custom_field": "custom_value",
        }

        with open(sidecar_path, "w") as f:
            json.dump(metadata_data, f)

        # Read it back
        metadata = read_sidecar_metadata(doc_path)

        assert metadata.source_type == "spec-kit"
        assert metadata.content_hash == "sha256:def456"
        assert metadata.mime_type == "text/plain"
        assert metadata.custom_field == "custom_value"


def test_read_sidecar_metadata_missing_file():
    """Test reading sidecar metadata when file doesn't exist."""
    from mcp_server_guide.utils.sidecar_operations import read_sidecar_metadata

    with tempfile.TemporaryDirectory() as temp_dir:
        doc_path = Path(temp_dir) / "nonexistent.md"

        result = read_sidecar_metadata(doc_path)
        assert result is None


def test_read_sidecar_metadata_corrupted_json():
    """Test reading sidecar metadata with corrupted JSON."""
    from mcp_server_guide.utils.sidecar_operations import read_sidecar_metadata

    with tempfile.TemporaryDirectory() as temp_dir:
        doc_path = Path(temp_dir) / "test.md"
        sidecar_path = Path(temp_dir) / "test.md_.json"

        # Create corrupted JSON file
        with open(sidecar_path, "w") as f:
            f.write("{ invalid json")

        result = read_sidecar_metadata(doc_path)
        assert result is None


def test_read_sidecar_metadata_permission_error():
    """Test reading sidecar metadata with permission errors."""
    from mcp_server_guide.utils.sidecar_operations import read_sidecar_metadata

    with tempfile.TemporaryDirectory() as temp_dir:
        doc_path = Path(temp_dir) / "test.md"
        sidecar_path = Path(temp_dir) / "test.md_.json"

        # Create valid JSON file
        with open(sidecar_path, "w") as f:
            json.dump({"source_type": "manual", "content_hash": "sha256:abc", "mime_type": "text/markdown"}, f)

        # Remove read permissions
        os.chmod(sidecar_path, 0o000)

        try:
            result = read_sidecar_metadata(doc_path)
            assert result is None
        finally:
            # Restore permissions for cleanup
            os.chmod(sidecar_path, 0o644)
