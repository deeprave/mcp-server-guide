"""Tests for content tools functionality."""

from unittest.mock import patch
from mcp_server_guide.tools.content_tools import (
    get_guide,
    get_language_guide,
    get_project_context,
    get_all_guides,
    search_content,
    show_guide,
    show_language_guide,
    show_project_summary,
)


def test_content_tools_basic():
    """Test basic content tools functionality."""
    # Test that functions return expected types
    result = get_guide()
    assert isinstance(result, str)

    result = get_language_guide()
    assert isinstance(result, str)

    result = get_project_context()
    assert isinstance(result, str)

    result = get_all_guides()
    assert isinstance(result, dict)

    result = search_content("test")
    assert isinstance(result, list)

    result = show_guide()
    assert isinstance(result, dict)

    result = show_language_guide()
    assert isinstance(result, dict)

    result = show_project_summary()
    assert isinstance(result, dict)


def test_get_project_context_variations():
    """Test get_project_context with different path types."""
    # Test with project parameter
    result = get_project_context("test_project")
    assert isinstance(result, str)

    # Test without project parameter
    result = get_project_context()
    assert isinstance(result, str)


def test_content_tools_comprehensive():
    """Test content tools comprehensive functionality."""
    # Test all functions return expected types
    result = get_guide("test_project")
    assert isinstance(result, str)

    result = get_language_guide("test_project")
    assert isinstance(result, str)

    result = get_project_context("test_project")
    assert isinstance(result, str)

    result = get_all_guides("test_project")
    assert isinstance(result, dict)

    result = search_content("test", "test_project")
    assert isinstance(result, list)

    # Test show functions
    result = show_guide("test_project")
    assert isinstance(result, dict)

    result = show_language_guide("test_project")
    assert isinstance(result, dict)

    result = show_project_summary("test_project")
    assert isinstance(result, dict)


def test_get_project_context_branches():
    """Test get_project_context different branches."""
    # Test with different project names to hit different branches
    result1 = get_project_context("test_project")
    assert isinstance(result1, str)

    result2 = get_project_context("another_project")
    assert isinstance(result2, str)

    result3 = get_project_context()
    assert isinstance(result3, str)


def test_get_all_guides_error_handling():
    """Test get_all_guides error handling branches."""
    # Call with different projects to potentially hit error branches
    result1 = get_all_guides("test_project")
    assert isinstance(result1, dict)

    result2 = get_all_guides("nonexistent_project")
    assert isinstance(result2, dict)

    result3 = get_all_guides()
    assert isinstance(result3, dict)

    # Verify all expected keys are present
    expected_keys = ["guide", "language_guide", "project_context"]
    for key in expected_keys:
        assert key in result1 or key in result2 or key in result3


def test_content_tools_edge_cases():
    """Test content tools with edge case inputs."""
    # Test with empty strings and special characters
    result = get_project_context("")
    assert isinstance(result, str)

    result = get_all_guides("")
    assert isinstance(result, dict)

    result = search_content("", "")
    assert isinstance(result, list)

    # Test with None values
    result = get_project_context(None)
    assert isinstance(result, str)

    result = get_all_guides(None)
    assert isinstance(result, dict)


def test_get_all_guides_individual_errors():
    """Test get_all_guides with individual function errors."""
    # Force errors in individual functions to hit exception branches
    with patch("mcp_server_guide.tools.content_tools.get_guide") as mock_guide:
        mock_guide.side_effect = Exception("Guide failed")
        result = get_all_guides("test")
        assert "Error: Guide failed" in result.get("guide", "")

    with patch("mcp_server_guide.tools.content_tools.get_language_guide") as mock_lang:
        mock_lang.side_effect = Exception("Language failed")
        result = get_all_guides("test")
        assert "Error: Language failed" in result.get("language_guide", "")

    with patch("mcp_server_guide.tools.content_tools.get_project_context") as mock_context:
        mock_context.side_effect = Exception("Context failed")
        result = get_all_guides("test")
        assert "Error: Context failed" in result.get("project_context", "")
