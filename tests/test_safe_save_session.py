"""Test the safe_save_session functionality."""

import pytest
from unittest.mock import AsyncMock, patch
from mcp_server_guide.session_manager import SessionManager


class TestSafeSaveSession:
    """Test the safe_save_session method."""

    @pytest.mark.asyncio
    async def test_safe_save_session_success(self):
        """Test safe_save_session when save_session succeeds."""
        with patch("mcp_server_guide.session_manager.SessionManager.save_session") as mock_save:
            mock_save.return_value = AsyncMock()

            session = SessionManager()

            # Should not raise any exception
            await session.safe_save_session()

            # Verify save_session was called
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_safe_save_session_handles_exceptions(self):
        """Test safe_save_session when save_session fails."""
        with patch("mcp_server_guide.session_manager.SessionManager.save_session") as mock_save:
            mock_save.side_effect = Exception("Save failed")

            session = SessionManager()

            # Should not raise any exception even when save_session fails
            await session.safe_save_session()

            # Verify save_session was called
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_safe_save_session_logs_success(self):
        """Test safe_save_session logs success."""
        with patch("mcp_server_guide.session_manager.SessionManager.save_session") as mock_save:
            with patch("mcp_server_guide.session_manager.logger") as mock_logger:
                mock_save.return_value = AsyncMock()

                session = SessionManager()
                await session.safe_save_session()

                # Verify debug log was called with the auto-save message
                mock_logger.debug.assert_any_call("Auto-saved session")

    @pytest.mark.asyncio
    async def test_safe_save_session_logs_failure(self):
        """Test safe_save_session logs failure."""
        with patch("mcp_server_guide.session_manager.SessionManager.save_session") as mock_save:
            with patch("mcp_server_guide.session_manager.logger") as mock_logger:
                mock_save.side_effect = Exception("Save failed")

                session = SessionManager()
                await session.safe_save_session()

                # Verify warning log was called
                mock_logger.warning.assert_called_once_with("Auto-save failed: Save failed")
