"""MCP prompt handlers for the developer guide system."""

from typing import Optional
from mcp.server.fastmcp import FastMCP
from .tools.content_tools import get_content


async def execute_prompt_with_guide(
    prompt_name: str, base_response: str, user_arg: Optional[str] = None, pre_text: Optional[str] = None
) -> str:
    """Execute prompt and use guide content if available, otherwise fallback to base response."""
    guide_content = await get_content("prompt", prompt_name)

    # Choose primary content
    if guide_content:
        primary_content = guide_content
    else:
        primary_content = base_response

    # Add user arg if provided
    if pre_text:
        primary_content = f"{pre_text}\n\n{primary_content}"
    if user_arg:
        primary_content = f"{primary_content}\n\n🎯 Focus: {user_arg}"
    return primary_content


async def status_prompt(arg: Optional[str] = None) -> str:
    """Show current mode status - client must check files."""
    base_response = """📋 **Status Check**
- If `.consent` file exists
    → .consent contains 'check' → CHECK mode
    → otherwise → IMPLEMENTATION mode
- Otherwise
    → if `.issue` file exists → PLAN mode
    → otherwise → DISCUSSION mode
"""
    return await execute_prompt_with_guide("status", base_response, arg)


async def discuss_prompt(arg: Optional[str] = None) -> str:
    """Enter discuss mode for ideation, concepts, and exploration."""
    pre_text = """☑️ **Required Actions:**
- Remove `.consent` file (if it exists)
- Remove `.issue` file (if it exists)
"""
    base_response = """✅ **Discuss Mode Instructions**
**Mode Capabilities:**
📍 Current step: Ideation and conceptual exploration
  - AI agent can: Brainstorm ideas, explore concepts, analyze requirements, discuss architecture
  - AI agent cannot: Make code changes, create files, implement solutions

🔄 **Next Step:** Use @plan when ready for concrete planning
📍 Next step will be: Concrete planning and specification creation
  - AI agent will be able to: Create task specifications, design documents, implementation plans
  - AI agent will not be able to: Make code changes"""

    return await execute_prompt_with_guide("discuss", base_response, arg, pre_text)


async def plan_prompt(arg: Optional[str] = None) -> str:
    """Enter plan mode for concrete planning and specification creation."""
    pre_text = """☑️ **Required Actions:**
- Remove `.consent` file (if it exists)
- Create empty `.issue` file (if it doesn't exist)
"""
    base_response = """✅ **Plan Mode Instructions**
**Mode Capabilities:**
📍 Current step: Concrete planning and specification creation
  - AI agent can: Create task specifications, design documents, implementation plans, analyze requirements
  - AI agent cannot: Make code changes, modify existing files, implement solutions

🔄 **Next Step:** Use @implement when ready for implementation (requires user consent)"""

    return await execute_prompt_with_guide("plan", base_response, arg, pre_text)


async def implement_prompt(arg: Optional[str] = None) -> str:
    """Enter implementation mode for code changes and implementation activities."""
    pre_text = """☑️ **Required Actions:**
- Create `.consent` file with content: `implementation`
"""
    base_response = """⚙️ **Implementation Mode Instructions**
**Mode Capabilities:**
📍 Current step: Implementation and code changes
  - AI agent can: Create/modify files, write code, implement solutions, make architectural changes
  - AI agent cannot: Skip testing, ignore quality requirements, bypass validation

🔄 **Next Step:** Use @check when ready for verification (update .consent file content to 'check')
📍 Next step will be: Verification and quality assurance
  - AI agent will be able to: Run tests, check code quality, validate implementation
  - AI agent will not be able to: Make further code changes, modify implementation"""

    return await execute_prompt_with_guide("implement", base_response, arg, pre_text)


async def check_prompt(arg: Optional[str] = None) -> str:
    """Enter check mode for verification and cleanup activities."""
    pre_text = """☑️ **Required Actions:**
- Update `.consent` file content to: `check`
"""
    base_response = """🔍 **Check Mode Instructions**
**Mode Capabilities:**
📍 Current step: Verification and quality assurance
  - AI agent can: Run tests, check code quality, validate implementation, run linting/formatting
  - AI agent cannot: Make code changes, modify implementation, alter functionality

🔄 **Next Step:** Remove `.consent` file when all checks pass and user approves
  - Next step will be: Return to planning mode (discuss/plan)
  - AI agent will be able to: Discuss concepts, create plans, analyze requirements
  - AI agent will not be able to: Make code changes, implement solutions

📋 **Verification Checklist:**
  * Test suite execution
  * Coverage analysis
  * Code linting
  * Format checking
  * Type checking"""

    return await execute_prompt_with_guide("check", base_response, arg, pre_text)


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
    async def _discuss_prompt(arg: Optional[str] = None) -> str:
        return await discuss_prompt(arg)

    @mcp.prompt("implement")
    async def _implement_prompt(arg: Optional[str] = None) -> str:
        return await implement_prompt(arg)

    @mcp.prompt("check")
    async def _check_prompt(arg: Optional[str] = None) -> str:
        return await check_prompt(arg)
