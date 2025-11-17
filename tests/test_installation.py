"""Tests for shared installation module."""

import pytest
from pathlib import Path
import tempfile
import yaml

from mcp_server_guide.installation import create_default_config
from mcp_server_guide.utils.installation_utils import copy_templates, get_templates_dir


class TestTemplateDiscovery:
    """Test template directory discovery logic."""

    def test_get_templates_dir_finds_package_templates(self):
        """Should find templates directory from package location."""
        templates_dir = get_templates_dir()

        assert templates_dir.exists()
        assert templates_dir.is_dir()
        assert templates_dir.name == "templates"

        # Should contain expected template directories
        expected_dirs = {"guide", "lang", "context", "prompt"}
        actual_dirs = {d.name for d in templates_dir.iterdir() if d.is_dir()}
        assert expected_dirs.issubset(actual_dirs)


class TestTemplateCopying:
    """Test silent template copying logic."""

    @pytest.mark.asyncio
    async def test_copy_templates_silent_copies_without_prompts(self):
        """Should copy templates silently without user interaction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            dest_dir = Path(temp_dir) / "dest"

            # Create test source structure
            source_dir.mkdir()
            (source_dir / "guide").mkdir()
            (source_dir / "guide" / "test.md").write_text("# Test Guide")
            (source_dir / "lang").mkdir()
            (source_dir / "lang" / "python.md").write_text("# Python Guide")

            # Copy templates silently
            await copy_templates(source_dir, dest_dir)

            # Verify structure copied
            assert dest_dir.exists()
            assert (dest_dir / "guide").exists()
            assert (dest_dir / "guide" / "test.md").exists()
            assert (dest_dir / "lang").exists()
            assert (dest_dir / "lang" / "python.md").exists()

            # Verify content copied
            assert (dest_dir / "guide" / "test.md").read_text() == "# Test Guide"
            assert (dest_dir / "lang" / "python.md").read_text() == "# Python Guide"

    @pytest.mark.asyncio
    async def test_copy_templates_silent_raises_when_source_not_found(self):
        """Should raise FileNotFoundError when source doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "nonexistent"
            dest_dir = Path(temp_dir) / "dest"

            with pytest.raises(FileNotFoundError, match="Source templates directory not found"):
                await copy_templates(source_dir, dest_dir)


class TestConfigCreation:
    """Test silent config creation logic."""

    @pytest.mark.asyncio
    async def test_create_default_config_creates_config_silently(self):
        """Should create default config file silently without prompts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            docroot = Path(temp_dir) / "docs"

            # Create config silently
            await create_default_config(config_path, docroot)

            # Verify config file created
            assert config_path.exists()

            # Verify config content
            with open(config_path) as f:
                config_data = yaml.safe_load(f)

            assert config_data is not None
            assert "docroot" in config_data
            assert config_data["docroot"] == str(docroot.resolve())

    @pytest.mark.asyncio
    async def test_create_default_config_creates_parent_directories(self):
        """Should create parent directories for config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "nested" / "config.yaml"
            docroot = Path(temp_dir) / "docs"

            # Create config silently
            await create_default_config(config_path, docroot)

            # Verify parent directories created
            assert config_path.parent.exists()
            assert config_path.exists()
