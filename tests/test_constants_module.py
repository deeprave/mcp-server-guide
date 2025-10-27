"""Test constants module."""

from mcp_server_guide.constants import BUILTIN_CATEGORIES


def test_builtin_categories_defined():
    """Test that builtin categories are defined correctly."""
    assert BUILTIN_CATEGORIES == ["guide", "lang", "context"]
