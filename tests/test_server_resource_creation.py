"""Tests for server resource creation and configuration handling."""

import pytest
from mcp_server_guide.server import create_server_with_config


class TestServerResourceCreation:
    """Tests for server resource creation and configuration handling."""

    def test_create_server_with_categories(self):
        """Test server creation with basic config."""
        config = {"name": "test-server", "project": "test-project"}

        # Should not raise an exception
        server = create_server_with_config(config)
        assert server is not None
        assert server.name == "test-server"
        assert server.project == "test-project"

    def test_create_server_with_empty_description(self):
        """Test server creation with empty description."""
        config = {"name": "test-server", "docroot": "/test"}

        server = create_server_with_config(config)
        assert server is not None
        assert server.docroot == "/test"

    def test_create_server_with_none_description(self):
        """Test server creation with None values."""
        config = {"name": "test-server", "project": None}

        server = create_server_with_config(config)
        assert server is not None
        assert server.project is None

    def test_create_server_with_none_values(self):
        """Test server creation with None values in various fields."""
        # Test None docroot
        config1 = {"name": "test-server", "docroot": None}
        server1 = create_server_with_config(config1)
        assert server1.docroot is None

        # Test None config_file
        config2 = {"name": "test-server", "config_file": None}
        server2 = create_server_with_config(config2)
        assert server2.config_file is None

    def test_create_server_missing_required_fields(self):
        """Test server creation with missing required fields."""
        # Empty config should still work (name is optional)
        config = {}
        server = create_server_with_config(config)
        assert server is not None

    def test_create_server_invalid_collection_config(self):
        """Test server creation with invalid collection configuration."""
        # Test with invalid config structure
        config = {"name": "test-server", "invalid_field": "invalid_value"}

        # Should handle gracefully (unknown fields ignored)
        server = create_server_with_config(config)
        assert server is not None

    def test_create_server_with_collections(self):
        """Test server creation with config file."""
        config = {"name": "test-server", "config_file": "/test/config.json"}

        server = create_server_with_config(config)
        assert server is not None
        assert server.config_file == "/test/config.json"

    def test_category_reader_success(self):
        """Test basic server creation success."""
        config = {"name": "success-server"}

        server = create_server_with_config(config)
        assert server is not None
        assert server.name == "success-server"

    def test_create_server_with_invalid_config(self):
        """Test server creation with invalid config type."""
        with pytest.raises(TypeError, match="Config must be a mapping"):
            create_server_with_config("invalid config")

    def test_collection_reader_success(self):
        """Test server creation with all parameters."""
        config = {
            "name": "collection-server",
            "project": "test-project",
            "docroot": "/test/docs",
            "config_file": "/test/config.json",
        }

        server = create_server_with_config(config)
        assert server is not None
        assert server.name == "collection-server"
        assert server.project == "test-project"
        assert server.docroot == "/test/docs"
        assert server.config_file == "/test/config.json"

    def test_collection_empty_description(self):
        """Test server creation with empty string parameters."""
        config = {"name": "empty-test", "project": "", "docroot": ""}

        server = create_server_with_config(config)
        assert server is not None
        assert server.project == ""
        assert server.docroot == ""
