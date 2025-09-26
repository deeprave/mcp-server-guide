"""Tests for session integration with existing MCP resources."""

from mcp_server_guide.server import create_server_with_config
from mcp_server_guide.session_tools import SessionManager, set_local_file
from mcp_server_guide.tools.config_tools import set_project_config
from mcp_server_guide.tools.project_tools import switch_project


class TestSessionIntegration:
    """Test session integration with server configuration."""

    def setup_method(self):
        """Reset SessionManager singleton before each test."""
        # Reset the singleton instance
        SessionManager._instance = None

    def test_server_uses_session_config(self):
        """Test that server respects session configuration."""
        # Set session config
        switch_project("test-project")
        set_project_config("docroot", "/custom/session/path")
        set_project_config("guide", "session-guidelines")

        # Create server - should use session config
        config = {"docroot": "/default/path", "guide": "default-guide"}
        server = create_server_with_config(config)

        # Server should use session config over provided config
        assert server.session_config["docroot"] == "/custom/session/path"
        assert server.session_config["guide"] == "session-guidelines"

    def test_session_config_precedence(self):
        """Test session config takes precedence over CLI/env config."""
        # Set session config
        switch_project("precedence-test")
        set_project_config("language", "session-python")

        # Create server with different config
        config = {"language": "cli-rust", "docroot": "/cli/path"}
        server = create_server_with_config(config)

        # Session should override CLI for set values
        assert server.session_config["language"] == "session-python"
        # CLI should be used for unset session values
        assert server.session_config["docroot"] == "/cli/path"

    def test_session_local_file_resolution(self):
        """Test that session local files are resolved correctly."""
        # Set local file in session
        switch_project("local-file-test")
        set_local_file("guide", "./session-guide.md")
        set_project_config("language", "file://./session-lang.md")

        # Create server
        config = {"docroot": "."}
        server = create_server_with_config(config)

        # Should have session paths
        assert server.session_config["guide"] == "local:./session-guide.md"
        assert server.session_config["language"] == "file://./session-lang.md"

    def test_mixed_session_and_default_config(self):
        """Test mixing session config with defaults."""
        # Set partial session config
        switch_project("mixed-test")
        set_project_config("guide", "session-guide")
        # Leave other values as defaults

        # Create server
        config = {"docroot": "/server/path"}
        server = create_server_with_config(config)

        # Should mix session and provided config
        assert server.session_config["guide"] == "session-guide"  # From session
        assert server.session_config["docroot"] == "/server/path"  # From config
        assert server.session_config["guidesdir"] == "guide/"  # Default

    def test_project_switching_affects_server(self):
        """Test that switching projects affects server configuration."""
        # Set config for project A
        switch_project("projectA")
        set_project_config("guide", "project-a-guide")

        # Create server for project A and capture its config
        config = {"docroot": "."}
        serverA = create_server_with_config(config)
        serverA_guide = serverA.session_config["guide"]

        # Set config for project B
        switch_project("projectB")
        set_project_config("guide", "project-b-guide")

        # Create server for project B
        serverB = create_server_with_config(config)
        serverB_guide = serverB.session_config["guide"]

        # Should have different configs
        assert serverA_guide == "project-a-guide"
        assert serverB_guide == "project-b-guide"

    def test_session_path_resolution_in_server(self):
        """Test that server resolves session paths correctly."""
        # Set session config with various path types
        switch_project("path-resolution-test")
        set_project_config("guide", "local:./client-guide.md")
        set_project_config("language", "file:///server/lang.md")
        set_project_config("docroot", "./relative-path")

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
        # Default should be resolved to server path
        assert resolved_docroot.endswith("relative-path")
