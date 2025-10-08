"""Tests for category auto-save functionality."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.mcp_server_guide.tools.category_tools import (
    add_category,
    remove_category,
    update_category,
)


@pytest.fixture
def mock_session_with_save():
    """Mock session manager with save functionality."""
    with patch("src.mcp_server_guide.tools.category_tools.SessionManager") as mock:
        session_instance = Mock()
        mock.return_value = session_instance
        session_instance.get_current_project_safe = AsyncMock(return_value="test-project")
        session_instance.session_state.get_project_config = AsyncMock(
            return_value={
                "categories": {
                    "guide": {"dir": "guide/", "patterns": ["guidelines.md"], "description": ""},
                    "lang": {"dir": "lang/", "patterns": ["python.md"], "description": ""},
                    "context": {"dir": "context/", "patterns": ["context.md"], "description": ""},
                }
            }
        )
        session_instance.session_state.set_project_config = AsyncMock()
        session_instance.save_to_file = AsyncMock()
        # Mock the save_to_file method
        session_instance.save_to_file = Mock()
        session_instance.save_to_file = AsyncMock()
        yield session_instance


async def test_add_category_triggers_auto_save(mock_session_with_save):
    """Test that adding a category triggers auto-save."""
    # This test should FAIL initially, demonstrating the missing functionality
    result = await add_category("testing", "test/", ["*.md", "test-*.txt"])

    assert result["success"] is True
    # This assertion should fail because auto-save is not implemented yet
    mock_session_with_save.save_to_file.assert_called_once()


async def test_update_category_triggers_auto_save(mock_session_with_save):
    """Test that updating a category triggers auto-save."""
    # Set up existing custom category
    mock_session_with_save.session_state.get_project_config = AsyncMock(
        return_value={
            "categories": {"custom_test": {"dir": "test/", "patterns": ["*.md"], "description": "Old description"}}
        }
    )

    result = await update_category("custom_test", "test/", ["*.md"], description="Updated description")

    assert result["success"] is True
    # This assertion should fail because auto-save is not implemented yet
    mock_session_with_save.save_to_file.assert_called_once()


async def test_remove_category_triggers_auto_save(mock_session_with_save):
    """Test that removing a category triggers auto-save."""
    # Add a custom category first to the mock config
    mock_session_with_save.session_state.get_project_config = AsyncMock(
        return_value={"categories": {"custom": {"dir": "custom/", "patterns": ["*.md"], "description": ""}}}
    )

    # This test should FAIL initially, demonstrating the missing functionality
    result = await remove_category("custom")

    assert result["success"] is True
    # This assertion should fail because auto-save is not implemented yet
    mock_session_with_save.save_to_file.assert_called_once()


async def test_auto_save_uses_default_config_filename(mock_session_with_save):
    """Test that auto-save uses the default config filename."""
    result = await add_category("testing", "test/", ["*.md"])

    assert result["success"] is True
    # This should fail initially - auto-save should use default filename
    mock_session_with_save.save_to_file.assert_called_once_with(".mcp-server-guide.config.json")


async def test_auto_save_handles_save_errors_gracefully(mock_session_with_save):
    """Test that auto-save errors don't break category operations."""
    # Make save_to_file raise an exception
    mock_session_with_save.save_to_file.side_effect = Exception("Save failed")

    # Category operation should still succeed even if save fails
    result = await add_category("testing", "test/", ["*.md"])

    assert result["success"] is True
    # The operation should complete successfully despite save failure
    assert "testing" in result["category"]["name"]
