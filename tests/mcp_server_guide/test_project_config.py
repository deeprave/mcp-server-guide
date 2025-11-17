"""Tests for ProjectConfig validation and ProjectConfigManager functionality."""

import tempfile
import yaml
from pathlib import Path
import pytest
from mcp_server_guide.project_config import ProjectConfigManager, ProjectConfig
from mcp_server_guide.models.category import Category


async def test_project_config_manager_save_config_corrupted_file(monkeypatch):
    """Test ProjectConfigManager.save_config with corrupted existing file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"

        # Create corrupted YAML file
        config_file.write_text("invalid: yaml: content: [")

        manager = ProjectConfigManager()
        # Set the config path to use our temp file
        manager.set_config_filename(config_file)

        config = ProjectConfig(categories={})

        # Should handle corrupted file and create new one
        await manager.save_config("test-project", config)

        # Verify file was recreated with valid content (now in YAML format)
        data = yaml.safe_load(config_file.read_text())
        assert "projects" in data
        assert "test-project" in data["projects"]
        # docroot should be defaulted to proper path
        from mcp_server_guide.models.config_file import get_default_docroot

        expected_docroot = str(get_default_docroot())
        assert data["docroot"] == expected_docroot


async def test_project_config_to_dict_excludes_empty():
    """Test ProjectConfig.to_dict excludes None and empty values."""
    config = ProjectConfig(
        categories={},  # Should be excluded if empty
    )

    data = config.to_dict()
    assert "categories" not in data  # Empty dicts excluded


async def test_project_config_manager_load_config_default():
    """Test ProjectConfigManager.load_config returns default when no file exists."""
    with tempfile.TemporaryDirectory():
        manager = ProjectConfigManager()

        # Should return None when no config file exists
        config = await manager.load_config("nonexistent-project")

        assert config is None


async def test_project_config_manager_load_config_with_projects(monkeypatch):
    """Test ProjectConfigManager.load_config with projects structure."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"

        # Create config with projects structure (docroot is global, not per-project)
        config_data = {"docroot": "/test/path", "projects": {"test-project": {"categories": {}}}}
        config_file.write_text(yaml.dump(config_data))

        manager = ProjectConfigManager()
        # Set the config path to use our temp file
        manager.set_config_filename(config_file)

        config = await manager.load_config("test-project")

        assert config is not None
        # docroot is stored in manager, not in ProjectConfig
        assert str(manager.docroot) == "/test/path"


async def test_project_config_manager_load_config_nonexistent():
    """Test ProjectConfigManager.load_config with nonexistent project."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"

        # Create config with projects structure but different project
        config_data = {"docroot": "/other/path", "projects": {"other-project": {"categories": {}}}}
        config_file.write_text(yaml.dump(config_data))

        manager = ProjectConfigManager()
        # Set the config path to use our temp file
        manager.set_config_filename(config_file)

        config = await manager.load_config("test-project")
        assert config is None


# Validation tests for ProjectConfig


async def test_categories_non_dict_rejected():
    """Test that non-dict categories value is rejected."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
        ProjectConfig(categories="not a dict")


async def test_category_name_starting_with_number_rejected():
    """Test that category name starting with number is rejected."""
    with pytest.raises(ValueError, match="must start with a letter"):
        ProjectConfig(categories={"1invalid": Category(dir="test/", patterns=["*.md"])})


async def test_category_name_with_special_chars_rejected():
    """Test that category name with invalid special characters is rejected."""
    with pytest.raises(ValueError, match="alphanumeric"):
        ProjectConfig(categories={"invalid@name": Category(dir="test/", patterns=["*.md"])})


async def test_category_name_exceeding_length_rejected():
    """Test that category name exceeding 30 characters is rejected."""
    long_name = "a" * 31
    with pytest.raises(ValueError, match="cannot exceed 30 characters"):
        ProjectConfig(categories={long_name: Category(dir="test/", patterns=["*.md"])})
