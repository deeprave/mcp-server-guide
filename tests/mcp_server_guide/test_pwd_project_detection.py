"""Tests for PWD-based project detection."""

import os
import pytest
from unittest.mock import patch
from src.mcp_server_guide.session_tools import SessionManager


@pytest.mark.asyncio
async def test_get_current_project_uses_pwd_when_current_project_none():
    """Test that get_current_project uses PWD when _current_project is None."""
    session_manager = SessionManager()

    # Ensure _current_project is None
    session_manager._current_project = None

    with patch.dict(os.environ, {"PWD": "/home/user/my-project"}):
        project = await session_manager.get_current_project()
        assert project == "my-project"


@pytest.mark.asyncio
async def test_get_current_project_returns_current_project_when_set():
    """Test that get_current_project returns _current_project when it's set."""
    session_manager = SessionManager()

    # Set _current_project to a specific value
    session_manager._current_project = "explicit-project"

    with patch.dict(os.environ, {"PWD": "/home/user/different-project"}):
        project = await session_manager.get_current_project()
        assert project == "explicit-project"  # Should return the set value, not PWD


@pytest.mark.asyncio
async def test_get_current_project_returns_none_when_pwd_not_available():
    """Test that get_current_project returns None when PWD is not available."""
    session_manager = SessionManager()

    # Ensure _current_project is None
    session_manager._current_project = None

    # Remove PWD from environment
    with patch.dict(os.environ, {}, clear=True):
        project = await session_manager.get_current_project()
        assert project is None


@pytest.mark.asyncio
async def test_set_current_project_without_file_io():
    """Test that set_current_project only sets _current_project without file I/O."""
    session_manager = SessionManager()

    # Should not require directory to be set
    await session_manager.set_current_project("new-project")

    # Should set the internal field
    assert session_manager._current_project == "new-project"

    # Should return the set project
    project = await session_manager.get_current_project()
    assert project == "new-project"
