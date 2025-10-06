#!/usr/bin/env python3
"""Integration test for MCP client-server communication."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, "src")


async def test_mcp_stdio_integration():
    """Test MCP server with simulated stdio client communication."""
    from mcp_server_guide.main import start_mcp_server

    print("=== Testing MCP STDIO Integration ===")

    # Create a mock client working directory
    test_dir = Path("/tmp/test_mcp_client")
    test_dir.mkdir(exist_ok=True)

    # Create minimal config
    config = {
        "config_filename": ".mcp-server-guide.config.json",
        "context": "",
        "contextdir": "context",
        "docroot": "docs",
        "guide": "",
        "guidesdir": "guides",
        "lang": "",
        "langsdir": "langs",
        "log_console": True,
        "log_level": "DEBUG",
    }

    try:
        # Start the MCP server
        print("Starting MCP server...")
        server = start_mcp_server("stdio", config)
        print(f"Server created: {server}")

        # Test if server has the expected methods
        print(f"Server type: {type(server)}")
        print(f"Server methods: {[m for m in dir(server) if not m.startswith('_')]}")

        return True

    except Exception as e:
        print(f"Server start error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_manual_context_simulation():
    """Test by manually creating MCP context simulation."""
    from mcp_server_guide.server import mcp

    print("\n=== Testing Manual Context Simulation ===")

    # Try to understand how to properly test MCP tools
    try:
        # Check if we can access the server's internal state
        print(f"MCP server type: {type(mcp)}")

        # Look for test utilities or ways to simulate context
        mcp_attrs = [
            attr
            for attr in dir(mcp)
            if "test" in attr.lower() or "context" in attr.lower() or "session" in attr.lower()
        ]
        print(f"MCP test/context/session attributes: {mcp_attrs}")

        # Check if there's a way to create a test context
        if hasattr(mcp, "get_context"):
            try:
                context = mcp.get_context()
                print(f"Context outside request: {context}")
            except Exception as e:
                print(f"Context error (expected): {e}")

        return True

    except Exception as e:
        print(f"Manual context error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_with_pytest_fixtures():
    """Test using pytest-style fixtures to mock MCP context."""
    from unittest.mock import AsyncMock, MagicMock, patch
    from mcp.types import ListRootsResult, Root
    from mcp_server_guide.client_path import ClientPath

    print("\n=== Testing with Mocked MCP Context ===")

    try:
        # Create mock roots
        mock_roots = [Root(uri="file:///tmp/test-project", name="Test Project")]
        mock_result = ListRootsResult(roots=mock_roots)

        # Mock the session.list_roots method
        mock_session = AsyncMock()
        mock_session.list_roots.return_value = mock_result

        # Mock the context
        mock_context = MagicMock()
        mock_context.session = mock_session

        # Mock the mcp.get_context method
        with patch("mcp_server_guide.client_path.sys.modules") as mock_modules:
            mock_mcp = MagicMock()
            mock_mcp.get_context.return_value = mock_context

            mock_server_module = MagicMock()
            mock_server_module.mcp = mock_mcp
            mock_modules.__getitem__.return_value = mock_server_module
            mock_modules.__contains__.return_value = True

            # Test ClientPath with mocked context
            roots = await ClientPath._request_client_roots()
            print(f"Mocked roots: {roots}")

            primary = await ClientPath.get_primary_root()
            print(f"Mocked primary root: {primary}")

            return len(roots) > 0 and primary is not None

    except Exception as e:
        print(f"Mocked context error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all integration tests."""
    print("Starting MCP integration tests...")

    # Test 1: STDIO integration
    success1 = await test_mcp_stdio_integration()

    # Test 2: Manual context simulation
    success2 = await test_manual_context_simulation()

    # Test 3: Mocked context
    success3 = await test_with_pytest_fixtures()

    print("\nResults:")
    print(f"STDIO integration: {success1}")
    print(f"Manual context: {success2}")
    print(f"Mocked context: {success3}")

    if success3:
        print("\n✅ ClientPath works with proper MCP context!")
    else:
        print("\n❌ ClientPath still has issues")


if __name__ == "__main__":
    asyncio.run(main())
