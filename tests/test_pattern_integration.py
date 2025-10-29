"""Tests for pattern integration with document management."""

import tempfile
from pathlib import Path
from mcp_server_guide.tools.category_tools import _safe_glob_search
from mcp_server_guide.constants import METADATA_SUFFIX, DOCUMENT_SUBDIR
from mcp_server_guide.services.document_discovery import get_category_documents_by_path


def test_safe_glob_search_excludes_metadata_files():
    """Test that _safe_glob_search excludes metadata files from pattern matching."""
    with tempfile.TemporaryDirectory() as temp_dir:
        search_dir = Path(temp_dir)

        # Create regular document files
        (search_dir / "document1.md").write_text("# Document 1")
        (search_dir / "document2.txt").write_text("Document 2 content")

        # Create metadata files that should be excluded
        (search_dir / f"document1.md{METADATA_SUFFIX}").write_text('{"source_type": "manual"}')
        (search_dir / f"document2.txt{METADATA_SUFFIX}").write_text('{"source_type": "manual"}')

        # Search with patterns that would match both
        patterns = ["*.md", "*.txt", "*.json"]
        matched_files = _safe_glob_search(search_dir, patterns)

        # Should only find the document files, not metadata files
        matched_names = [f.name for f in matched_files]
        assert "document1.md" in matched_names
        assert "document2.txt" in matched_names
        assert f"document1.md{METADATA_SUFFIX}" not in matched_names
        assert f"document2.txt{METADATA_SUFFIX}" not in matched_names


def test_managed_documents_take_precedence_over_pattern_files():
    """Test that managed documents take precedence over pattern files in deduplication."""
    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)
        docs_dir = category_dir / DOCUMENT_SUBDIR
        docs_dir.mkdir()

        # Create a pattern file
        (category_dir / "readme.md").write_text("# Pattern File Content")

        # Create a managed document with the same name
        (docs_dir / "readme.md").write_text("# Managed Document Content")
        (docs_dir / f"readme.md{METADATA_SUFFIX}").write_text('{"source_type": "manual", "content_hash": "sha256:abc", "mime_type": "text/markdown"}')

        # Get pattern files
        pattern_files = _safe_glob_search(category_dir, ["*.md"])

        # Get managed documents
        managed_docs = get_category_documents_by_path(category_dir)

        # Both should find their respective files
        pattern_names = [f.name for f in pattern_files]
        managed_names = [doc.path.name for doc in managed_docs]

        assert "readme.md" in pattern_names
        assert "readme.md" in managed_names

def test_get_combined_category_content_deduplication():
    """Test that get_category_content properly deduplicates managed vs pattern files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        category_dir = Path(temp_dir)
        docs_dir = category_dir / DOCUMENT_SUBDIR
        docs_dir.mkdir()

        # Create a pattern file
        (category_dir / "readme.md").write_text("# Pattern File Content")

        # Create a managed document with the same name (should take precedence)
        (docs_dir / "readme.md").write_text("# Managed Document Content")
        (docs_dir / f"readme.md{METADATA_SUFFIX}").write_text('{"source_type": "manual", "content_hash": "sha256:abc", "mime_type": "text/markdown"}')

        # Create a unique pattern file
        (category_dir / "unique_pattern.md").write_text("# Unique Pattern Content")

        # Create a unique managed document
        (docs_dir / "unique_managed.md").write_text("# Unique Managed Content")
        (docs_dir / f"unique_managed.md{METADATA_SUFFIX}").write_text('{"source_type": "manual", "content_hash": "sha256:def", "mime_type": "text/markdown"}')

        # This should be implemented in the GREEN phase
        from mcp_server_guide.tools.category_tools import _get_combined_category_files

        combined_files = _get_combined_category_files(category_dir, ["*.md"])

        # Should have 3 files: managed readme.md (not pattern), unique_pattern.md, unique_managed.md
        file_names = [f.name for f in combined_files]
        assert len(file_names) == 3
        assert "readme.md" in file_names
        assert "unique_pattern.md" in file_names
        assert "unique_managed.md" in file_names

        # The readme.md should be from the managed documents directory
        readme_file = next(f for f in combined_files if f.name == "readme.md")
        assert DOCUMENT_SUBDIR in str(readme_file)  # Should be from __docs__ directory
