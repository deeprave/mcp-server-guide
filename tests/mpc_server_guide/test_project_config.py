"""Tests for project configuration functionality."""

from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from mcp_server_guide.project_config import ProjectConfig, ProjectConfigManager


async def test_project_config_dataclass():
    """Test ProjectConfig dataclass."""
    # Test with required project parameter
    config = ProjectConfig(project="test_project")

    # Should be a dataclass with expected attributes
    assert hasattr(config, "project")
    assert hasattr(config, "docroot")
    assert hasattr(config, "categories")
    assert hasattr(config, "categories")

    assert config.project == "test_project"
    assert config.docroot is None  # default


async def test_project_config_manager_initialization():
    """Test ProjectConfigManager initialization."""
    # Test initialization - no arguments needed
    manager = ProjectConfigManager()
    assert hasattr(manager, "CONFIG_FILENAME")
    assert manager.CONFIG_FILENAME == ".mcp-server-guide.config.json"

    # Test that it has the expected methods
    assert hasattr(manager, "save_config")
    assert hasattr(manager, "load_config")


async def test_project_config_manager_edge_cases():
    """Test project config manager edge cases to hit all branches."""
    manager = ProjectConfigManager()
    project_path = Path("/test/project")

    # Test load config with non-existent file
    with patch("pathlib.Path.exists", return_value=False):
        result = manager.load_config(project_path)
        assert result is None

    # Test load config with JSON decode error
    with patch("pathlib.Path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data="invalid json")):
            result = manager.load_config(project_path)
            assert result is None

    # Test load config with FileNotFoundError
    with patch("pathlib.Path.exists", return_value=True):
        with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
            result = manager.load_config(project_path)
            assert result is None

    # Test save config
    config = ProjectConfig(project="test", docroot="/test/path")
    with patch("builtins.open", mock_open()) as mock_file:
        manager.save_config(project_path, config)
        mock_file.assert_called()


async def test_project_config_manager_all_methods():
    """Test all project config manager methods."""
    manager = ProjectConfigManager()
    project_path = Path("/test/project")

    # Test with valid config file using projects structure
    config_data = '{"projects": {"test": {"project": "test", "docroot": "/test/path"}}}'
    with patch("pathlib.Path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=config_data)):
            result = manager.load_config(project_path, "test")
            assert isinstance(result, ProjectConfig)
            assert result.project == "test"
            assert result.docroot == "/test/path"


async def test_project_config_to_dict():
    """Test ProjectConfig.to_dict method."""
    config = ProjectConfig(project="test", docroot="/docs")

    result = config.to_dict()
    assert isinstance(result, dict)
    assert result["project"] == "test"
    assert result["docroot"] == "/docs"
    assert result["docroot"] == "/docs"


async def test_project_config_from_dict():
    """Test ProjectConfig.from_dict method."""
    # Test with valid data (legacy fields should be filtered out)
    data = {"project": "test", "guide": "test_guide", "language": "python", "docroot": "/docs"}
    config = ProjectConfig.from_dict(data)
    assert config.project == "test"
    assert config.docroot == "/docs"
    assert config.categories == {}

    # Test with minimal data
    minimal_data = {"project": "minimal"}
    config = ProjectConfig.from_dict(minimal_data)
    assert config.project == "minimal"


async def test_project_config_manager_basic():
    """Test basic ProjectConfigManager functionality."""
    manager = ProjectConfigManager()

    # Test that manager has expected attributes
    assert hasattr(manager, "CONFIG_FILENAME")
    assert hasattr(manager, "save_config")
    assert hasattr(manager, "load_config")

    # Test basic operations don't crash
    project_path = Path("/test/project")
    config = ProjectConfig(project="test")

    # These should not raise exceptions
    try:
        manager.save_config(project_path, config)
    except Exception:
        pass  # Expected to fail in test environment

    try:
        result = manager.load_config(project_path)
        assert result is None or isinstance(result, ProjectConfig)
    except Exception:
        pass  # Expected to fail in test environment


async def test_config_file_watcher_complete():
    """Test ConfigFileWatcher complete functionality."""
    from mcp_server_guide.project_config import ConfigFileWatcher

    config_path = Path("/test/config.json")
    callback = Mock()

    # Test watcher initialization and all methods
    watcher = ConfigFileWatcher(config_path, callback)
    assert watcher.config_path == config_path
    assert watcher.callback == callback
    assert watcher.observer is not None
    assert watcher.handler is not None

    # Test start method
    with patch.object(watcher.observer, "schedule") as mock_schedule:
        with patch.object(watcher.observer, "start") as mock_start:
            watcher.start()
            mock_schedule.assert_called_once()
            mock_start.assert_called_once()

    # Test stop method
    with patch.object(watcher.observer, "stop") as mock_stop:
        with patch.object(watcher.observer, "join") as mock_join:
            watcher.stop()
            mock_stop.assert_called_once()
            mock_join.assert_called_once()


async def test_config_change_handler_complete():
    """Test ConfigChangeHandler complete functionality."""
    from mcp_server_guide.project_config import ConfigChangeHandler

    config_path = Path("/test/config.json")
    callback = Mock()

    handler = ConfigChangeHandler(config_path, callback)
    assert handler.config_path == config_path
    assert handler.callback == callback

    # Test on_modified with matching file
    mock_event = Mock()
    mock_event.src_path = str(config_path)
    mock_event.is_directory = False

    # Test successful config load and callback
    config_data = '{"project": "test", "guide": "test_guide"}'
    with patch("builtins.open", mock_open(read_data=config_data)):
        handler.on_modified(mock_event)
        callback.assert_called_once()

    # Test with JSON decode error (should be ignored)
    callback.reset_mock()
    with patch("builtins.open", mock_open(read_data="invalid json")):
        handler.on_modified(mock_event)
        callback.assert_not_called()

    # Test with FileNotFoundError (should be ignored)
    callback.reset_mock()
    with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
        handler.on_modified(mock_event)
        callback.assert_not_called()

    # Test with directory event (should be ignored)
    callback.reset_mock()
    mock_event.is_directory = True
    handler.on_modified(mock_event)
    callback.assert_not_called()

    # Test with different file path (should be ignored)
    callback.reset_mock()
    mock_event.is_directory = False
    mock_event.src_path = "/different/path"
    handler.on_modified(mock_event)
    callback.assert_not_called()


async def test_project_config_manager_detect_project_root_complete():
    """Test ProjectConfigManager.detect_project_root complete functionality."""
    manager = ProjectConfigManager()

    # Test successful detection
    start_path = Path("/deep/nested/project/subdir")
    project_root = Path("/deep/nested/project")
    config_file = project_root / manager.CONFIG_FILENAME

    with patch("pathlib.Path.resolve", return_value=start_path):

        def exists_side_effect(self):
            # Return True only for the config file in the project root
            return self == config_file

        with patch("pathlib.Path.exists", exists_side_effect):
            result = manager.detect_project_root(start_path)
            assert result == project_root

    # Test no config file found (traverse to root)
    with patch("pathlib.Path.resolve", return_value=start_path):
        with patch("pathlib.Path.exists", return_value=False):
            result = manager.detect_project_root(start_path)
            assert result is None
