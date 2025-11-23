"""Tests for project tools error handling."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from mcp_server_guide.tools.project_tools import switch_project


class TestProjectToolsErrorHandling:
    """Tests for project tools error handling scenarios."""

    @pytest.mark.asyncio
    async def test_switch_project_value_error(self):
        """Test switch_project with ValueError from session."""
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.switch_project = AsyncMock(side_effect=ValueError("Invalid project"))

            result = await switch_project("invalid")
            assert not result["success"]
            assert "Invalid project" in result["error"]

    @pytest.mark.asyncio
    async def test_switch_project_permission_error(self):
        """Test switch_project with PermissionError."""
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.switch_project = AsyncMock(side_effect=PermissionError("Access denied"))

            result = await switch_project("restricted")
            assert not result["success"]
            assert "Access denied" in result["error"]

    @pytest.mark.asyncio
    async def test_switch_project_unexpected_error(self):
        """Test switch_project with unexpected exception."""
        with patch("mcp_server_guide.session_manager.SessionManager") as mock_sm:
            mock_session = Mock()
            mock_sm.return_value = mock_session
            mock_session.switch_project = AsyncMock(side_effect=RuntimeError("Unexpected failure"))

            result = await switch_project("failing")
            assert not result["success"]
            assert "Unexpected failure" in result["error"]
