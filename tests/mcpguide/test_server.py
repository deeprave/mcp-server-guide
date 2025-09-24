"""Tests for mcpguide server module."""

from pathlib import Path

from mcpguide.server import mcp, defaults, create_server_with_config


def test_mcp_instance_exists():
    """Test that MCP instance is created."""
    assert mcp is not None
    assert hasattr(mcp, "name")


def test_mcp_name():
    """Test MCP instance has correct name."""
    assert mcp.name == "Developer Guide MCP"


def test_defaults_structure():
    """Test defaults dictionary has expected structure."""
    assert isinstance(defaults, dict)
    assert "guide" in defaults
    assert "project" in defaults
    assert "lang" in defaults


def test_defaults_paths():
    """Test defaults contain valid path strings."""
    for key, path in defaults.items():
        assert isinstance(path, str)
        assert path.startswith("./")


def test_guide_directory_exists(guide_dir: Path):
    """Test guide directory exists."""
    assert guide_dir.exists()
    assert guide_dir.is_dir()


def test_project_directory_exists(project_dir: Path):
    """Test project directory exists."""
    assert project_dir.exists()
    assert project_dir.is_dir()


def test_lang_directory_exists(lang_dir: Path):
    """Test lang directory exists."""
    assert lang_dir.exists()
    assert lang_dir.is_dir()


def test_create_server_with_config():
    """Test creating server with configuration."""
    resolved_config = {
        "docroot": ".",
        "guidesdir": "guide/",
        "guide": "guidelines",
        "langdir": "lang/",
        "language": "python",
        "projdir": "project/",
        "project": "mcpguide",
    }

    server = create_server_with_config(resolved_config)
    assert server is not None
    assert hasattr(server, "name")
    assert server.name == "Developer Guide MCP"
