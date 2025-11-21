"""Tests for config formatting functions."""

import pytest
from unittest.mock import patch
from src.mcp_server_guide.prompts import _format_projects_list, _format_project_config
from src.mcp_server_guide.models.project_config import ProjectConfig
from src.mcp_server_guide.models.category import Category
from src.mcp_server_guide.models.collection import Collection


def test_format_projects_list():
    """Format list of project names."""
    projects = ["project1", "project2", "project3"]
    result = _format_projects_list(projects)
    assert result == "project1\nproject2\nproject3"


def test_format_projects_list_empty():
    """Format empty project list."""
    result = _format_projects_list([])
    assert result == ""


@pytest.mark.asyncio
async def test_format_project_config_basic():
    """Format basic project config without verbose."""
    config = ProjectConfig(categories={"cat1": Category(name="cat1", dir="dir1", patterns=["*.md"])}, collections={})
    result = await _format_project_config("myproject", config, verbose=False)
    assert "**Project**: myproject" in result
    assert "**Categories**" in result
    assert "- cat1 dir1/ [*.md]" in result


@pytest.mark.asyncio
async def test_format_project_config_with_collections():
    """Format project config with collections."""
    config = ProjectConfig(
        categories={"cat1": Category(name="cat1", dir="dir1", patterns=["*.md"])},
        collections={"coll1": Collection(name="coll1", categories=["cat1", "cat2"])},
    )
    result = await _format_project_config("myproject", config, verbose=False)
    assert "**Collections**" in result
    assert "- coll1 [cat1, cat2]" in result


@pytest.mark.asyncio
async def test_format_project_config_verbose():
    """Format project config with documents in verbose mode."""
    with patch("src.mcp_server_guide.prompts._list_category_documents", return_value=["doc1.md", "doc2.txt"]):
        config = ProjectConfig(
            categories={"cat1": Category(name="cat1", dir="dir1", patterns=["*.md"])}, collections={}
        )
        result = await _format_project_config("myproject", config, verbose=True)
        assert "   - doc1.md" in result
        assert "   - doc2.txt" in result
