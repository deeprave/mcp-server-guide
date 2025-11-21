"""Tests for listing all projects from config file."""

import pytest
from src.mcp_server_guide.project_config import ProjectConfigManager


@pytest.mark.asyncio
async def test_list_all_projects(tmp_path):
    """List all projects from config file."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
projects:
  project1:
    categories: {}
    collections: {}
  project2:
    categories: {}
    collections: {}
  project3:
    categories: {}
    collections: {}
""")

    manager = ProjectConfigManager()
    manager.set_config_filename(config_file)
    result = await manager.list_all_projects()
    assert set(result) == {"project1", "project2", "project3"}


@pytest.mark.asyncio
async def test_list_all_projects_empty_config(tmp_path):
    """List projects when config file is empty."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("projects: {}")

    manager = ProjectConfigManager()
    manager.set_config_filename(config_file)
    result = await manager.list_all_projects()
    assert result == []


@pytest.mark.asyncio
async def test_list_all_projects_no_config_file(tmp_path):
    """List projects when config file doesn't exist."""
    config_file = tmp_path / "nonexistent.yaml"

    manager = ProjectConfigManager()
    manager.set_config_filename(config_file)
    result = await manager.list_all_projects()
    assert result == []
