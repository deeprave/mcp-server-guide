"""Tests for unified content resolution system (Phase 2)."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from mcp_server_guide.tools.content_tools import (
    get_guide,
    get_language_guide,
    get_project_context,
    get_all_guides,
)


@pytest.fixture
def mock_category_content():
    """Mock get_category_content function."""
    with patch("mcp_server_guide.tools.content_tools.get_category_content") as mock:
        yield mock


async def test_get_guide_uses_category_system(mock_category_content):
    """Test that await get_guide() uses unified category system instead of server calls."""
    # Setup mock response
    mock_category_content.return_value = {"success": True, "content": "# Development Guidelines\n\nTDD approach..."}

    # Call function
    result = await get_guide("test-project")

    # Verify it uses category system
    mock_category_content.assert_called_once_with("guide", "test-project")
    assert result == "# Development Guidelines\n\nTDD approach..."


async def test_get_language_guide_uses_category_system(mock_category_content):
    """Test that await get_language_guide() uses unified category system."""
    mock_category_content.return_value = {"success": True, "content": "# Python Guidelines\n\nUse ruff format..."}

    result = await get_language_guide("test-project")

    mock_category_content.assert_called_once_with("lang", "test-project")
    assert result == "# Python Guidelines\n\nUse ruff format..."


async def test_get_project_context_uses_category_system(mock_category_content):
    """Test that await get_project_context() uses unified category system."""
    mock_category_content.return_value = {"success": True, "content": "# Project Context\n\nThis is a test project..."}

    result = await get_project_context("test-project")

    mock_category_content.assert_called_once_with("context", "test-project")
    assert result == "# Project Context\n\nThis is a test project..."


async def test_content_functions_handle_category_errors(mock_category_content):
    """Test that content functions handle category system errors gracefully."""
    mock_category_content.return_value = {"success": False, "error": "Category not found"}

    # All functions should return empty string on error
    assert await get_guide("test-project") == ""
    assert await get_language_guide("test-project") == ""
    assert await get_project_context("test-project") == ""


async def test_content_functions_use_current_project_when_none_provided(mock_category_content):
    """Test that content functions use current project when project=None."""
    mock_category_content.return_value = {"success": True, "content": "test content"}

    # Mock SessionManager to return current project
    with patch("mcp_server_guide.tools.content_tools.SessionManager") as mock_session:
        session_instance = Mock()
        mock_session.return_value = session_instance
        session_instance.get_current_project_safe = AsyncMock(return_value="current-project")

        await get_guide(None)

        # Should use current project
        mock_category_content.assert_called_once_with("guide", None)


async def test_get_all_guides_uses_unified_system():
    """Test that await get_all_guides() uses unified category system with auto_load."""
    from mcp_server_guide.project_config import ProjectConfig, Category

    with patch("mcp_server_guide.tools.content_tools.SessionManager") as mock_session_class:
        # Set up mock session with auto_load categories
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get_current_project_safe = AsyncMock(return_value="test-project")
        mock_session.get_project_name.return_value = "test-project"
        config_data = ProjectConfig(
            categories={
                "guide": Category(dir="guide/", patterns=["*.md"], description="Guide"),
                "lang": Category(dir="lang/", patterns=["*.md"], description="Language"),
                "context": Category(dir="context/", patterns=["*.md"], description="Context"),
            }
        )
        mock_session.get_or_create_project_config = AsyncMock(return_value=config_data)

        with patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_category_content:
            # Mock responses for each category
            def mock_category_response(category, project):
                content_map = {
                    "guide": "# Guidelines content",
                    "lang": "# Language content",
                    "context": "# Context content",
                }
                return {"success": True, "content": content_map.get(category, "")}

            mock_category_content.side_effect = mock_category_response

            result = await get_all_guides("test-project")

            # Should call get_category_content for each auto_load category
            assert mock_category_content.call_count == 3

            # Should return dict with all content
            assert "guide" in result
            assert "lang" in result
            assert "context" in result
            assert result["guide"] == "# Guidelines content"
            assert result["lang"] == "# Language content"
            assert result["context"] == "# Context content"
