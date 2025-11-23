"""Tests for refactored mcp_install.py script."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from src.mcp_install import copy_templates_with_interaction, create_or_update_config, main


class TestMcpInstallRefactored:
    """Test refactored mcp_install.py functionality."""

    @pytest.mark.asyncio
    async def test_main_uses_shared_installation_module(self):
        """Should use shared installation module for template discovery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            install_path = str(Path(temp_dir) / "install")
            config_path = str(Path(temp_dir) / "config.yaml")

            # Mock the shared module functions
            with (
                patch("src.mcp_install.get_templates_dir") as mock_get_templates,
                patch("src.mcp_install.copy_templates_with_interaction") as mock_copy,
                patch("src.mcp_install.create_or_update_config") as mock_config,
            ):
                # Setup mocks
                mock_templates_dir = Path(temp_dir) / "templates"
                mock_templates_dir.mkdir()
                mock_get_templates.return_value = mock_templates_dir

                mock_config.return_value = (Path(install_path), Path(config_path))

                # Run main with yes=True to avoid prompts
                await main(install_path=install_path, config_path=config_path, verbose=False, yes=True)

                # Verify shared module was used
                mock_get_templates.assert_called_once()
                mock_copy.assert_called_once()
                mock_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_copy_templates_with_interaction_handles_user_prompts(self):
        """Should handle user interaction for template copying."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            dest_dir = Path(temp_dir) / "dest"

            # Create test source structure
            source_dir.mkdir()
            (source_dir / "test.md").write_text("# Test")

            # Create existing destination with files
            dest_dir.mkdir()
            (dest_dir / "existing.md").write_text("# Existing")

            # Mock click.confirm to return True (proceed with update)
            with patch("src.mcp_install.click.confirm", return_value=True), patch("src.mcp_install.click.echo"):
                await copy_templates_with_interaction(source_dir, dest_dir, verbose=False)

                # Verify files were copied
                assert (dest_dir / "test.md").exists()
                assert (dest_dir / "test.md").read_text() == "# Test"

    @pytest.mark.asyncio
    async def test_create_or_update_config_preserves_existing_config(self):
        """Should preserve existing configuration when updating."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            docroot = Path(temp_dir) / "docs"

            # Create existing config
            config_path.write_text("existing_key: existing_value\ndocroot: /old/path")

            # Call without install_path (should preserve existing docroot)
            result_docroot, result_config = await create_or_update_config(
                docroot, config_path=str(config_path), install_path=None
            )

            # Verify config was updated but existing docroot preserved (mcp_install.py behavior)
            assert result_config == config_path
            assert result_docroot == Path("/old/path")  # Should use existing docroot

            # Check config content
            import yaml

            with open(config_path) as f:
                config_data = yaml.safe_load(f)

            assert config_data["existing_key"] == "existing_value"
            assert config_data["docroot"] == "/old/path"  # Should preserve existing

    @pytest.mark.asyncio
    async def test_main_maintains_cli_functionality(self):
        """Should maintain all existing CLI functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            install_path = str(Path(temp_dir) / "install")
            config_path = str(Path(temp_dir) / "config.yaml")

            # Mock all external dependencies
            with (
                patch("src.mcp_install.get_templates_dir") as mock_get_templates,
                patch("src.mcp_install.copy_templates_with_interaction") as mock_copy,
                patch("src.mcp_install.create_or_update_config") as mock_config,
                patch("src.mcp_install.prompt_install_location") as mock_prompt,
                patch("src.mcp_install.click.confirm", return_value=True),
                patch("src.mcp_install.click.echo"),
            ):
                # Setup mocks
                mock_templates_dir = Path(temp_dir) / "templates"
                mock_templates_dir.mkdir()
                mock_get_templates.return_value = mock_templates_dir
                mock_config.return_value = (Path(install_path), Path(config_path))
                mock_prompt.return_value = Path(install_path)

                # Test with all CLI options
                await main(
                    install_path=install_path,
                    config_path=config_path,
                    verbose=True,
                    yes=False,  # Should still prompt for confirmation
                )

                # Verify all functionality was called
                mock_get_templates.assert_called_once()
                mock_config.assert_called_once()
                mock_prompt.assert_called_once()
                mock_copy.assert_called_once()
