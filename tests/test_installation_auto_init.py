"""Tests for auto_initialize_new_installation function."""

import pytest
from pathlib import Path
import tempfile
from unittest.mock import patch

from mcp_server_guide.installation import auto_initialize_new_installation


class TestAutoInitializeNewInstallation:
    """Test auto initialization of new installations."""

    @pytest.mark.asyncio
    @patch("mcp_server_guide.installation.get_templates_dir")
    @patch("mcp_server_guide.installation.copy_templates")
    @patch("mcp_server_guide.installation.create_default_config")
    @patch("mcp_server_guide.installation.get_default_docroot")
    @patch("pathlib.Path.mkdir")
    async def test_production_environment_uses_global_default(
        self, mock_mkdir, mock_get_default_docroot, mock_create_config, mock_copy_templates, mock_get_templates_dir
    ):
        """Test production environment uses global default docroot."""
        # Setup mocks
        mock_get_default_docroot.return_value = Path("/home/user/.config/mcp-server-guide/docs")
        mock_get_templates_dir.return_value = Path("/templates")
        mock_copy_templates.return_value = None
        mock_create_config.return_value = None
        mock_mkdir.return_value = None

        # Use a production-like path (not /tmp or /var/folders)
        config_file = Path("/home/user/.config/mcp-server-guide/config.yaml")

        await auto_initialize_new_installation(config_file)

        # Verify global default docroot was used
        mock_get_default_docroot.assert_called_once()
        mock_create_config.assert_called_once()

        # Check that the docroot passed to create_default_config is the expanded global default
        call_args = mock_create_config.call_args[0]
        assert call_args[0] == config_file
        assert str(call_args[1]) == "/home/user/.config/mcp-server-guide/docs"

    @pytest.mark.asyncio
    @patch("mcp_server_guide.installation.get_templates_dir")
    @patch("mcp_server_guide.installation.copy_templates")
    @patch("mcp_server_guide.installation.create_default_config")
    @patch("mcp_server_guide.installation.get_default_docroot")
    @patch("pathlib.Path.mkdir")
    async def test_test_environment_uses_relative_path(
        self, mock_mkdir, mock_get_default_docroot, mock_create_config, mock_copy_templates, mock_get_templates_dir
    ):
        """Test test environment uses relative docroot path."""
        # Setup mocks
        mock_get_default_docroot.return_value = Path("/home/user/.config/mcp-server-guide/docs")
        mock_get_templates_dir.return_value = Path("/templates")
        mock_copy_templates.return_value = None
        mock_create_config.return_value = None
        mock_mkdir.return_value = None

        with tempfile.TemporaryDirectory() as temp_dir:
            # Use a test environment path (/tmp)
            config_file = Path(temp_dir) / "config.yaml"

            await auto_initialize_new_installation(config_file)

            # Verify relative docroot was used
            mock_create_config.assert_called_once()

            # Check that the docroot passed is relative to config file
            call_args = mock_create_config.call_args[0]
            assert call_args[0] == config_file
            assert call_args[1] == config_file.parent / "docs"

    @pytest.mark.asyncio
    @patch("mcp_server_guide.installation.get_templates_dir")
    @patch("mcp_server_guide.installation.copy_templates")
    @patch("mcp_server_guide.installation.create_default_config")
    @patch("mcp_server_guide.installation.get_default_docroot")
    @patch("pathlib.Path.mkdir")
    async def test_var_folders_path_uses_relative_docroot(
        self, mock_mkdir, mock_get_default_docroot, mock_create_config, mock_copy_templates, mock_get_templates_dir
    ):
        """Test /var/folders path (macOS temp) uses relative docroot."""
        # Setup mocks
        mock_get_default_docroot.return_value = Path("/home/user/.config/mcp-server-guide/docs")
        mock_get_templates_dir.return_value = Path("/templates")
        mock_copy_templates.return_value = None
        mock_create_config.return_value = None
        mock_mkdir.return_value = None

        # Use a /var/folders path (macOS temporary directory pattern)
        config_file = Path("/var/folders/abc123/config.yaml")

        await auto_initialize_new_installation(config_file)

        # Verify relative docroot was used for /var/folders path
        mock_create_config.assert_called_once()

        # Check that the docroot passed is relative to config file
        call_args = mock_create_config.call_args[0]
        assert call_args[0] == config_file
        assert call_args[1] == config_file.parent / "docs"
