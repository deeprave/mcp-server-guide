"""Tests for session integration with existing MCP resources."""

from mcp_server_guide.server import create_server_with_config
from mcp_server_guide.session_tools import SessionManager
from mcp_server_guide.tools.config_tools import set_project_config
from mcp_server_guide.tools.project_tools import switch_project


class TestSessionIntegration:
    """Test session integration with server configuration."""

    def setup_method(self):
        """Reset SessionManager singleton before each test."""
        # Reset the singleton instance
        SessionManager._instance = None

    def test_server_uses_session_config(self, isolated_config):
        """Test that server respects session configuration."""
        # Set session config
        switch_project("test-project")
        set_project_config("docroot", "/custom/session/path", config_filename=isolated_config)
        set_project_config("guide", "session-guidelines", config_filename=isolated_config)

        # Create server - should use session config
        config = {"docroot": "/default/path", "guide": "default-guide"}
        server = create_server_with_config(config)

        # Server should use session config over provided config
        assert server.session_config["docroot"] == "/custom/session/path"
        assert server.session_config["guide"] == "session-guidelines"

    def test_session_config_precedence(self, isolated_config):
        """Test that session config takes precedence over file config."""
        # Set session config that overrides file config
        switch_project("test-project")
        set_project_config("language", "session-python", config_filename=isolated_config)

        # Create server with different config
        config = {"language": "file-rust", "docroot": "/test/path"}
        server = create_server_with_config(config)

        # Session should override file config
        assert server.session_config["language"] == "session-python"
        # Non-overridden config should come from file
        assert server.session_config["docroot"] == "/test/path"

    def test_session_local_file_resolution(self, isolated_config):
        """Test that session resolves local file paths correctly."""
        # Set session config with local file
        switch_project("test-project")
        set_project_config("language", "file://./session-lang.md", config_filename=isolated_config)

        # Create server
        config = {}
        server = create_server_with_config(config)

        # Should resolve local file path
        resolved_path = server.resolve_session_path("file://./session-lang.md")
        assert resolved_path.endswith("session-lang.md")

    def test_mixed_session_and_default_config(self, isolated_config):
        """Test mixing session config with default values."""
        # Set only some session config
        switch_project("test-project")
        set_project_config("guide", "session-guide", config_filename=isolated_config)

        # Create server with partial config
        config = {"docroot": "/mixed/path"}
        server = create_server_with_config(config)

        # Should have session config where set
        assert server.session_config["guide"] == "session-guide"
        # Should have provided config for others
        assert server.session_config["docroot"] == "/mixed/path"

    def test_project_switching_affects_server(self, isolated_config):
        """Test that switching projects affects server configuration."""
        # Set config for project A
        switch_project("project-a")
        set_project_config("guide", "project-a-guide", config_filename=isolated_config)

        # Create server
        config = {}
        server_a = create_server_with_config(config)

        # Switch to project B and set different config
        switch_project("project-b")
        set_project_config("guide", "project-b-guide", config_filename=isolated_config)

        # Create new server
        server_b = create_server_with_config(config)

        # Servers should have different configs
        assert server_a.session_config["guide"] == "project-a-guide"
        assert server_b.session_config["guide"] == "project-b-guide"

    def test_session_path_resolution_in_server(self, isolated_config):
        """Test that server resolves session paths correctly."""
        # Set session config with various path types
        switch_project("path-resolution-test")
        set_project_config("guide", "local:./client-guide.md", config_filename=isolated_config)
        set_project_config("language", "file:///server/lang.md", config_filename=isolated_config)
        set_project_config("docroot", "./relative-path", config_filename=isolated_config)

        # Create server
        config = {}
        server = create_server_with_config(config)

        # Should resolve paths according to session rules
        resolved_guide = server.resolve_session_path("local:./client-guide.md")
        resolved_lang = server.resolve_session_path("file:///server/lang.md")
        resolved_docroot = server.resolve_session_path("./relative-path")

        # Local should be resolved to client path
        assert resolved_guide.endswith("client-guide.md")
        # File URL should be resolved to server path
        assert resolved_lang == "/server/lang.md"
        # Relative should be resolved relative to docroot
        assert resolved_docroot.endswith("relative-path")
