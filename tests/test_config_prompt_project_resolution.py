"""Test config_prompt project name resolution with PWD fallback."""

import json
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

        # Mock get_or_create_project_config
        mock_config = MagicMock()
        mock_config.categories = {}
        mock_config.collections = {}
        mock_sm.get_or_create_project_config = AsyncMock(return_value=mock_config)

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


@pytest.mark.asyncio
async def test_config_prompt_returns_result_json_format() -> None:
    """Test that config_prompt returns Result.to_json() format."""
    with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm_class:
        mock_sm = MagicMock()
        mock_sm_class.return_value = mock_sm

        mock_sm.get_project_name.return_value = "test-project"
        mock_config = MagicMock()
        mock_config.categories = {}
        mock_config.collections = {}
        mock_sm.get_or_create_project_config = AsyncMock(return_value=mock_config)

        result = await config_prompt()

        # Should be JSON string with Result format
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert "value" in parsed
        assert "instruction" in parsed
        assert "test-project" in parsed["value"]


@pytest.mark.asyncio
async def test_config_prompt_error_includes_error_type() -> None:
    """Test that config_prompt errors include error_type field from Result."""
    with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm_class:
        mock_sm = MagicMock()
        mock_sm_class.return_value = mock_sm

        error_msg = "Cannot determine project name"
        mock_sm.get_project_name.side_effect = ValueError(error_msg)

        result = await config_prompt()

        # Should include error_type field from Result pattern
        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "error" in parsed
        assert "error_type" in parsed  # This is the new field from Result
        assert parsed["error_type"] == "project_context"


@pytest.mark.asyncio
async def test_config_prompt_list_projects_returns_result_json_format() -> None:
    """Test list_projects=True branch returns Result.to_json() format."""
    with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm_class:
        mock_sm = MagicMock()
        mock_sm_class.return_value = mock_sm

        # Mock projects list
        mock_sm.list_all_projects = AsyncMock(return_value=["proj-a", "proj-b"])

        result = await config_prompt(list_projects=True)

        # Should be JSON string with Result format
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert "value" in parsed
        assert "instruction" in parsed

        # Projects should be included in the value
        assert "proj-a" in parsed["value"]
        assert "proj-b" in parsed["value"]


@pytest.mark.asyncio
async def test_config_prompt_project_not_found_error_result_json_format() -> None:
    """Test project_not_found error branch returns Result.to_json() format."""
    with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm_class:
        mock_sm = MagicMock()
        mock_sm_class.return_value = mock_sm

        # Mock project name resolution
        mock_sm.get_project_name.return_value = "missing-project"

        # Simulate missing project config
        mock_sm.get_or_create_project_config = AsyncMock(return_value=None)

        result = await config_prompt()

        # Should be JSON string with Result error format
        parsed = json.loads(result)
        assert parsed["success"] is False
        assert parsed["error_type"] == "project_not_found"

        # Error message should reference the missing project
        assert "error" in parsed
        assert "missing-project" in parsed["error"]
