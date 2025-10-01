"""Tests for absolute path resolution in docroot."""

import tempfile
from pathlib import Path
from src.mcp_server_guide.session_tools import SessionManager


async def test_absolute_docroot_resolution():
    """Test that absolute docroot paths are used as-is."""
    session = SessionManager()

    with tempfile.TemporaryDirectory() as temp_dir:
        abs_path = str(Path(temp_dir).resolve())

        # Set absolute docroot
        session.session_state.projects["test-project"] = {
            "docroot": abs_path,
            "categories": {"guide": {"dir": "guide/", "patterns": ["*.md"]}},
        }

        config = session.get_effective_config("test-project")

        # Should use absolute path as-is
        assert config["docroot"] == abs_path
        assert Path(config["docroot"]).is_absolute()


async def test_relative_docroot_resolution():
    """Test that relative docroot paths are resolved to absolute."""
    session = SessionManager()

    # Set relative docroot
    session.session_state.projects["test-project"] = {
        "docroot": "./docs",
        "categories": {"guide": {"dir": "guide/", "patterns": ["*.md"]}},
    }

    config = session.get_effective_config("test-project")

    # Should be resolved to absolute path
    assert Path(config["docroot"]).is_absolute()
    assert config["docroot"].endswith("docs")


async def test_current_dir_docroot_resolution():
    """Test that '.' docroot is resolved to absolute current directory."""
    session = SessionManager()

    # Set current directory docroot
    session.session_state.projects["test-project"] = {
        "docroot": ".",
        "categories": {"guide": {"dir": "guide/", "patterns": ["*.md"]}},
    }

    config = session.get_effective_config("test-project")

    # Should be resolved to absolute current directory
    assert Path(config["docroot"]).is_absolute()
    assert config["docroot"] == str(Path.cwd())


async def test_missing_docroot_defaults_to_current():
    """Test that missing docroot defaults to current directory."""
    session = SessionManager()

    # No docroot specified
    session.session_state.projects["test-project"] = {"categories": {"guide": {"dir": "guide/", "patterns": ["*.md"]}}}

    config = session.get_effective_config("test-project")

    # Should default to current directory
    assert "docroot" in config
    assert Path(config["docroot"]).is_absolute()
    assert config["docroot"] == str(Path.cwd())
