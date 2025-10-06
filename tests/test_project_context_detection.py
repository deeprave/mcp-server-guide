"""Tests for project context detection functionality."""

from mcp_server_guide.session import ProjectContext


def test_project_context_detection_from_path():
    """Test that ProjectContext.detect extracts project name and path correctly."""
    result = ProjectContext.detect("/some/path")
    assert result.name == "path"
    assert result.path == "/some/path"
