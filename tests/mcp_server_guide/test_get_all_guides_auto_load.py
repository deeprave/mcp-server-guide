"""Tests for get_all_guides auto_load filtering."""

from unittest.mock import Mock, patch
from mcp_server_guide.tools.content_tools import get_all_guides


async def test_get_all_guides_returns_only_auto_load_true_categories():
    """Test that get_all_guides returns only categories with auto_load: true."""
    with patch("mcp_server_guide.tools.content_tools.SessionManager") as mock_session_class:
        # Set up mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get_current_project.return_value = "test-project"
        mock_session.session_state.get_project_config.return_value = {
            "categories": {
                "guide": {"dir": "guide/", "patterns": ["*.md"], "description": "Guide", "auto_load": True},
                "lang": {"dir": "lang/", "patterns": ["*.md"], "description": "Language"},  # No auto_load = False
                "context": {"dir": "context/", "patterns": ["*.md"], "description": "Context", "auto_load": True},
                "custom": {"dir": "custom/", "patterns": ["*.md"], "description": "Custom", "auto_load": False},
            }
        }

        with patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_get_content:
            mock_get_content.return_value = {"success": True, "content": "Test content"}

            result = await get_all_guides()

            # Should only call get_category_content for categories with auto_load: true
            actual_calls = [call[0] for call in mock_get_content.call_args_list]

            assert len(actual_calls) == 2
            assert ("guide", "test-project") in actual_calls
            assert ("context", "test-project") in actual_calls
            assert ("lang", "test-project") not in actual_calls
            assert ("custom", "test-project") not in actual_calls

            # Should return content for auto_load categories
            assert "guide" in result
            assert "context" in result
            assert "lang" not in result
            assert "custom" not in result


async def test_get_all_guides_returns_empty_dict_when_no_auto_load_true_categories():
    """Test that get_all_guides returns empty dict when no auto_load: true categories."""
    with patch("mcp_server_guide.tools.content_tools.SessionManager") as mock_session_class:
        # Set up mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get_current_project.return_value = "test-project"
        mock_session.session_state.get_project_config.return_value = {
            "categories": {
                "guide": {"dir": "guide/", "patterns": ["*.md"], "description": "Guide"},  # No auto_load = False
                "lang": {"dir": "lang/", "patterns": ["*.md"], "description": "Language"},  # No auto_load = False
            }
        }

        with patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_get_content:
            result = await get_all_guides()

            # Should not call get_category_content for any categories
            mock_get_content.assert_not_called()

            # Should return empty dict
            assert result == {}


async def test_get_all_guides_error_handling_when_category_loading_fails():
    """Test error handling when category loading fails."""
    with patch("mcp_server_guide.tools.content_tools.SessionManager") as mock_session_class:
        # Set up mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get_current_project.return_value = "test-project"
        mock_session.session_state.get_project_config.return_value = {
            "categories": {
                "guide": {"dir": "guide/", "patterns": ["*.md"], "description": "Guide", "auto_load": True},
                "context": {"dir": "context/", "patterns": ["*.md"], "description": "Context", "auto_load": True},
            }
        }

        with patch("mcp_server_guide.tools.content_tools.get_category_content") as mock_get_content:
            # Make guide succeed and context fail
            def side_effect(category, project):
                if category == "guide":
                    return {"success": True, "content": "Guide content"}
                elif category == "context":
                    raise Exception("Failed to load context")

            mock_get_content.side_effect = side_effect

            result = await get_all_guides()

            # Should have guide content and error for context
            assert "guide" in result
            assert result["guide"] == "Guide content"
            assert "context" in result
            assert "Error:" in result["context"]
