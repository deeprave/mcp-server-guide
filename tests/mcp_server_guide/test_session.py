"""Tests for session-scoped project configuration."""

from mcp_server_guide.project_config import ProjectConfig
from mcp_server_guide.session import ProjectContext, SessionState


async def test_session_state_creation():
    """Test creating session state."""
    session = SessionState()
    assert session is not None
    assert isinstance(session.project_config, ProjectConfig)
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
    assert isinstance(config, ProjectConfig)


async def test_session_config_set_and_get():
    """Test setting and getting project configuration."""
    session = SessionState("test-project")

    # Set configuration - only 'categories' is valid now
    test_categories = {
        "guide": {"dir": "guide/", "patterns": ["*.md"], "description": "Guidelines"},
        "lang": {"dir": "lang/", "patterns": ["*.md"], "description": "Language guides"},
    }
    session.set_project_config("categories", test_categories)

    # Get configuration
    config = session.get_project_config()
    assert config.to_dict()["categories"] == test_categories


async def test_session_config_project_isolation():
    """Test session config for single project."""
    session = SessionState("projectA")

    # Set config for current project - only 'categories' is valid now
    test_categories = {"guide": {"dir": "guide/", "patterns": ["*.md"]}}
    session.set_project_config("categories", test_categories)

    # Verify config
    config = session.get_project_config()
    config_dict = config.to_dict()
    # Check that guide category exists with correct values
    assert "guide" in config_dict["categories"]
    assert config_dict["categories"]["guide"]["dir"] == "guide/"
    assert config_dict["categories"]["guide"]["patterns"] == ["*.md"]


async def test_session_config_precedence():
    """Test session config behavior."""
    session = SessionState("test-project")

    # Set session config - only 'categories' is valid now
    test_categories_v1 = {"guide": {"dir": "guide/", "patterns": ["*.md"]}}
    session.set_project_config("categories", test_categories_v1)

    # Should have the set value
    config = session.get_project_config()
    config_dict = config.to_dict()
    assert "guide" in config_dict["categories"]
    assert config_dict["categories"]["guide"]["dir"] == "guide/"

    # Update with new value
    test_categories_v2 = {"context": {"dir": "context/", "patterns": ["*.md"]}}
    session.set_project_config("categories", test_categories_v2)

    # Should have the updated value
    config = session.get_project_config()
    config_dict = config.to_dict()
    assert "context" in config_dict["categories"]
    assert config_dict["categories"]["context"]["dir"] == "context/"


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


async def test_session_config_with_categories():
    """Test session configuration with categories structure."""
    session = SessionState("test-project")

    # Set categories with various directory paths
    test_categories = {
        "local_guide": {"dir": "local/guide/", "patterns": ["*.md"]},
        "remote_lang": {"dir": "remote/lang/", "patterns": ["*.py"]},
    }
    session.set_project_config("categories", test_categories)

    config = session.get_project_config()
    config_dict = config.to_dict()
    # Check categories exist
    assert "local_guide" in config_dict["categories"]
    assert "remote_lang" in config_dict["categories"]
    # Check specific values
    assert config_dict["categories"]["local_guide"]["dir"] == "local/guide/"
    assert config_dict["categories"]["local_guide"]["patterns"] == ["*.md"]
    assert config_dict["categories"]["remote_lang"]["dir"] == "remote/lang/"
    assert config_dict["categories"]["remote_lang"]["patterns"] == ["*.py"]


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
