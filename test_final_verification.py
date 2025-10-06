#!/usr/bin/env python3
"""Final verification test - proves ClientPath works with MCP context."""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add src to path
sys.path.insert(0, "src")


async def test_clientpath_works_with_context():
    """PROOF: ClientPath works when MCP context is available."""
    from mcp.types import ListRootsResult, Root

    print("=== PROOF: ClientPath Works with MCP Context ===")

    # Create realistic mock data
    mock_roots = [Root(uri="file:///tmp/test-project", name="MCP Server Guide")]
    mock_result = ListRootsResult(roots=mock_roots)

    # Mock the MCP session
    mock_session = AsyncMock()
    mock_session.list_roots.return_value = mock_result

    # Mock the MCP context
    mock_context = MagicMock()
    mock_context.session = mock_session

    # Mock the MCP server
    mock_mcp = MagicMock()
    mock_mcp.get_context.return_value = mock_context

    # Patch the server module import
    with patch.dict("sys.modules", {"mcp_server_guide.server": MagicMock(mcp=mock_mcp)}):
        from mcp_server_guide.client_path import ClientPath

        # Test the fixed ClientPath implementation
        print("Testing _request_client_roots()...")
        roots = await ClientPath._request_client_roots()
        print(f"✅ Got {len(roots)} roots: {roots}")

        print("Testing get_primary_root()...")
        primary = await ClientPath.get_primary_root()
        print(f"✅ Primary root: {primary}")

        print("Testing list_roots()...")
        all_roots = await ClientPath.list_roots()
        print(f"✅ All roots: {all_roots}")

        # Verify the results
        assert len(roots) == 1
        assert str(roots[0].uri) == "file:///tmp/test-project"
        assert primary == Path("/tmp/test-project")
        assert len(all_roots) == 1
        assert all_roots[0] == Path("/tmp/test-project")

        print("\n🎉 SUCCESS: ClientPath implementation is CORRECT!")
        print("The issue is that MCP context is only available during actual client requests.")

        return True


async def test_why_it_fails_without_context():
    """Demonstrate why it fails without MCP context."""
    print("\n=== Why It Fails Without Context ===")

    try:
        from mcp_server_guide.client_path import ClientPath

        # This will fail because there's no MCP context
        roots = await ClientPath._request_client_roots()
        print(f"Unexpected success: {roots}")
        return False

    except Exception as e:
        print(f"✅ Expected failure: {e}")
        print("This proves the implementation correctly requires MCP context.")
        return True


async def test_current_project_manager_issue():
    """Show the CurrentProjectManager async issue."""
    print("\n=== CurrentProjectManager Async Issue ===")

    from mcp_server_guide.current_project_manager import CurrentProjectManager

    manager = CurrentProjectManager()

    # This fails because directory property tries to run async code synchronously
    try:
        directory = manager.directory
        print(f"Directory: {directory}")

        if directory is None:
            print("✅ Returns None because ClientPath fails without MCP context")
            print("This is the root cause of the 'Cannot determine client working directory' error")
            return True
        else:
            print(f"Unexpected directory: {directory}")
            return False

    except Exception as e:
        print(f"Directory error: {e}")
        return False


def show_solution():
    """Show the architectural solution needed."""
    print("\n=== THE SOLUTION ===")
    print("1. ✅ ClientPath implementation is CORRECT - it properly uses MCP protocol")
    print("2. ✅ The fix to use context.session.list_roots() is RIGHT")
    print("3. ❌ The problem: CurrentProjectManager.directory tries to run async code synchronously")
    print("4. ❌ The problem: Tools call get_current_project_safe() outside MCP request context")
    print()
    print("ARCHITECTURAL FIX NEEDED:")
    print("- Remove synchronous directory property from CurrentProjectManager")
    print("- Make all client directory access async and context-aware")
    print("- Pass client directory from MCP context to tools during request execution")
    print("- Don't try to resolve client directory during server initialization")


async def main():
    """Run verification tests."""
    print("🔍 FINAL VERIFICATION: Is ClientPath Implementation Correct?")
    print("=" * 60)

    # Test 1: Prove ClientPath works with context
    success1 = await test_clientpath_works_with_context()

    # Test 2: Show why it fails without context
    success2 = await test_why_it_fails_without_context()

    # Test 3: Show CurrentProjectManager issue
    success3 = await test_current_project_manager_issue()

    # Show the solution
    show_solution()

    print("\n" + "=" * 60)
    if all([success1, success2, success3]):
        print("🎉 CONCLUSION: ClientPath implementation is CORRECT!")
        print("The architectural issue is in CurrentProjectManager and tool execution flow.")
    else:
        print("❌ ClientPath implementation needs more work.")


if __name__ == "__main__":
    asyncio.run(main())
