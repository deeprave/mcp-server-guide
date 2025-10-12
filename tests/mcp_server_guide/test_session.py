"""Tests for session-scoped project configuration."""

from mcp_server_guide.session import SessionState, ProjectContext


async def test_session_state_creation():
    """Test creating session state."""
    session = SessionState()
    assert session is not None
    assert isinstance(session.project_config, dict)
    assert session.project_name is None  # Defaults to None, not empty string


async def test_project_context_detection():
    """Test project context detection from directory."""
    context = ProjectContext.detect("/path/to/project")
    assert context.name == "project"
    assert context.path == "/path/to/project"


async def test_session_config_get_default():
    """Test getting default configuration for project."""
    session = SessionState("test-project")
    config = session.get_project_config()
    assert isinstance(config, dict)


async def test_session_config_set_and_get():
    """Test setting and getting project configuration."""
    session = SessionState("test-project")

    # Set configuration
    session.set_project_config("guidelines", "python-web")
    session.set_project_config("language", "python")

    # Get configuration
    config = session.get_project_config()
    assert config["guidelines"] == "python-web"
    assert config["language"] == "python"


async def test_session_config_project_isolation():
    """Test session config for single project."""
    session = SessionState("projectA")

    # Set config for current project
    session.set_project_config("guidelines", "python-web")

    # Verify config
    config = session.get_project_config()
    assert config["guidelines"] == "python-web"


async def test_session_config_precedence():
    """Test session config behavior."""
    session = SessionState("test-project")

    # Set session config
    session.set_project_config("docroot", "/custom/path")

    # Should have the set value
    config = session.get_project_config()
    assert config["docroot"] == "/custom/path"


async def test_resolve_session_path_default():
    """Test resolving paths with default behavior."""
    from mcp_server_guide.session import resolve_session_path

    # Default behavior - server process context
    result = resolve_session_path("./guide.md", "test-project")
    assert result.endswith("guide.md")
    assert not result.startswith("local:")


async def test_resolve_session_path_local_prefix():
    """Test resolving paths with local: prefix."""
    from mcp_server_guide.session import resolve_session_path

    # Local prefix - explicit client access
    result = resolve_session_path("local:./guide.md", "test-project")
    assert result.endswith("guide.md")
    # Should be resolved to client path (implementation dependent)


async def test_resolve_session_path_file_urls():
    """Test resolving file:// URLs."""
    from mcp_server_guide.session import resolve_session_path

    # Relative file URL - server process context
    result = resolve_session_path("file://./guide.md", "test-project")
    assert result.endswith("guide.md")
    assert not result.startswith("file://")

    # Absolute file URL - server process context
    result = resolve_session_path("file:///etc/guide.md", "test-project")
    assert result == "/etc/guide.md"


async def test_session_config_with_local_paths():
    """Test session configuration with local file paths."""
    session = SessionState("test-project")

    # Set local file paths
    session.set_project_config("guidelines", "local:./team-guide.md")
    session.set_project_config("language", "file://./python.md")

    config = session.get_project_config()
    assert config["guidelines"] == "local:./team-guide.md"
    assert config["language"] == "file://./python.md"


async def test_validate_session_path():
    """Test path validation for session paths."""
    from mcp_server_guide.session import validate_session_path

    # Valid paths
    assert validate_session_path("./guide.md") is True
    assert validate_session_path("local:./guide.md") is True
    assert validate_session_path("file://./guide.md") is True
    assert validate_session_path("file:///etc/guide.md") is True

    # Invalid paths should be handled gracefully
    assert validate_session_path("") is False
