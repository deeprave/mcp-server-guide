#!/usr/bin/env python3
"""Fixed test for ClientPath with proper mocking."""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add src to path
sys.path.insert(0, "src")


async def test_client_path_with_proper_mock():
    """Test ClientPath with properly mocked MCP context."""
    from mcp.types import ListRootsResult, Root

    print("=== Testing ClientPath with Proper Mock ===")

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
        mock_mcp = MagicMock()
        mock_mcp.get_context.return_value = mock_context

        # Patch the import in ClientPath
        with patch.dict("sys.modules", {"mcp_server_guide.server": MagicMock(mcp=mock_mcp)}):
            from mcp_server_guide.client_path import ClientPath

            # Test ClientPath with mocked context
            roots = await ClientPath._request_client_roots()
            print(f"Mocked roots: {roots}")
            print(f"Roots type: {type(roots)}")
            print(f"First root: {roots[0] if roots else 'None'}")

            primary = await ClientPath.get_primary_root()
            print(f"Mocked primary root: {primary}")
            print(f"Primary type: {type(primary)}")

            return len(roots) > 0 and primary is not None

    except Exception as e:
        print(f"Mocked context error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_current_project_manager_with_mock():
    """Test CurrentProjectManager with mocked ClientPath."""
    print("\n=== Testing CurrentProjectManager with Mock ===")

    try:
        # Mock ClientPath to return a test directory
        test_dir = Path("/tmp/test-project")

        with patch("mcp_server_guide.current_project_manager.ClientPath") as mock_client_path:
            mock_client_path.get_primary_root.return_value = asyncio.create_task(asyncio.coroutine(lambda: test_dir)())

            from mcp_server_guide.current_project_manager import CurrentProjectManager

            manager = CurrentProjectManager()

            # Test directory property
            directory = manager.directory
            print(f"Mocked directory: {directory}")

            # Test current project
            project = manager.get_current_project()
            print(f"Mocked current project: {project}")

            return directory is not None

    except Exception as e:
        print(f"CurrentProjectManager mock error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_session_manager_with_mock():
    """Test SessionManager with mocked CurrentProjectManager."""
    print("\n=== Testing SessionManager with Mock ===")

    try:
        # Mock CurrentProjectManager to return a test project
        test_project = "test-project"

        with patch("mcp_server_guide.session_tools.CurrentProjectManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.get_current_project.return_value = test_project
            mock_manager_class.return_value = mock_manager

            from mcp_server_guide.session_tools import SessionManager

            session = SessionManager()

            # Test get_current_project
            project = session.get_current_project()
            print(f"Mocked session project: {project}")

            # Test get_current_project_safe
            project_safe = session.get_current_project_safe()
            print(f"Mocked session project safe: {project_safe}")

            return project == test_project and project_safe == test_project

    except Exception as e:
        print(f"SessionManager mock error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_guide_prompt_with_full_mock():
    """Test the @guide prompt with full mocking chain."""
    print("\n=== Testing @guide Prompt with Full Mock ===")

    try:
        test_project = "test-project"

        # Mock the entire chain
        with patch("mcp_server_guide.session_tools.CurrentProjectManager") as mock_manager_class:
            mock_manager = MagicMock()
            mock_manager.get_current_project.return_value = test_project
            mock_manager_class.return_value = mock_manager

            # Import and test the guide prompt
            from mcp_server_guide.server import guide_prompt

            # Test guide prompt
            result = await guide_prompt()
            print(f"Guide prompt result: {result}")
            print(f"Result type: {type(result)}")

            return "No guides available" in result or len(result) > 0

    except Exception as e:
        print(f"Guide prompt mock error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all fixed tests."""
    print("Starting fixed ClientPath tests...")

    # Test 1: ClientPath with proper mock
    success1 = await test_client_path_with_proper_mock()

    # Test 2: CurrentProjectManager with mock
    success2 = await test_current_project_manager_with_mock()

    # Test 3: SessionManager with mock
    success3 = await test_session_manager_with_mock()

    # Test 4: Guide prompt with full mock
    success4 = await test_guide_prompt_with_full_mock()

    print("\nResults:")
    print(f"ClientPath mock: {success1}")
    print(f"CurrentProjectManager mock: {success2}")
    print(f"SessionManager mock: {success3}")
    print(f"Guide prompt mock: {success4}")

    if all([success1, success2, success3, success4]):
        print("\n✅ All components work with proper mocking!")
        print("The issue is that ClientPath needs MCP request context to work.")
    else:
        print("\n❌ Some components still have issues")


if __name__ == "__main__":
    asyncio.run(main())
