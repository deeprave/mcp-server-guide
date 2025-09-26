# Task 013: Remove Unnecessary Tools Configuration Feature

## Problem
The `tools` configuration field in ProjectConfig is dead code that serves no functional purpose:
- Stores a list of strings but doesn't affect MCP server behavior
- All MCP tools are always registered regardless of this setting
- Misleading - suggests it controls tool availability but doesn't
- Adds unnecessary complexity to the configuration

## Solution
Remove the tools configuration feature entirely.

## Implementation Steps

1. **Remove tools field from ProjectConfig dataclass**
   - File: `src/mcp_server_guide/project_config.py`
   - Remove: `tools: Optional[List[str]] = field(default_factory=list)`

2. **Remove get_tools and set_tools functions**
   - File: `src/mcp_server_guide/tools/config_tools.py`
   - Remove: `get_tools()` and `set_tools()` functions

3. **Remove MCP tool registrations**
   - File: `src/mcp_server_guide/server.py`
   - Remove: `@mcp.tool()` decorators and functions for `get_tools` and `set_tools`

4. **Update __all__ exports**
   - File: `src/mcp_server_guide/tools/config_tools.py`
   - File: `src/mcp_server_guide/tools/__init__.py`
   - Remove: `"get_tools"` and `"set_tools"` from exports

5. **Run tests**
   - Ensure no functionality breaks
   - Update any tests that reference the removed functions

## Priority
Low - cleanup/refactoring task, not blocking other work

## Status
Planned - deferred for later cleanup
