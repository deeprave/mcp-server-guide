"""Tests for ProjectConfig validation and ProjectConfigManager functionality."""

import tempfile
import yaml
from pathlib import Path
import pytest
from mcp_server_guide.project_config import ProjectConfigManager, ProjectConfig, Category


async def test_project_config_manager_save_config_corrupted_file(monkeypatch):
    """Test ProjectConfigManager.save_config with corrupted existing file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"

        # Create corrupted YAML file
        config_file.write_text("invalid: yaml: content: [")

        manager = ProjectConfigManager()
        # Set the config path to use our temp file
        manager.set_config_filename(config_file)

        config = ProjectConfig(docroot="/test/path", categories={})

        # Should handle corrupted file and create new one
        manager.save_config("test-project", config)

        # Verify file was recreated with valid content (now in YAML format)
        data = yaml.safe_load(config_file.read_text())
        assert "projects" in data
        assert "test-project" in data["projects"]


async def test_project_config_to_dict_excludes_empty():
    """Test ProjectConfig.to_dict excludes None and empty values."""
    config = ProjectConfig(
        docroot=None,  # Should be excluded
        categories={},  # Should be excluded if empty
    )

    data = config.to_dict()
    assert "docroot" not in data  # None values excluded
    assert "categories" not in data  # Empty dicts excluded


async def test_project_config_manager_load_config_default():
    """Test ProjectConfigManager.load_config returns default when no file exists."""
    with tempfile.TemporaryDirectory():
        manager = ProjectConfigManager()

        # Should return None when no config file exists
        config = manager.load_config("nonexistent-project")

        assert config is None


async def test_project_config_manager_load_config_with_projects(monkeypatch):
    """Test ProjectConfigManager.load_config with projects structure."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"

        # Create config with projects structure
        config_data = {"projects": {"test-project": {"docroot": "/test/path", "categories": {}}}}
        config_file.write_text(yaml.dump(config_data))

        manager = ProjectConfigManager()
        # Set the config path to use our temp file
        manager.set_config_filename(config_file)

        config = manager.load_config("test-project")

        assert config is not None
        assert config.docroot == "/test/path"


async def test_project_config_manager_load_config_nonexistent():
    """Test ProjectConfigManager.load_config with nonexistent project."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_file = Path(temp_dir) / "config.yaml"

        # Create config with projects structure but different project
        config_data = {"projects": {"other-project": {"docroot": "/other/path", "categories": {}}}}
        config_file.write_text(yaml.dump(config_data))

        manager = ProjectConfigManager()
        # Set the config path to use our temp file
        manager.set_config_filename(config_file)

        config = manager.load_config("test-project")
        assert config is None


# Validation tests for ProjectConfig


async def test_docroot_with_path_traversal_rejected():
    """Test that docroot with path traversal (..) is rejected."""
    with pytest.raises(ValueError, match="path traversal"):
        ProjectConfig(docroot="../etc/passwd", categories={})


async def test_docroot_empty_string_becomes_none():
    """Test that empty docroot string is normalized to None."""
    config = ProjectConfig(docroot="   ", categories={})
    assert config.docroot is None


async def test_categories_non_dict_rejected():
    """Test that non-dict categories value is rejected."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
        ProjectConfig(docroot=None, categories="not a dict")


async def test_category_name_starting_with_number_rejected():
    """Test that category name starting with number is rejected."""
    with pytest.raises(ValueError, match="must start with a letter"):
        ProjectConfig(docroot=None, categories={"1invalid": Category(dir="test/", patterns=["*.md"])})


async def test_category_name_with_special_chars_rejected():
    """Test that category name with invalid special characters is rejected."""
    with pytest.raises(ValueError, match="alphanumeric"):
        ProjectConfig(docroot=None, categories={"invalid@name": Category(dir="test/", patterns=["*.md"])})


async def test_category_name_exceeding_length_rejected():
    """Test that category name exceeding 30 characters is rejected."""
    long_name = "a" * 31
    with pytest.raises(ValueError, match="cannot exceed 30 characters"):
        ProjectConfig(docroot=None, categories={long_name: Category(dir="test/", patterns=["*.md"])})
