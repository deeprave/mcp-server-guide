#!/usr/bin/env python3
"""Debug tests for ClientPath MCP integration."""

import asyncio
import sys

# Add src to path
sys.path.insert(0, "src")


async def test_client_path_in_mcp_context():
    """Test ClientPath within proper MCP context."""
    from mcp_server_guide.server import mcp
    from mcp_server_guide.client_path import ClientPath

    print("=== Testing ClientPath in MCP Context ===")

    # Create a test tool that uses ClientPath
    @mcp.tool()
    async def debug_client_path() -> str:
        try:
            print("Inside MCP tool context...")

            # Test getting context
            context = mcp.get_context()
            print(f"Context: {context}")
            print(f"Session: {context.session}")

            # Test ClientPath
            roots = await ClientPath._request_client_roots()
            print(f"Roots: {roots}")

            primary = await ClientPath.get_primary_root()
            print(f"Primary root: {primary}")

            return f"Success: {len(roots)} roots, primary: {primary}"

        except Exception as e:
            print(f"Error in tool: {e}")
            import traceback

            traceback.print_exc()
            return f"Error: {e}"

    # Test calling the tool (this should provide MCP context)
    try:
        result = await mcp.call_tool("debug_client_path", {})
        print(f"Tool result: {result}")
        return True
    except Exception as e:
        print(f"Tool call error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_current_project_manager():
    """Test CurrentProjectManager directory resolution."""
    from mcp_server_guide.current_project_manager import CurrentProjectManager

    print("\n=== Testing CurrentProjectManager ===")

    manager = CurrentProjectManager()

    # Test directory property
    try:
        directory = manager.directory
        print(f"Directory: {directory}")
    except Exception as e:
        print(f"Directory error: {e}")
        import traceback

        traceback.print_exc()

    # Test current project
    try:
        project = manager.get_current_project()
        print(f"Current project: {project}")
    except Exception as e:
        print(f"Current project error: {e}")


async def test_session_manager():
    """Test SessionManager current project resolution."""
    from mcp_server_guide.session_tools import SessionManager

    print("\n=== Testing SessionManager ===")

    session = SessionManager()

    # Test get_current_project
    try:
        project = session.get_current_project()
        print(f"Session current project: {project}")
    except Exception as e:
        print(f"Session current project error: {e}")

    # Test get_current_project_safe
    try:
        project_safe = session.get_current_project_safe()
        print(f"Session current project safe: {project_safe}")
    except Exception as e:
        print(f"Session current project safe error: {e}")


async def main():
    """Run all debug tests."""
    print("Starting ClientPath debug tests...")

    # Test 1: MCP context
    success1 = await test_client_path_in_mcp_context()

    # Test 2: CurrentProjectManager
    await test_current_project_manager()

    # Test 3: SessionManager
    await test_session_manager()

    print(f"\nMCP context test passed: {success1}")


if __name__ == "__main__":
    asyncio.run(main())
