"""Test concurrent initialization race condition fix."""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from mcp_server_guide.server import ensure_client_roots_initialized


@pytest.mark.asyncio
async def test_concurrent_initialization_calls():
    """Test that concurrent calls to ensure_client_roots_initialized don't cause race conditions."""

    # Reset ClientPath._initialized for this test
    with patch("mcp_server_guide.server.ClientPath") as mock_client_path:
        # Set up the mock to track initialization state
        initialized = False

        def get_initialized():
            return initialized

        def set_initialized(value):
            nonlocal initialized
            initialized = value

        # Create a real async lock for proper synchronization
        real_lock = asyncio.Lock()

        # Mock the new encapsulated methods
        mock_client_path.is_initialized.side_effect = get_initialized
        mock_client_path.get_init_lock.return_value = real_lock

        # Mock the MCP context
        mock_context = MagicMock()
        mock_context.session = MagicMock()

        with patch("mcp_server_guide.server.mcp") as mock_mcp:
            mock_mcp.get_context.return_value = mock_context

            # Mock ClientPath.initialize to simulate some async work
            initialize_call_count = 0

            async def mock_initialize(session):
                nonlocal initialize_call_count
                initialize_call_count += 1
                # Simulate some async work
                await asyncio.sleep(0.01)
                set_initialized(True)

            mock_client_path.initialize = AsyncMock(side_effect=mock_initialize)

            # Launch multiple concurrent calls
            tasks = [ensure_client_roots_initialized() for _ in range(5)]
            await asyncio.gather(*tasks)

            # Verify initialize was called only once despite multiple concurrent calls
            assert initialize_call_count == 1
            mock_client_path.initialize.assert_called_once()


@pytest.mark.asyncio
async def test_initialization_already_done():
    """Test that no initialization occurs when already initialized."""

    with patch("mcp_server_guide.server.ClientPath") as mock_client_path:
        mock_client_path._initialized = True

        # Should return immediately without any MCP calls
        await ensure_client_roots_initialized()

        # Verify no initialization calls were made
        mock_client_path.initialize.assert_not_called()
