"""Test config_prompt project name resolution with PWD fallback."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_server_guide.prompts import config_prompt


@pytest.mark.asyncio
async def test_config_prompt_uses_get_project_name_method(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that config_prompt calls get_project_name() not .project_name property."""
    monkeypatch.setenv("PWD", "/path/to/test-project")

    with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm_class:
        mock_sm = MagicMock()
        mock_sm_class.return_value = mock_sm

        # Mock get_project_name to return test project
        mock_sm.get_project_name.return_value = "test-project"

        # Mock get_full_project_config
        mock_config = MagicMock()
        mock_config.categories = {}
        mock_config.collections = {}
        mock_sm.get_full_project_config.return_value = mock_config

        result = await config_prompt()

        # Should call get_project_name() method
        mock_sm.get_project_name.assert_called_once()
        assert "test-project" in result
        assert "unknown" not in result.lower()


@pytest.mark.asyncio
async def test_config_prompt_handles_value_error_from_get_project_name() -> None:
    """Test that config_prompt handles ValueError when project name cannot be determined."""
    with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm_class:
        mock_sm = MagicMock()
        mock_sm_class.return_value = mock_sm

        # Mock get_project_name to raise ValueError
        error_msg = (
            "Cannot determine project name: no session state, context resolution, or PWD environment variable available.\n"
            "To fix: Call switch_project with the basename of the current working directory."
        )
        mock_sm.get_project_name.side_effect = ValueError(error_msg)

        result = await config_prompt()

        # Should contain error message with fix instruction
        assert "switch_project" in result
        assert "Cannot determine project name" in result
        assert "unknown" not in result.lower()


@pytest.mark.asyncio
async def test_config_prompt_with_explicit_project_bypasses_get_project_name() -> None:
    """Test that config_prompt with explicit project parameter doesn't call get_project_name."""
    with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm_class:
        mock_sm = MagicMock()
        mock_sm_class.return_value = mock_sm

        # Mock load_project_config
        mock_config = MagicMock()
        mock_config.categories = {}
        mock_config.collections = {}
        mock_sm.load_project_config = AsyncMock(return_value=mock_config)

        result = await config_prompt(project="explicit-project")

        # Should NOT call get_project_name when explicit project provided
        mock_sm.get_project_name.assert_not_called()
        assert "explicit-project" in result
