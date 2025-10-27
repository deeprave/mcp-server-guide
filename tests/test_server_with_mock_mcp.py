"""Tests for server.py using MockMCP."""

import pytest
from unittest.mock import patch
from mcp_server_guide.server import create_server, create_server_with_config


class TestServerWithMockMCP:
    """Tests for server.py using MockMCP."""

    def test_create_server_basic(self):
        """Test create_server basic functionality."""
        with patch("mcp_server_guide.server.server_lifespan"):
            server = create_server()
            assert server is not None
            assert hasattr(server, 'name')

    def test_create_server_with_config_basic(self):
        """Test create_server_with_config basic functionality."""
        config = {
            "categories": {"test": {"dir": "/test", "patterns": ["*.py"]}},
            "collections": {}
        }

        with patch("mcp_server_guide.server.server_lifespan"):
            server = create_server_with_config(config)
            assert server is not None
            assert hasattr(server, 'name')

    def test_create_server_with_config_empty(self):
        """Test create_server_with_config with empty config."""
        config = {"categories": {}, "collections": {}}

        with patch("mcp_server_guide.server.server_lifespan"):
            server = create_server_with_config(config)
            assert server is not None

    def test_create_server_with_invalid_config_type(self):
        """Test create_server_with_config with invalid config type."""
        with pytest.raises(AttributeError):
            create_server_with_config("not_a_dict")
