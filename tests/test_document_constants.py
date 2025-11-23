"""Tests for document management constants."""


def test_metadata_suffix_constant_exists():
    """Test that METADATA_SUFFIX constant exists and has correct value."""
    from mcp_server_guide.constants import METADATA_SUFFIX

    assert METADATA_SUFFIX == "_.json"


def test_document_subdir_constant_exists():
    """Test that DOCUMENT_SUBDIR constant exists and has correct value."""
    from mcp_server_guide.constants import DOCUMENT_SUBDIR

    assert DOCUMENT_SUBDIR == "__docs__"


def test_constants_are_strings():
    """Test that both constants are strings."""
    from mcp_server_guide.constants import DOCUMENT_SUBDIR, METADATA_SUFFIX

    assert isinstance(METADATA_SUFFIX, str)
    assert isinstance(DOCUMENT_SUBDIR, str)
