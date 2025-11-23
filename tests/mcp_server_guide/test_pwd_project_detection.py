"""Tests for PWD-based project detection."""

import os
from unittest.mock import patch

import pytest

from mcp_server_guide.session_manager import SessionManager


@pytest.mark.asyncio
async def test_get_current_project_uses_pwd_when_current_project_none():
    """Test that get_current_project uses PWD when project_name is None."""
    # Reset singleton to ensure fresh state
    SessionManager.clear()
    session_manager = SessionManager()

    # Ensure project_name is None
    session_manager.session_state.project_name = None

    with patch.dict(os.environ, {"PWD": "/home/user/my-project"}):
        project = session_manager.get_project_name()
        assert project == "my-project"


@pytest.mark.asyncio
async def test_get_current_project_returns_current_project_when_set():
    """Test that get_current_project returns _current_project when it's set."""
    session_manager = SessionManager()

    # Set _current_project to a specific value
    session_manager.set_project_name("explicit-project")

    with patch.dict(os.environ, {"PWD": "/home/user/different-project"}):
        project = session_manager.get_project_name()
        assert project == "explicit-project"  # Should return the set value, not PWD


@pytest.mark.asyncio
async def test_get_current_project_raises_when_pwd_not_available():
    """Test that get_current_project raises ValueError when PWD is not available."""
    session_manager = SessionManager()

    # Ensure _current_project is None
    session_manager.session_state.project_name = None

    # Remove PWD from environment - should raise ValueError
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="Cannot determine project name"):
            session_manager.get_project_name()


@pytest.mark.asyncio
async def test_set_current_project_without_file_io():
    """Test that set_current_project only sets _current_project without file I/O."""
    session_manager = SessionManager()

    # Should not require directory to be set
    session_manager.set_project_name("new-project")

    # Should set the internal field
    assert session_manager.session_state.project_name == "new-project"

    # Should return the set project
    project = session_manager.get_project_name()
    assert project == "new-project"
