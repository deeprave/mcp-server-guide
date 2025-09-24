"""Tests for session-scoped project configuration."""

from mcpguide.session import SessionState, ProjectContext


def test_session_state_creation():
    """Test creating session state."""
    session = SessionState()
    assert session is not None
    assert isinstance(session.projects, dict)


def test_project_context_detection():
    """Test project context detection from directory."""
    context = ProjectContext.detect("/path/to/project")
    assert context.name == "project"
    assert context.path == "/path/to/project"


def test_session_config_get_default():
    """Test getting default configuration for project."""
    session = SessionState()
    config = session.get_project_config("test-project")

    # Should return default values
    assert config["docroot"] == "."
    assert config["guidesdir"] == "guide/"
    assert config["guide"] == "guidelines"


def test_session_config_set_and_get():
    """Test setting and getting project configuration."""
    session = SessionState()

    # Set configuration
    session.set_project_config("test-project", "guidelines", "python-web")
    session.set_project_config("test-project", "language", "python")

    # Get configuration
    config = session.get_project_config("test-project")
    assert config["guidelines"] == "python-web"
    assert config["language"] == "python"
    # Other values should remain default
    assert config["docroot"] == "."


def test_session_config_project_isolation():
    """Test that projects have isolated configurations."""
    session = SessionState()

    # Set different configs for different projects
    session.set_project_config("projectA", "guidelines", "python-web")
    session.set_project_config("projectB", "guidelines", "rust-systems")

    # Verify isolation
    configA = session.get_project_config("projectA")
    configB = session.get_project_config("projectB")

    assert configA["guidelines"] == "python-web"
    assert configB["guidelines"] == "rust-systems"


def test_session_config_precedence():
    """Test that session config takes precedence over defaults."""
    session = SessionState()

    # Set session config
    session.set_project_config("test-project", "docroot", "/custom/path")

    # Should override default
    config = session.get_project_config("test-project")
    assert config["docroot"] == "/custom/path"
    assert config["guidesdir"] == "guide/"  # Default unchanged
def test_resolve_session_path_default():
    """Test resolving paths with default behavior."""
    from mcpguide.session import resolve_session_path

    # Default behavior - server process context
    result = resolve_session_path("./guide.md", "test-project")
    assert result.endswith("guide.md")
    assert not result.startswith("local:")


def test_resolve_session_path_local_prefix():
    """Test resolving paths with local: prefix."""
    from mcpguide.session import resolve_session_path

    # Local prefix - explicit client access
    result = resolve_session_path("local:./guide.md", "test-project")
    assert result.endswith("guide.md")
    # Should be resolved to client path (implementation dependent)


def test_resolve_session_path_file_urls():
    """Test resolving file:// URLs."""
    from mcpguide.session import resolve_session_path

    # Relative file URL - server process context
    result = resolve_session_path("file://./guide.md", "test-project")
    assert result.endswith("guide.md")
    assert not result.startswith("file://")

    # Absolute file URL - server process context
    result = resolve_session_path("file:///etc/guide.md", "test-project")
    assert result == "/etc/guide.md"


def test_session_config_with_local_paths():
    """Test session configuration with local file paths."""
    session = SessionState()

    # Set local file paths
    session.set_project_config("test-project", "guidelines", "local:./team-guide.md")
    session.set_project_config("test-project", "language", "file://./python.md")

    config = session.get_project_config("test-project")
    assert config["guidelines"] == "local:./team-guide.md"
    assert config["language"] == "file://./python.md"


def test_validate_session_path():
    """Test path validation for session paths."""
    from mcpguide.session import validate_session_path

    # Valid paths
    assert validate_session_path("./guide.md") is True
    assert validate_session_path("local:./guide.md") is True
    assert validate_session_path("file://./guide.md") is True
    assert validate_session_path("file:///etc/guide.md") is True

    # Invalid paths should be handled gracefully
    assert validate_session_path("") is False
