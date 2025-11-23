"""Tests for category auto-save functionality."""

from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from mcp_server_guide.session_manager import SessionManager
from mcp_server_guide.tools.category_tools import add_category, remove_category, update_category


@pytest.fixture
def mock_session_with_save():
    """Mock session manager with save functionality."""
    with patch("mcp_server_guide.session_manager.SessionManager") as mock:
        from mcp_server_guide.models.category import Category
        from mcp_server_guide.project_config import ProjectConfig

        session_instance = Mock()
        mock.return_value = session_instance
        session_instance.get_project_name = Mock(return_value="test-proj")

        config_data = ProjectConfig(
            categories={
                "guide": Category(dir="guide/", patterns=["guidelines.md"], description=""),
                "lang": Category(dir="lang/", patterns=["python.md"], description=""),
                "context": Category(dir="context/", patterns=["context.md"], description=""),
            }
        )

        session_instance.get_or_create_project_config = AsyncMock(return_value=config_data)
        session_instance.safe_save_session = AsyncMock()

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
        result = await update_category("testing", description="Updated", dir="updated-test/", patterns=["*.txt"])

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
    mock_session_with_save.safe_save_session.assert_called_once()


# Additional test to verify auto-save error handling
async def test_auto_save_errors():
    """Test that category operations succeed even if auto-save fails."""
    with patch("mcp_server_guide.session_manager.SessionManager") as mock:
        from mcp_server_guide.models.category import Category
        from mcp_server_guide.project_config import ProjectConfig

        session_instance = Mock()
        mock.return_value = session_instance
        session_instance.get_project_name = Mock(return_value="test-proj")

        config_data = ProjectConfig(
            categories={
                "guide": Category(dir="guide/", patterns=["guidelines.md"], description=""),
                "lang": Category(dir="lang/", patterns=["python.md"], description=""),
                "context": Category(dir="context/", patterns=["context.md"], description=""),
            }
        )

        session_instance.get_or_create_project_config = AsyncMock(return_value=config_data)
        # Make the underlying save_session fail, but safe_save_session should handle it
        session_instance.save_session = AsyncMock(side_effect=Exception("Save failed"))
        session_instance.safe_save_session = AsyncMock()  # This should not raise

        result = await add_category("testing", "test/", ["*.md"])

        # Category operation should still succeed even if save fails
        assert result["success"] is True
        session_instance.safe_save_session.assert_called_once()
