"""Tests for absolute path resolution in docroot."""

import pytest
import tempfile
from pathlib import Path
from src.mcp_server_guide.session_manager import SessionManager


@pytest.mark.asyncio
async def test_absolute_docroot_resolution():
    """Test that absolute docroot paths are used as-is."""
    session = SessionManager()

    with tempfile.TemporaryDirectory() as temp_dir:
        abs_path = str(Path(temp_dir).resolve())

        # Set absolute docroot
        session.session_state.set_project_config("docroot", abs_path)
        session.session_state.set_project_name("test-project")
        session.session_state.set_project_config("categories", {"guide": {"dir": "guide/", "patterns": ["*.md"]}})

        config = await session.get_effective_config("test-project")

        # Should use absolute path as-is
        assert config["docroot"] == abs_path
        assert Path(config["docroot"]).is_absolute()


@pytest.mark.asyncio
async def test_relative_docroot_resolution():
    """Test that relative docroot paths are resolved to absolute."""
    session = SessionManager()

    # Set relative docroot
    session.session_state.set_project_config("docroot", "./docs")
    session.session_state.set_project_name("test-project")
    session.session_state.set_project_config("categories", {"guide": {"dir": "guide/", "patterns": ["*.md"]}})

    config = await session.get_effective_config("test-project")

    # Should be resolved to absolute path
    assert Path(config["docroot"]).is_absolute()
    assert config["docroot"].endswith("docs")


@pytest.mark.asyncio
async def test_current_dir_docroot_resolution():
    """Test that '.' docroot is resolved to absolute current directory."""
    session = SessionManager()

    # Set current directory docroot
    session.session_state.set_project_config("docroot", ".")
    session.session_state.set_project_name("test-project")
    session.session_state.set_project_config("categories", {"guide": {"dir": "guide/", "patterns": ["*.md"]}})

    config = await session.get_effective_config("test-project")

    # Should be resolved to absolute current directory
    assert Path(config["docroot"]).is_absolute()
    assert config["docroot"] == str(Path.cwd())


@pytest.mark.asyncio
async def test_missing_docroot_defaults_to_current():
    """Test that missing docroot defaults to current directory."""
    # Capture cwd BEFORE creating SessionManager
    cwd = Path.cwd()

    # Reset singleton to ensure fresh state
    SessionManager.clear()
    session = SessionManager()

    # No docroot specified
    session.session_state.set_project_name("test-project")
    session.session_state.set_project_config("categories", {"guide": {"dir": "guide/", "patterns": ["*.md"]}})

    config = await session.get_effective_config("test-project")

    # Should default to the current directory
    assert "docroot" in config
    assert Path(config["docroot"]).is_absolute()
    assert config["docroot"] == str(cwd)
