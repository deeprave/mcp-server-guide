"""Tests for persistent project configuration (Issue 004)."""

import json
import tempfile
from pathlib import Path
from mcpguide.project_config import ProjectConfig, ProjectConfigManager


def test_project_config_creation():
    """Test creating project configuration."""
    config = ProjectConfig(project="test-project", guide="local:./guide.md", language="python", docroot="local:./docs")

    assert config.project == "test-project"
    assert config.guide == "local:./guide.md"
    assert config.language == "python"
    assert config.docroot == "local:./docs"


def test_project_config_to_dict():
    """Test converting project config to dictionary."""
    config = ProjectConfig(
        project="web-app", guide="https://example.com/guide.md", language="typescript", tools=["github", "jest"]
    )

    config_dict = config.to_dict()
    expected = {
        "project": "web-app",
        "guide": "https://example.com/guide.md",
        "language": "typescript",
        "tools": ["github", "jest"],
    }

    assert config_dict == expected


def test_project_config_from_dict():
    """Test creating project config from dictionary."""
    config_dict = {
        "project": "api-service",
        "guide": "server:./api-guide.md",
        "language": "rust",
        "docroot": "local:./documentation",
    }

    config = ProjectConfig.from_dict(config_dict)
    assert config.project == "api-service"
    assert config.guide == "server:./api-guide.md"
    assert config.language == "rust"
    assert config.docroot == "local:./documentation"


def test_project_config_manager_save():
    """Test saving project configuration to file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        manager = ProjectConfigManager()

        config = ProjectConfig(project="save-test", guide="https://example.com/guide.md", language="python")

        # Save configuration
        manager.save_config(project_path, config)

        # Check file was created
        config_file = project_path / ".mcpguide.config.json"
        assert config_file.exists()

        # Check file contents
        with open(config_file) as f:
            saved_data = json.load(f)

        expected = {"project": "save-test", "guide": "https://example.com/guide.md", "language": "python"}
        assert saved_data == expected


def test_project_config_manager_load():
    """Test loading project configuration from file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        config_file = project_path / ".mcpguide.config.json"

        # Create config file
        config_data = {
            "project": "load-test",
            "guide": "local:./team-guide.md",
            "language": "javascript",
            "tools": ["eslint", "jest"],
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        # Load configuration
        manager = ProjectConfigManager()
        config = manager.load_config(project_path)

        assert config.project == "load-test"
        assert config.guide == "local:./team-guide.md"
        assert config.language == "javascript"
        assert config.tools == ["eslint", "jest"]


def test_project_config_manager_load_missing_file():
    """Test loading configuration when file doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        manager = ProjectConfigManager()

        # Should return None for missing file
        config = manager.load_config(project_path)
        assert config is None


def test_project_config_manager_detect_project_root():
    """Test detecting project root by finding config file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create nested directory structure
        project_root = Path(temp_dir) / "my-project"
        sub_dir = project_root / "src" / "components"
        sub_dir.mkdir(parents=True)

        # Create config file in project root
        config_file = project_root / ".mcpguide.config.json"
        config_data = {"project": "my-project", "guide": "local:./README.md"}

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        manager = ProjectConfigManager()

        # Should find project root from subdirectory
        detected_root = manager.detect_project_root(sub_dir)
        assert detected_root.resolve() == project_root.resolve()

        # Should find project root from root itself
        detected_root = manager.detect_project_root(project_root)
        assert detected_root.resolve() == project_root.resolve()


def test_project_config_manager_detect_no_project():
    """Test project detection when no config file exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = ProjectConfigManager()

        # Should return None when no config file found
        detected_root = manager.detect_project_root(Path(temp_dir))
        assert detected_root is None


def test_project_config_file_watching():
    """Test file watching for configuration changes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        config_file = project_path / ".mcpguide.config.json"

        # Create initial config
        initial_config = {"project": "watch-test", "guide": "local:./guide.md"}
        with open(config_file, "w") as f:
            json.dump(initial_config, f)

        manager = ProjectConfigManager()
        callback_called = []

        def config_changed(new_config):
            callback_called.append(new_config)

        # Start watching
        watcher = manager.watch_config(project_path, config_changed)

        # Modify config file
        updated_config = {"project": "watch-test", "guide": "https://example.com/guide.md"}
        with open(config_file, "w") as f:
            json.dump(updated_config, f)

        # Should have called callback (in real implementation)
        # For now, just test that watcher was created
        assert watcher is not None

        # Stop watching
        watcher.stop()


def test_session_integration_with_persistent_config():
    """Test session integration with persistent configuration."""
    from mcpguide.session_tools import SessionManager

    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        config_file = project_path / ".mcpguide.config.json"

        # Create persistent config
        persistent_config = {
            "project": "integration-test",
            "guide": "https://example.com/guide.md",
            "language": "python",
            "tools": ["pytest", "mypy"],
        }

        with open(config_file, "w") as f:
            json.dump(persistent_config, f)

        # Session should load persistent config
        session = SessionManager()
        session.load_project_from_path(project_path)

        # Session should have persistent config values
        project_config = session.session_state.get_project_config("integration-test")
        assert project_config["guide"] == "https://example.com/guide.md"
        assert project_config["language"] == "python"
        assert project_config["tools"] == ["pytest", "mypy"]


def test_save_session_to_persistent_config():
    """Test saving session configuration to persistent file."""
    from mcpguide.session_tools import SessionManager

    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)

        # Configure session
        session = SessionManager()
        session.set_current_project("save-session-test")
        session.session_state.set_project_config("save-session-test", "guide", "local:./guide.md")
        session.session_state.set_project_config("save-session-test", "language", "typescript")
        session.session_state.set_project_config("save-session-test", "tools", ["eslint", "jest"])

        # Save session to persistent config
        manager = ProjectConfigManager()
        manager.save_session_config(project_path, session, "save-session-test")

        # Check file was created with correct content
        config_file = project_path / ".mcpguide.config.json"
        assert config_file.exists()

        with open(config_file) as f:
            saved_data = json.load(f)

        # Should contain the session-specific config
        assert saved_data["project"] == "save-session-test"
        assert saved_data["guide"] == "local:./guide.md"
        assert saved_data["language"] == "typescript"
        assert saved_data["tools"] == ["eslint", "jest"]


def test_config_precedence():
    """Test configuration precedence: session overrides > file config > defaults."""
    from mcpguide.session_tools import SessionManager

    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        config_file = project_path / ".mcpguide.config.json"

        # Create persistent config
        persistent_config = {
            "project": "precedence-test",
            "guide": "https://example.com/guide.md",
            "language": "python",
        }

        with open(config_file, "w") as f:
            json.dump(persistent_config, f)

        session = SessionManager()

        # Load persistent config
        session.load_project_from_path(project_path)

        # Session override should take precedence
        session.session_state.set_project_config("precedence-test", "language", "typescript")

        # Get effective config should show session override
        effective_config = session.get_effective_config("precedence-test")
        assert effective_config["guide"] == "https://example.com/guide.md"  # From file
        assert effective_config["language"] == "typescript"  # Session override
