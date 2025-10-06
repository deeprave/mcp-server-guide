"""Tests for ClientPath - TDD implementation."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, Mock
from mcp.types import Root

from src.mcp_server_guide.client_path import ClientPath


class TestClientPath:
    """Test suite for ClientPath static methods."""

    def setup_method(self):
        """Reset ClientPath state before each test."""
        ClientPath._primary_root = None
        ClientPath._initialized = False

    def teardown_method(self):
        """Clean up ClientPath state after each test."""
        ClientPath._primary_root = None
        ClientPath._initialized = False

    def test_get_primary_root_returns_first_client_directory(self):
        """Test that get_primary_root returns the primary client working directory."""
        # Mock initialized state with test root
        ClientPath._initialized = True
        ClientPath._primary_root = Path("/Users/test/project1")

        result = ClientPath.get_primary_root()

        assert isinstance(result, Path)
        assert str(result) == "/Users/test/project1"

    def test_list_roots_returns_all_client_directories(self):
        """Test that list_roots returns the client working directory."""
        # Mock initialized state with test root
        ClientPath._initialized = True
        ClientPath._primary_root = Path("/Users/test/project1")

        result = ClientPath.list_roots()

        assert isinstance(result, list)
        assert len(result) == 1
        assert all(isinstance(root, Path) for root in result)
        expected_paths = [Path("/Users/test/project1")]
        assert result == expected_paths

    def test_get_primary_root_handles_no_roots_gracefully(self):
        """Test that get_primary_root handles case when client has no root."""
        # Mock initialized state with no root
        ClientPath._initialized = True
        ClientPath._primary_root = None

        result = ClientPath.get_primary_root()
        assert result is None

    def test_get_primary_root_handles_initialization_failure(self, monkeypatch):
        """Test that get_primary_root handles initialization failure gracefully."""
        # Simulate initialize raising an exception
        monkeypatch.setattr(ClientPath, "initialize", Mock(side_effect=RuntimeError("Initialization failed")))
        ClientPath._initialized = False
        ClientPath._primary_root = None

        result = ClientPath.get_primary_root()
        assert result is None

    @pytest.mark.asyncio
    async def test_mcp_roots_protocol_communication(self):
        """Test that ClientPath initializes via MCP roots/list protocol."""
        # Mock MCP session with roots capability
        mock_session = Mock()
        mock_session.client_params = Mock()
        mock_session.client_params.capabilities = Mock()
        mock_session.client_params.capabilities.roots = True

        mock_result = Mock()
        mock_result.roots = [
            Root(uri="file:///Users/test/project1", name="Project 1"),
        ]
        mock_session.list_roots = AsyncMock(return_value=mock_result)

        # Test initialization
        await ClientPath.initialize(mock_session)

        # Verify initialization worked via roots
        assert ClientPath._initialized is True
        assert ClientPath._primary_root == Path("/Users/test/project1")

        # Test that methods now work
        result = ClientPath.list_roots()
        expected_paths = [Path("/Users/test/project1")]
        assert result == expected_paths

    def test_not_initialized_returns_none(self):
        """Test that methods return None/empty when not initialized (lazy initialization)."""
        # Should return None gracefully when not initialized
        assert ClientPath.get_primary_root() is None
        assert ClientPath.list_roots() == []

    @pytest.mark.asyncio
    async def test_initialization_with_fallback_to_cwd(self, monkeypatch):
        """Test initialization fallback to os.getcwd() when roots and PWD not available."""
        # Mock session without roots capability
        mock_session = Mock()
        mock_session.client_params = Mock()
        mock_session.client_params.capabilities = Mock()
        mock_session.client_params.capabilities.roots = None

        # Remove PWD from environment
        monkeypatch.delenv("PWD", raising=False)

        # Mock os.getcwd() to return test directory
        test_cwd = "/Users/test/working-dir"
        monkeypatch.setattr("os.getcwd", lambda: test_cwd)

        # Test initialization
        await ClientPath.initialize(mock_session)

        # Verify initialization worked via CWD fallback
        assert ClientPath._initialized is True
        assert ClientPath._primary_root == Path(test_cwd).resolve()

    @pytest.mark.asyncio
    async def test_initialization_with_pwd_environment(self, monkeypatch):
        """Test initialization via PWD environment variable when roots not available."""
        # Mock session without roots capability
        mock_session = Mock()
        mock_session.client_params = Mock()
        mock_session.client_params.capabilities = Mock()
        mock_session.client_params.capabilities.roots = None

        # Set PWD environment variable
        test_pwd = "/Users/test/from-pwd"
        monkeypatch.setenv("PWD", test_pwd)

        # Mock os.getcwd() to return different directory
        monkeypatch.setattr("os.getcwd", lambda: "/Users/test/from-cwd")

        # Test initialization
        await ClientPath.initialize(mock_session)

        # Verify PWD was used, not CWD
        assert ClientPath._initialized is True
        assert ClientPath._primary_root == Path(test_pwd).resolve()

    @pytest.mark.asyncio
    async def test_initialization_prefers_roots_over_pwd(self, monkeypatch):
        """Test that MCP roots are preferred over PWD and CWD fallbacks."""
        # Mock session with roots capability
        mock_session = Mock()
        mock_session.client_params = Mock()
        mock_session.client_params.capabilities = Mock()
        mock_session.client_params.capabilities.roots = True

        mock_result = Mock()
        mock_result.roots = [
            Root(uri="file:///Users/test/from-roots", name="From Roots"),
        ]
        mock_session.list_roots = AsyncMock(return_value=mock_result)

        # Set PWD environment variable
        monkeypatch.setenv("PWD", "/Users/test/from-pwd")

        # Mock os.getcwd() to return different directory
        monkeypatch.setattr("os.getcwd", lambda: "/Users/test/from-cwd")

        # Test initialization
        await ClientPath.initialize(mock_session)

        # Verify roots was used, not PWD or CWD
        assert ClientPath._initialized is True
        assert ClientPath._primary_root == Path("/Users/test/from-roots")

    def test_file_uri_parsing(self):
        """Test that file:// URIs are correctly parsed to Path objects."""
        test_uri = "file:///Users/test/my-project"
        result = ClientPath._parse_file_uri(test_uri)

        assert isinstance(result, Path)
        assert str(result) == "/Users/test/my-project"

    def test_invalid_uri_handling(self):
        """Test that non-file:// URIs are rejected."""
        with pytest.raises(ValueError, match="URI must start with file://"):
            ClientPath._parse_file_uri("http://example.com/path")

    def test_malformed_uri_edge_cases(self):
        """Test comprehensive edge cases for URI parsing."""
        malformed_uris = [
            "",  # Empty string
            "file:",  # Missing slashes
            "file:/",  # Single slash
            "file://",  # No path
            "ftp://example.com/path",  # Wrong scheme
            "file:///",  # Root only
            None,  # None value
        ]

        for uri in malformed_uris:
            if uri is None:
                with pytest.raises((ValueError, TypeError)):
                    ClientPath._parse_file_uri(uri)
            elif not uri or not uri.startswith("file://"):
                with pytest.raises(ValueError):
                    ClientPath._parse_file_uri(uri)
            else:
                # Valid file:// URIs should work
                try:
                    result = ClientPath._parse_file_uri(uri)
                    assert isinstance(result, Path)
                except ValueError:
                    # Some edge cases may still be invalid
                    pass
