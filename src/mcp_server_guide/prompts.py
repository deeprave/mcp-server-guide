"""MCP prompt handlers for the developer guide system."""

import json
import re
from typing import Optional, Dict, Any

from mcp.server.fastmcp import FastMCP, Context

from .http.secure_client import SecureHTTPClient
from .exceptions import NetworkError, SecurityError
from .logging_config import get_logger
from .services.speckit_manager import enable_speckit, is_speckit_enabled, update_speckit_config, get_speckit_config

# Category tools are now accessed through guide integration
from .tools.content_tools import get_content

logger = get_logger(__name__)


async def execute_prompt_with_guide(
    prompt_name: str,
    base_response: str,
    user_arg: Optional[str] = None,
    pre_text: Optional[str] = None,
    content: Optional[str] = None,
) -> str:
    """Execute prompt and use guide content if available, otherwise fallback to base response."""
    logger.debug(f"""execute_prompt_with_guide called:
      prompt: {prompt_name}
    user_arg: {repr(user_arg)}
    pre_text: {repr(pre_text)}
     content: {repr(content)}""")

    guide_content = await get_content("prompt", prompt_name)
    logger.debug(f"  guide_content length: {len(guide_content) if guide_content else 0}")

    # Choose primary content
    primary_content = guide_content or base_response

    # Add user arg if provided
    if pre_text:
        primary_content = f"{pre_text}\n{primary_content}"

    if user_arg:
        primary_content = f"{primary_content}\n\n**Focus**: {user_arg}\n\n"

    # Add additional content if provided and not empty/whitespace
    if content and content.strip():
        primary_content = f"{primary_content}\n📄 **Additional Content:**\n{content.strip()}"

    return primary_content


async def status_prompt(arg: Optional[str] = None) -> str:
    """Show current mode status - client must check files."""
    pre_text = None
    if arg:
        pre_text = f"""🎯 **Focus:**
- {arg}"""

    base_response = """📋 **Status Check**
- If `.consent` file exists
    → .consent contains 'check' → CHECK mode
    → otherwise → IMPLEMENTATION mode
    → if '.issue' file exists → content is the current issue
- Otherwise
    → if `.issue` file exists and is non empty → PLAN mode
    → otherwise → DISCUSSION mode
"""
    return await execute_prompt_with_guide("status", base_response, None, pre_text)


async def discuss_prompt(arg: Optional[str] = None, content: Optional[str] = None) -> str:
    """Enter discuss mode for ideation, concepts, and exploration."""
    pre_text = """☑️ **Required Actions:**
- Remove `.consent` file (if it exists)
- If `.issue` file exists, ask the user if they wish to remove it (and do so if confirmed)"""

    if arg:
        pre_text += f"""

🎯 **Focus:**
- {arg}"""

    base_response = """💬 **Discussion Mode Instructions**
**Mode Capabilities:**
📍 Current step: Ideation and conceptual exploration
  - Brainstorm ideas, explore concepts, analyze requirements, discuss architecture
  - You may NOT make code changes, create files, implement solutions other than plans, specifications, or checklists

🔄 **Next Step:** plan when ready for concrete planning
📍 Next step will be PLANNING and task and specification creation
  - You will still not be able to make code changes"""

    return await execute_prompt_with_guide("discuss", base_response, None, pre_text, content)


async def plan_prompt(arg: Optional[str] = None) -> str:
    """Enter plan mode for concrete planning and specification creation."""
    pre_text = """☑️ **Required Actions:**
- Remove `.consent` file (if it exists)
- Create empty `.issue` file (if it doesn't already exist)
- Add paths of documents created during planning to the `.issue` file"""

    if arg:
        pre_text += f"""

🎯 **Focus:**
- {arg}"""

    base_response = """✅ **Plan Mode Instructions**
**Mode Capabilities:**
📍 Current step: Concrete planning and specification creation
  - You may create task specifications, design documents, implementation plans, analyze and gather requirements
  - You may NOT make code changes or implement solutions

🔄 **Next Step:** IMPLEMENTATION (requires user consent)"""

    return await execute_prompt_with_guide("plan", base_response, None, pre_text)


async def implement_prompt(arg: Optional[str] = None, content: Optional[str] = None) -> str:
    """Enter implementation mode for code changes and implementation activities."""
    pre_text = """☑️ **Required Actions:**
- Create `.consent` file with content: `implementation`"""

    if arg:
        pre_text += f"""

🎯 **Focus:**
- {arg}"""

    base_response = """⚙️ **Implementation Mode Instructions**
**Mode Capabilities:**
📍 Current step: Implementation and code changes
  - You may create, modify and remove files, write code, implement solutions, make architectural changes as planned
  - You may not ignore quality requirements or bypass validation
  - You must implement features completely as specified in plans and specifications

🔄 **Next Step:** CHECK when ready for verification (update .consent file content to 'check')"""

    return await execute_prompt_with_guide("implement", base_response, None, pre_text, content)


async def check_prompt(arg: Optional[str] = None, content: Optional[str] = None) -> str:
    """Enter check mode for verification and cleanup activities."""
    logger.debug(f"check_prompt arg: '{repr(arg)}' content: '{repr(content)}'")

    pre_text = """☑️ **Required Actions:**
- Update `.consent` file content to: `check`"""

    if arg:
        pre_text += f"""
🎯 **Focus:**
- {arg}
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

    return await execute_prompt_with_guide("check", base_response, None, pre_text, content)


async def spec_prompt(arg: Optional[str] = None, ctx: Optional[Context] = None) -> str:
    """Handle spec init/upgrade commands with feature gating."""
    # Set up context project name in session manager if context is available
    if ctx:
        try:
            from .session_manager import SessionManager

            session_manager = SessionManager()
            await session_manager.ensure_context_project_loaded(ctx)
            logger.debug("Context project name set up from spec prompt")
        except Exception as e:
            logger.debug(f"Failed to set up context project name from spec prompt: {e}")

    # Check if SpecKit is enabled
    enabled = is_speckit_enabled()

    if not arg or not arg.strip():
        if enabled:
            return """🔧 **Spec-Kit Integration** (Enabled)

**Available Commands:**
- `spec upgrade` - Update spec-kit installation and configuration

**Usage:** Use the spec command with one of the above subcommands."""
        else:
            return """🔧 **Spec-Kit Integration** (Disabled)

**Available Commands:**
- `spec init` - Initialize spec-kit for the current project

**Usage:** Use 'spec init' to enable SpecKit functionality."""

    parts = arg.strip().split()
    command = parts[0] if parts else ""

    # Parse keyword arguments (url=..., version=...)
    kwargs = parse_spec_kwargs(parts[1:])

    if command == "init":
        if enabled:
            return "❌ SpecKit is already initialized. Use 'spec upgrade' to update settings."
        return await handle_spec_init(kwargs)
    elif command == "upgrade":
        if not enabled:
            return "❌ SpecKit must be initialized first. Run 'spec init'."
        return await handle_spec_upgrade(kwargs)
    else:
        return f"❌ Unknown spec command: '{command}'. Use 'spec' without arguments for help."


def parse_spec_kwargs(args: list[str]) -> dict[str, str]:
    """Parse keyword arguments from spec command arguments.

    Args:
        args: List of argument strings like ["url=https://...", "version=v1.0.0"]

    Returns:
        Dictionary of parsed keyword arguments
    """
    kwargs = {}
    valid_keys = {"url", "version"}

    for arg in args:
        if "=" not in arg:
            continue

        key, value = arg.split("=", 1)
        key = key.strip()
        value = value.strip()

        # Validate key is in allowed set
        if key not in valid_keys:
            continue

        # Validate value is not empty and within reasonable length
        if not value or len(value) > 200:
            continue

        # Comprehensive sanitization - no control characters or null bytes
        if any(ord(c) < 32 or c in "\x00\x7f" for c in value):
            continue

        # Additional validation per key type
        if key == "url" and not value.startswith("https://github.com/"):
            continue
        if key == "version" and not re.match(r"^(latest|v?\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?)$", value):
            continue

        kwargs[key] = value
    return kwargs


async def handle_spec_init(kwargs: dict[str, str]) -> str:
    """Handle spec init command with optional parameters."""
    # Check if already enabled
    if is_speckit_enabled():
        return "⚠️ SpecKit is already initialized. Use 'spec upgrade' to update settings."

    # Get parameters with defaults
    url = kwargs.get("url", "https://github.com/spec-kit/spec-kit")
    version = kwargs.get("version", "latest")

    # Validate URL is GitHub only
    if not url.startswith("https://github.com/"):
        return "❌ Invalid URL: Only GitHub repositories are supported"

    # Validate GitHub URL format - allow dots in repo names but not usernames
    if not re.match(r"^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9._-]+/?$", url):
        return f"❌ Invalid GitHub URL format: '{url}'"

    # Enable SpecKit
    enable_speckit(url, version)

    return f"✅ SpecKit initialized successfully!\n📍 URL: {url}\n🏷️ Version: {version}"


async def handle_spec_upgrade(kwargs: dict[str, str]) -> str:
    """Handle spec upgrade command with optional parameters."""
    try:
        # Check if SpecKit is enabled
        if not is_speckit_enabled():
            return "❌ SpecKit is not initialized. Run 'spec init' first."

        current_config = get_speckit_config()
        target_version = kwargs.get("version")
        target_url = kwargs.get("url", current_config.url)

        # If no version specified, fetch latest from GitHub
        if not target_version:
            try:
                latest_release = await fetch_latest_github_release(target_url)
                if latest_release and "tag_name" in latest_release:
                    target_version = latest_release["tag_name"]
                else:
                    return "❌ Could not fetch latest release information from GitHub."
            except ValueError as e:
                return f"❌ Invalid release data: {str(e)}"
            except Exception:
                get_logger(__name__).error("Unexpected error in GitHub API call")
                return "❌ Unexpected error occurred. Please try again."

        # Check if already at target version
        if current_config.version == target_version:
            return f"✅ SpecKit is already at version {target_version}. No upgrade needed."

        # Update configuration
        update_speckit_config({"enabled": True, "url": target_url, "version": target_version})

        return f"""✅ **SpecKit Upgraded Successfully!**

**Previous Version:** {current_config.version or "unknown"}
**New Version:** {target_version}
**Repository:** {target_url}

The SpecKit configuration has been updated. You may need to restart your development environment to use the new version."""

    except Exception as e:
        return f"❌ Error during upgrade: {str(e)}"


async def fetch_latest_github_release(repo_url: str) -> Dict[str, Any]:
    """Fetch latest release information from GitHub API."""
    logger = get_logger(__name__)

    # Strict validation - allow dots in repo names but not usernames, exact domain match
    match = re.match(r"^https://github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9._-]+)/?$", repo_url)
    if not match:
        logger.warning(f"Security: Invalid GitHub URL format attempted: {repo_url}")
        raise ValueError(f"Invalid GitHub URL format: {repo_url}")

    # Additional validation to prevent subdomain attacks
    if not repo_url.startswith("https://github.com/"):
        logger.warning(f"Security: Non-GitHub domain attempted: {repo_url}")
        raise ValueError("Only github.com URLs are allowed")

    owner, repo = match.groups()

    # Validate GitHub naming rules strictly - no dots allowed for security
    if not re.match(r"^[a-zA-Z0-9_-]+$", owner):
        logger.warning(f"Security: Invalid GitHub username format attempted: {owner}")
        raise ValueError(f"Invalid GitHub username format: {owner}")

    if not re.match(r"^[a-zA-Z0-9_-]+$", repo):
        logger.warning(f"Security: Invalid GitHub repository format attempted: {repo}")
        raise ValueError(f"Invalid GitHub repository format: {repo}")

    # Additional validation for GitHub username/repo name rules
    if not (1 <= len(owner) <= 39) or not (1 <= len(repo) <= 100):
        logger.warning(f"Security: Invalid GitHub owner/repo name length attempted: {owner}/{repo}")
        raise ValueError(f"Invalid GitHub owner/repo name length: {owner}/{repo}")

    # Ensure we only hit GitHub API
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    logger.info(f"Security: GitHub API request to {api_url}")

    client = SecureHTTPClient()
    try:
        # Add appropriate timeout (10 seconds) to prevent hanging
        response = client.get(api_url, timeout=10)
        data = json.loads(response.content)

        # Validate required fields
        if not isinstance(data, dict) or "tag_name" not in data:
            raise ValueError("Invalid release data format")

        return data
    except (NetworkError, SecurityError) as e:
        logger.warning(f"Security: GitHub API request failed for {api_url}: {e}")
        raise ValueError("Failed to fetch release information from GitHub")
    except json.JSONDecodeError:
        logger.warning(f"Security: Invalid JSON from GitHub API: {api_url}")
        raise ValueError("Invalid JSON response from GitHub API")


def register_prompts(mcp: FastMCP) -> None:
    """Register all prompt handlers with the MCP server."""

    # Make registration idempotent per MCP instance
    if getattr(mcp, "_prompts_registered", False):
        return
    setattr(mcp, "_prompts_registered", True)

    @mcp.prompt("spec")
    async def _spec_prompt(arg: Optional[str] = None, ctx: Optional[Context] = None) -> str:
        return await spec_prompt(arg, ctx)

    @mcp.prompt("guide")
    async def _guide_prompt(
        arg1: Optional[str] = None,
        arg2: Optional[str] = None,
        arg3: Optional[str] = None,
        arg4: Optional[str] = None,
        arg5: Optional[str] = None,
        arg6: Optional[str] = None,
        arg7: Optional[str] = None,
        arg8: Optional[str] = None,
        arg9: Optional[str] = None,
        arg10: Optional[str] = None,
        arg11: Optional[str] = None,
        arg12: Optional[str] = None,
        arg13: Optional[str] = None,
        arg14: Optional[str] = None,
        arg15: Optional[str] = None,
        arg16: Optional[str] = None,
        ctx: Optional[Context] = None,
    ) -> str:
        """Access guide content with category/document syntax.

        Examples:
        - @guide docs                    # Show docs category content
        - @guide docs/readme             # Show specific document in docs category
        - @guide my-collection           # Show collection content
        """
        from .guide_integration import GuidePromptHandler

        handler = GuidePromptHandler()

        # Reconstruct args list from non-None parameters (MCP has pre-parsed strings)
        args = [
            arg
            for arg in [
                arg1,
                arg2,
                arg3,
                arg4,
                arg5,
                arg6,
                arg7,
                arg8,
                arg9,
                arg10,
                arg11,
                arg12,
                arg13,
                arg14,
                arg15,
                arg16,
            ]
            if arg is not None
        ]

        if args:
            return await handler.handle_guide_request(args, ctx)
        else:
            # No arguments - show help
            return await handler.handle_guide_request([], ctx)
