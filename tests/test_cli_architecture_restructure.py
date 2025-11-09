"""Tests for CLI architecture restructure - async context race condition fix."""

import pytest
from unittest.mock import patch, AsyncMock
from mcp_server_guide.main import cli_main, start_mcp_server


class TestCurrentBehavior:
    """Test current CLI behavior before restructuring."""

    def test_cli_main_entry_point_exists(self):
        """Test that cli_main entry point exists and is callable."""
        assert callable(cli_main)

    @pytest.mark.asyncio
    async def test_start_mcp_server_is_async(self):
        """Test that start_mcp_server is async function."""
        with patch("mcp_server_guide.server.get_current_server") as mock_get_server:
            mock_server = AsyncMock()
            mock_server.run_stdio_async = AsyncMock()
            mock_get_server.return_value = mock_server

            result = await start_mcp_server("stdio", {"docroot": "."})
            assert "stdio mode" in result

    def test_current_architecture_problem(self):
        """Document the current architectural problem."""
        # Current flow: cli_main() -> asyncio.run(cli_main_async()) -> await main() -> Click command -> complex loop detection
        # This test documents the problem we're fixing
        assert True  # Placeholder for architectural documentation


class TestTargetArchitecture:
    """Test target architecture after restructuring."""

    def test_target_cli_parsing_only(self):
        """Test that CLI parsing should only return config, not start server."""
        # Target: parse_cli_arguments() -> returns config dict
        # This will be implemented in the restructure
        assert True  # Placeholder for future implementation

    def test_new_cli_parsing_function_exists(self):
        """Test that new CLI parsing function exists."""
        from mcp_server_guide.main import parse_cli_arguments

        assert callable(parse_cli_arguments)


class TestPhase2CleanAsyncFlow:
    """Test Phase 2: Clean Async Flow - removing complex loop detection."""

    @pytest.mark.asyncio
    async def test_start_server_with_config_is_clean_async(self):
        """Test that start_server_with_config runs in clean async context."""
        from mcp_server_guide.main import start_server_with_config

        with patch("mcp_server_guide.main.start_mcp_server") as mock_start:
            mock_start.return_value = "Server started"

            config = {"mode": "stdio", "docroot": "."}

            # This should run cleanly without any loop detection complexity
            await start_server_with_config(config)

            # Verify start_mcp_server was called with correct arguments
            mock_start.assert_called_once()
            args, kwargs = mock_start.call_args
            assert args[0] == "stdio"  # mode
            assert isinstance(args[1], dict)  # resolved_config


class TestPhase3ArchitectureVerification:
    """Test Phase 3: Verify Architecture - comprehensive integration tests."""

    def test_entry_point_updated(self):
        """Test that entry point uses new architecture."""
        # Check that pyproject.toml points to cli_main_new
        import os

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pyproject_path = os.path.join(project_root, "pyproject.toml")

        with open(pyproject_path, "r") as f:
            content = f.read()
        assert "cli_main_new" in content
        assert 'mcp-server-guide = "mcp_server_guide.main:cli_main_new"' in content

    def test_new_architecture_separation_of_concerns(self):
        """Test that new architecture properly separates CLI parsing from server startup."""
        from mcp_server_guide.main import parse_cli_arguments, start_server_with_config

        # CLI parsing should be sync and return config
        import inspect

        assert not inspect.iscoroutinefunction(parse_cli_arguments)

        # Server startup should be async
        assert inspect.iscoroutinefunction(start_server_with_config)

    def test_integration_with_mocked_server(self):
        """Test full integration with mocked server startup (sync version)."""
        from mcp_server_guide.main import parse_cli_arguments

        # Test that CLI parsing works correctly
        with patch("sys.argv", ["test", "--docroot", "/custom"]):
            config = parse_cli_arguments()
            assert config["docroot"] == "/custom"
            assert config["mode"] == "stdio"

    def test_old_complex_loop_detection_removed(self):
        """Test that old complex loop detection code is no longer used."""
        from mcp_server_guide.main import cli_main_new, start_server_with_config
        import inspect

        # Check that new functions don't contain complex loop detection
        cli_source = inspect.getsource(cli_main_new)
        server_source = inspect.getsource(start_server_with_config)

        # These patterns should NOT exist in new architecture
        forbidden_patterns = ["get_running_loop()", "ThreadPoolExecutor", "new_event_loop()", "concurrent.futures"]

        for pattern in forbidden_patterns:
            assert pattern not in cli_source, f"Found forbidden pattern '{pattern}' in cli_main_new"
            assert pattern not in server_source, f"Found forbidden pattern '{pattern}' in start_server_with_config"

    def test_single_asyncio_run_architecture(self):
        """Test that architecture has exactly one asyncio.run() call."""
        from mcp_server_guide.main import cli_main_new
        import inspect

        source = inspect.getsource(cli_main_new)
        asyncio_run_count = source.count("asyncio.run(")

        assert asyncio_run_count == 1, f"Expected exactly 1 asyncio.run() call, found {asyncio_run_count}"
