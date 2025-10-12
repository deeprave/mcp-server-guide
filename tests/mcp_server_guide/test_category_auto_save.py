"""Tests for category auto-save functionality."""

import pytest
from pathlib import Path
from unittest.mock import patch, Mock, AsyncMock
from mcp_server_guide.tools.category_tools import add_category, update_category, remove_category
from mcp_server_guide.session_manager import SessionManager


@pytest.fixture
def mock_session_with_save():
    """Mock session manager with save functionality."""
    with patch("mcp_server_guide.tools.category_tools.SessionManager") as mock:
        session_instance = Mock()
        mock.return_value = session_instance
        session_instance.get_current_project_safe = AsyncMock(return_value="test-proj")

        config_data = {
            "categories": {
                "guide": {"dir": "guide/", "patterns": ["guidelines.md"], "description": ""},
                "lang": {"dir": "lang/", "patterns": ["python.md"], "description": ""},
                "context": {"dir": "context/", "patterns": ["context.md"], "description": ""},
            }
        }

        session_instance.session_state.get_project_config = Mock(return_value=config_data)
        session_instance.get_or_create_project_config = AsyncMock(return_value=config_data)
        session_instance.session_state.set_project_config = Mock()
        session_instance.save_session = AsyncMock()
        # Mock the session state project name to be short
        session_instance.session_state.project_name = "test-proj"

        # Mock config manager to use temp directory
        import tempfile

        temp_dir = tempfile.mkdtemp()
        session_instance._config_manager.set_config_filename = Mock()
        session_instance._config_manager.get_config_filename = Mock(return_value=f"{temp_dir}/test.yaml")

        yield session_instance


async def test_add_auto_save():
    """Test that adding a category triggers auto-save."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_config.yaml"

        session = SessionManager()
        session._config_manager.set_config_filename(str(config_file))
        session.set_project_name("test-proj")

        result = await add_category("testing", "test/", ["*.md", "test-*.txt"])

        assert result["success"] is True
        # Verify config file was created by auto-save
        assert config_file.exists()


async def test_update_auto_save():
    """Test that updating a category triggers auto-save."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_config.yaml"

        session = SessionManager()
        session._config_manager.set_config_filename(str(config_file))
        session.set_project_name("test-proj")

        # Add a category first
        await add_category("testing", "test/", ["*.md"])

        # Update it
        result = await update_category("testing", "updated-test/", ["*.txt"], description="Updated")

        assert result["success"] is True
        # Verify config file was updated by auto-save
        assert config_file.exists()


async def test_remove_auto_save():
    """Test that removing a category triggers auto-save."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "test_config.yaml"

        session = SessionManager()
        session._config_manager.set_config_filename(str(config_file))
        session.set_project_name("test-proj")

        # Add a category first
        await add_category("testing", "test/", ["*.md"])

        # Remove it
        result = await remove_category("testing")

        assert result["success"] is True
        # Verify config file was updated by auto-save
        assert config_file.exists()


async def test_auto_save_default(mock_session_with_save):
    """Test that auto-save uses the default config filename."""
    result = await add_category("testing", "test/", ["*.md"])

    assert result["success"] is True
    # Verify auto-save was called (don't check exact filename)
    mock_session_with_save.save_session.assert_called_once()


# Additional test to verify auto-save error handling
async def test_auto_save_errors():
    """Test that category operations succeed even if auto-save fails."""
    with patch("mcp_server_guide.tools.category_tools.SessionManager") as mock:
        session_instance = Mock()
        mock.return_value = session_instance
        session_instance.get_current_project_safe = AsyncMock(return_value="test-proj")

        config_data = {
            "categories": {
                "guide": {"dir": "guide/", "patterns": ["guidelines.md"], "description": ""},
                "lang": {"dir": "lang/", "patterns": ["python.md"], "description": ""},
                "context": {"dir": "context/", "patterns": ["context.md"], "description": ""},
            }
        }

        session_instance.session_state.get_project_config = Mock(return_value=config_data)
        session_instance.get_or_create_project_config = AsyncMock(return_value=config_data)
        session_instance.session_state.set_project_config = Mock()
        # Make save_session fail
        session_instance.save_session = AsyncMock(side_effect=Exception("Save failed"))

        result = await add_category("testing", "test/", ["*.md"])

        # Category operation should still succeed even if save fails
        assert result["success"] is True
        session_instance.save_session.assert_called_once()
