"""MCP prompt handlers for the developer guide system."""

from typing import Optional
from mcp.server.fastmcp import FastMCP
from .tools.content_tools import get_content


async def execute_prompt_with_guide(
    prompt_name: str,
    base_response: str,
    user_arg: Optional[str] = None,
    pre_text: Optional[str] = None,
    content: Optional[str] = None,
) -> str:
    """Execute prompt and use guide content if available, otherwise fallback to base response."""
    guide_content = await get_content("prompt", prompt_name)

    # Choose primary content
    primary_content = guide_content or base_response
    # Add user arg if provided
    if pre_text:
        primary_content = f"{pre_text}\n{primary_content}"
    if user_arg:
        primary_content = f"{primary_content}\n🎯 Focus: {user_arg}"

    # Add additional content if provided and not empty/whitespace
    if content and content.strip():
        primary_content = f"{primary_content}\n📄 **Additional Content:**\n{content.strip()}"

    return primary_content


async def status_prompt(arg: Optional[str] = None) -> str:
    """Show current mode status - client must check files."""
    base_response = """📋 **Status Check**
- If `.consent` file exists
    → .consent contains 'check' → CHECK mode
    → otherwise → IMPLEMENTATION mode
    → if '.issue' file exists → content is the current issue
- Otherwise
    → if `.issue` file exists and is non empty → PLAN mode
    → otherwise → DISCUSSION mode
"""
    return await execute_prompt_with_guide("status", base_response, arg)


async def discuss_prompt(arg: Optional[str] = None, content: Optional[str] = None) -> str:
    """Enter discuss mode for ideation, concepts, and exploration."""
    pre_text = """☑️ **Required Actions:**
- Remove `.consent` file (if it exists)
- If `.issue` file exists, ask the user if they wish to remove it (and do so if confirmed)
"""
    base_response = """💬 **Discussion Mode Instructions**
**Mode Capabilities:**
📍 Current step: Ideation and conceptual exploration
  - Brainstorm ideas, explore concepts, analyze requirements, discuss architecture
  - You may NOT make code changes, create files, implement solutions other than plans, specifications, or checklists

🔄 **Next Step:** plan when ready for concrete planning
📍 Next step will be PLANNING and task and specification creation
  - You will still not be able to make code changes"""

    return await execute_prompt_with_guide("discuss", base_response, arg, pre_text, content)


async def plan_prompt(arg: Optional[str] = None) -> str:
    """Enter plan mode for concrete planning and specification creation."""
    pre_text = """☑️ **Required Actions:**
- Remove `.consent` file (if it exists)
- Create empty `.issue` file (if it doesn't already exist)
- Add paths of documents created during planning to the `.issue` file
"""
    base_response = """✅ **Plan Mode Instructions**
**Mode Capabilities:**
📍 Current step: Concrete planning and specification creation
  - You may create task specifications, design documents, implementation plans, analyze and gather requirements
  - You may NOT make code changes or implement solutions

🔄 **Next Step:** IMPLEMENTATION (requires user consent)"""

    return await execute_prompt_with_guide("plan", base_response, arg, pre_text)


async def implement_prompt(arg: Optional[str] = None, content: Optional[str] = None) -> str:
    """Enter implementation mode for code changes and implementation activities."""
    pre_text = """☑️ **Required Actions:**
- Create `.consent` file with content: `implementation`
"""
    base_response = """⚙️ **Implementation Mode Instructions**
**Mode Capabilities:**
📍 Current step: Implementation and code changes
  - You may create, modify and remove files, write code, implement solutions, make architectural changes as planned
  - You may not ignore quality requirements or bypass validation
  - You must implement features completely as specified in plans and specifications

🔄 **Next Step:** CHECK when ready for verification (update .consent file content to 'check')"""

    return await execute_prompt_with_guide("implement", base_response, arg, pre_text, content)


async def check_prompt(arg: Optional[str] = None, content: Optional[str] = None) -> str:
    """Enter check mode for verification and cleanup activities."""
    pre_text = """☑️ **Required Actions:**
- Update `.consent` file content to: `check`
"""
    base_response = """🔍 **Check Mode Instructions**
**Mode Capabilities:**
📍 Current step: Verification and quality assurance
  - You MUST Run tests, use code quality tools, validate the implementation, run linting/formatting
  - You may NOT make further code changes except to fix errors, modify implementation, alter functionality

📋 **Verification Checklist:**
  * Test suite execution
  * Code linting
  * Format checking
  * Type checking

🔄 **Next Step:** DISCUSSION - return to discussion mode (discuss/plan)"""

    return await execute_prompt_with_guide("check", base_response, arg, pre_text, content)


def register_prompts(mcp: FastMCP) -> None:
    """Register all prompt handlers with the MCP server."""

    # Make registration idempotent per MCP instance
    if getattr(mcp, "_prompts_registered", False):
        return
    setattr(mcp, "_prompts_registered", True)

    @mcp.prompt("status")
    async def _status_prompt(arg: Optional[str] = None) -> str:
        return await status_prompt(arg)

    @mcp.prompt("plan")
    async def _plan_prompt(arg: Optional[str] = None) -> str:
        return await plan_prompt(arg)

    @mcp.prompt("discuss")
    async def _discuss_prompt(arg: Optional[str] = None, content: Optional[str] = None) -> str:
        return await discuss_prompt(arg, content)

    @mcp.prompt("implement")
    async def _implement_prompt(arg: Optional[str] = None, content: Optional[str] = None) -> str:
        return await implement_prompt(arg, content)

    @mcp.prompt("check")
    async def _check_prompt(arg: Optional[str] = None, content: Optional[str] = None) -> str:
        return await check_prompt(arg, content)

    @mcp.prompt("debug")
    async def _debug_prompt(arg: Optional[str] = None, content: Optional[str] = None) -> str:
        return f"arg: '{arg}'\ncontent: '{content}'\narg type: {type(arg)}\ncontent type: {type(content)}"
