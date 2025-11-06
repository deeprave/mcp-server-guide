"""Tests for get_or_create_project_config functionality."""

import pytest
from unittest.mock import Mock, patch
from mcp_server_guide.tools.category_tools import list_categories


async def test_get_or_create_project_config_exception_handling():
    """Test that exceptions from get_or_create_project_config are properly handled."""

    with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        async def mock_get_config(project=None):
            raise Exception("Config creation failed")

        mock_session.get_or_create_project_config = mock_get_config

        with pytest.raises(Exception, match="Config creation failed"):
            await list_categories()


async def test_get_or_create_project_config_empty_config():
    """Test that empty config is handled correctly."""
    from mcp_server_guide.project_config import ProjectConfig

    with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get_project_name = Mock(return_value="test-project")
        mock_session.get_current_project_safe = Mock(return_value="test-project")

        async def mock_get_config(project=None):
            return ProjectConfig(categories={})

        mock_session.get_or_create_project_config = mock_get_config

        result = await list_categories()

        assert result["success"] is True
        assert result["categories"] == {}


async def test_get_or_create_project_config_no_categories_key():
    """Test that config without categories key is handled correctly."""
    from mcp_server_guide.project_config import ProjectConfig

    with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        mock_session.get_project_name = Mock(return_value="test-project")
        mock_session.get_current_project_safe = Mock(return_value="test-project")

        async def mock_get_config(project=None):
            return ProjectConfig(categories={})

        mock_session.get_or_create_project_config = mock_get_config

        result = await list_categories()

        assert result["success"] is True
        assert result["categories"] == {}


async def test_get_or_create_project_config_auto_save_behavior():
    """Test that save_to_file is called when a new project is created."""
    import tempfile
    from unittest.mock import patch, Mock
    from mcp_server_guide.project_config import ProjectConfig

    with tempfile.TemporaryDirectory():
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_session_class:
            mock_session = Mock()
            mock_session.get_project_name = Mock(return_value="new-project")
            mock_session.get_current_project_safe = Mock(return_value="new-project")

            async def mock_get_config(project=None):
                return ProjectConfig(categories={})

            mock_session.get_or_create_project_config = mock_get_config

            async def mock_save():
                pass

            mock_session.save_session = mock_save

            mock_session_class.return_value = mock_session

            result = await list_categories()

            assert result["success"] is True
            assert result["categories"] == {}
