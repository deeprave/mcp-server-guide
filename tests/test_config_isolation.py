"""Tests to verify that test collections don't leak to live config."""

from pathlib import Path

import pytest

from mcp_server_guide.session_manager import SessionManager
from mcp_server_guide.tools.collection_tools import add_collection


class TestConfigIsolation:
    """Test that test collections don't appear in live config."""

    @pytest.mark.asyncio
    async def test_collections_dont_leak_to_live_config(self, isolated_config_file):
        """Test that test collections don't appear in live config."""
        # Get the live config path
        live_config_manager = SessionManager()._config_manager
        live_config_path = live_config_manager.get_config_filename()

        # Read live config before test
        live_config_before = None
        if Path(live_config_path).exists():
            with open(live_config_path) as f:
                live_config_before = f.read()

        # Use isolated config for this test
        session = SessionManager()
        session._config_manager.set_config_filename(isolated_config_file)

        # Create a test collection in isolated environment
        result = await add_collection("test_isolation_collection", ["guide"], "Isolation test")
        assert result["success"] is True

        # Verify live config is unchanged
        live_config_after = None
        if Path(live_config_path).exists():
            with open(live_config_path) as f:
                live_config_after = f.read()

        # Live config should be unchanged
        assert live_config_before == live_config_after

        # Verify the test collection is NOT in live config
        if live_config_after:
            assert "test_isolation_collection" not in live_config_after
