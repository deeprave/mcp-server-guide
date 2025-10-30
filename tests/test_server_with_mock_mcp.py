"""Tests for server.py using MockMCP."""

import pytest
from unittest.mock import patch
from mcp_server_guide.server import create_server, create_server_with_config


class TestServerWithMockMCP:
    """Tests for server.py using MockMCP."""

    def test_create_server_basic(self):
        """Test create_server basic functionality."""
        server = create_server()
        assert server is not None
        assert hasattr(server, "name")

    def test_create_server_with_config_basic(self):
        """Test create_server_with_config basic functionality."""
        config = {"name": "test-server", "project": "test-project"}

        server = create_server_with_config(config)
        assert server is not None
        assert server.name == "test-server"
        assert server.project == "test-project"

    def test_create_server_with_config_empty(self):
        """Test create_server_with_config with empty config."""
        config = {}  # Empty config should work

        # Mock the lifespan function to be callable
        def mock_lifespan(server):
            return None

        with patch("mcp_server_guide.server.server_lifespan", mock_lifespan):
            server = create_server_with_config(config)
            assert server is not None

    def test_create_server_with_invalid_config_type(self):
        """Test create_server_with_config with invalid config type."""
        with pytest.raises(TypeError):
            create_server_with_config("not_a_dict")
