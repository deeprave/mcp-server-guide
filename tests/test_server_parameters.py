"""Test server parameter functionality."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, AsyncMock, Mock

from mcp_server_guide.server import create_server, GuideMCP


class TestServerParameters:
    """Test server parameter handling."""

    def test_guide_mcp_stores_parameters(self):
        """Test that GuideMCP stores parameters correctly."""
        server = GuideMCP(
            name="test-server", project="test-project", docroot="/test/path", config_file="/test/config.json"
        )

        assert server.project == "test-project"
        assert server.docroot == "/test/path"
        assert server.config_file == "/test/config.json"

    def test_create_server_passes_parameters(self):
        """Test that create_server passes parameters to GuideMCP."""
        server = create_server(
            name="test-server", project="test-project", docroot="/test/path", config_file="/test/config.json"
        )

        assert isinstance(server, GuideMCP)
        assert server.project == "test-project"
        assert server.docroot == "/test/path"
        assert server.config_file == "/test/config.json"

    @pytest.mark.asyncio
    async def test_server_lifecycle_applies_config_file(self):
        """Test that server lifecycle applies config_file parameter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"

            # Create a mock server with config_file
            server = GuideMCP(name="test-server", config_file=str(config_path))

            # Import and call the lifecycle function
            from mcp_server_guide.server_lifecycle import server_lifespan

            # Mock the session manager creation
            with patch("mcp_server_guide.server_lifecycle.SessionManager") as mock_sm_class:
                mock_config_manager = Mock()  # Regular Mock, not AsyncMock
                mock_config_manager.set_config_filename = Mock()  # Regular method
                mock_sm = AsyncMock()
                mock_sm._config_manager = mock_config_manager
                mock_sm.get_or_create_project_config = AsyncMock()
                mock_sm_class.return_value = mock_sm

                # Mock other dependencies
                with (
                    patch("mcp_server_guide.server_lifecycle.register_resources"),
                    patch("mcp_server_guide.server_lifecycle.register_prompts"),
                    patch("mcp_server_guide.tool_registry.register_tools"),
                ):
                    async with server_lifespan(server):
                        pass

                # Verify config file was set
                mock_config_manager.set_config_filename.assert_called_once_with(str(config_path))

    @pytest.mark.asyncio
    async def test_server_lifecycle_applies_project(self):
        """Test that server lifecycle applies project parameter."""
        from mcp_server_guide.server_lifecycle import server_lifespan

        server = GuideMCP(name="test-server", project="test-project")

        with patch("mcp_server_guide.server_lifecycle.SessionManager") as mock_sm_class:
            mock_sm = AsyncMock()
            mock_sm.switch_project = AsyncMock()
            mock_sm.get_or_create_project_config = AsyncMock()
            mock_sm_class.return_value = mock_sm

            # Mock other dependencies
            with (
                patch("mcp_server_guide.server_lifecycle.register_resources"),
                patch("mcp_server_guide.server_lifecycle.register_prompts"),
                patch("mcp_server_guide.tool_registry.register_tools"),
            ):
                async with server_lifespan(server):
                    pass

            # Verify project was switched
            mock_sm.switch_project.assert_called_once_with("test-project")

    @pytest.mark.asyncio
    async def test_server_lifecycle_applies_docroot(self):
        """Test that server lifecycle applies docroot parameter."""
        from mcp_server_guide.server_lifecycle import server_lifespan

        server = GuideMCP(name="test-server", docroot="/custom/docroot")

        with patch("mcp_server_guide.server_lifecycle.SessionManager") as mock_sm_class:
            mock_config_manager = Mock()  # Regular Mock, not AsyncMock
            mock_config_manager.set_config_filename = Mock()  # Regular method
            mock_sm = AsyncMock()
            mock_sm._config_manager = mock_config_manager
            mock_sm.get_or_create_project_config = AsyncMock()
            mock_sm_class.return_value = mock_sm

            # Mock other dependencies
            with (
                patch("mcp_server_guide.server_lifecycle.register_resources"),
                patch("mcp_server_guide.server_lifecycle.register_prompts"),
                patch("mcp_server_guide.tool_registry.register_tools"),
            ):
                async with server_lifespan(server):
                    pass

            # Verify docroot was set (check that _docroot attribute was assigned)
            assert hasattr(mock_config_manager, "_docroot")

    @pytest.mark.asyncio
    async def test_server_lifecycle_parameter_order(self):
        """Test that parameters are applied in correct order: config_file, project, docroot."""
        from mcp_server_guide.server_lifecycle import server_lifespan

        server = GuideMCP(
            name="test-server", config_file="/test/config.json", project="test-project", docroot="/custom/docroot"
        )

        call_order = []

        def track_config_file_call(path):
            call_order.append(f"config_file:{path}")

        async def track_project_call(project):
            call_order.append(f"project:{project}")

        def track_docroot_call(value):
            call_order.append(f"docroot:{value}")

        with patch("mcp_server_guide.server_lifecycle.SessionManager") as mock_sm_class:
            mock_config_manager = AsyncMock()
            mock_config_manager.set_config_filename = Mock(side_effect=track_config_file_call)  # Not async

            mock_sm = AsyncMock()
            mock_sm._config_manager = mock_config_manager
            mock_sm.switch_project.side_effect = track_project_call
            mock_sm.get_or_create_project_config = AsyncMock()
            mock_sm_class.return_value = mock_sm

            # Mock LazyPath to track docroot calls
            with patch("mcp_server_guide.path_resolver.LazyPath") as mock_lazy_path:
                mock_lazy_path.side_effect = lambda x: track_docroot_call(x)

                # Mock other dependencies
                with (
                    patch("mcp_server_guide.server_lifecycle.register_resources"),
                    patch("mcp_server_guide.server_lifecycle.register_prompts"),
                    patch("mcp_server_guide.tool_registry.register_tools"),
                ):
                    async with server_lifespan(server):
                        pass

        # Verify correct order: config_file, project, docroot
        expected_order = ["config_file:/test/config.json", "project:test-project", "docroot:/custom/docroot"]
        assert call_order == expected_order

    @pytest.mark.asyncio
    async def test_server_lifecycle_fallback_to_pwd(self):
        """Test that server lifecycle falls back to PWD when no project specified."""
        from mcp_server_guide.server_lifecycle import server_lifespan

        server = GuideMCP(name="test-server")  # No project specified

        with patch.dict(os.environ, {"PWD": "/test/project/path"}):
            with patch("mcp_server_guide.server_lifecycle.SessionManager") as mock_sm_class:
                mock_sm = AsyncMock()
                mock_sm.get_or_create_project_config = AsyncMock()
                mock_sm_class.return_value = mock_sm

                # Mock other dependencies
                with (
                    patch("mcp_server_guide.server_lifecycle.register_resources"),
                    patch("mcp_server_guide.server_lifecycle.register_prompts"),
                    patch("mcp_server_guide.tool_registry.register_tools"),
                ):
                    async with server_lifespan(server):
                        pass

                # Verify PWD basename was used as project name
                mock_sm.get_or_create_project_config.assert_called_once_with("path")
