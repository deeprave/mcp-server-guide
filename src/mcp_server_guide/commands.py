"""Command name constants and metadata - single source of truth."""

from dataclasses import dataclass
from typing import Final, Optional


@dataclass(frozen=True)
class CommandInfo:
    """Metadata for a guide command."""

    name: str
    description: str
    usage: str
    help_text: str
    category: str  # "phase", "utility", "management"
    usage_pattern: str = ":COMMAND"  # ":COMMAND" or "CATEGORY/COLLECTION"
    accepts_user_content: bool = False
    has_prompt_document: bool = False


# Phase transition commands
CMD_DISCUSS: Final[str] = "discuss"
CMD_PLAN: Final[str] = "plan"
CMD_IMPLEMENT: Final[str] = "implement"
CMD_CHECK: Final[str] = "check"

# Utility commands
CMD_STATUS: Final[str] = "status"
CMD_SEARCH: Final[str] = "search"
CMD_HELP: Final[str] = "help"
CMD_CONFIG: Final[str] = "config"
CMD_CLONE: Final[str] = "clone"
CMD_AGENT_INFO: Final[str] = "agent-info"

# Management commands
CMD_CATEGORY: Final[str] = "category"
CMD_COLLECTION: Final[str] = "collection"
CMD_DOCUMENT: Final[str] = "document"

# Command metadata registry
COMMANDS = {
    CMD_DISCUSS: CommandInfo(
        name=CMD_DISCUSS,
        description="Start discussion phase with optional focus",
        usage=':discuss "Add optional focus of the discussion"',
        help_text="Use to initiate a discussion phase, either general or focus on a specific topic",
        category="phase",
        usage_pattern=":COMMAND",
        accepts_user_content=True,
        has_prompt_document=True,
    ),
    CMD_PLAN: CommandInfo(
        name=CMD_PLAN,
        description="Start planning phase with optional focus",
        usage=':plan "Add optional planning focus"',
        help_text="Use to initiate a planning phase with optional focus area",
        category="phase",
        usage_pattern=":COMMAND",
        accepts_user_content=True,
        has_prompt_document=True,
    ),
    CMD_IMPLEMENT: CommandInfo(
        name=CMD_IMPLEMENT,
        description="Start implementation phase with optional focus",
        usage=':implement "Add optional implementation focus"',
        help_text="Use to initiate implementation phase with optional focus area",
        category="phase",
        usage_pattern=":COMMAND",
        accepts_user_content=True,
        has_prompt_document=True,
    ),
    CMD_CHECK: CommandInfo(
        name=CMD_CHECK,
        description="Start check phase with optional focus",
        usage=':check "Add optional check focus"',
        help_text="Use to initiate check phase with optional focus area",
        category="phase",
        usage_pattern=":COMMAND",
        accepts_user_content=True,
        has_prompt_document=True,
    ),
    CMD_STATUS: CommandInfo(
        name=CMD_STATUS,
        description="Show current status",
        usage=":status",
        help_text="Display current project and phase status",
        category="utility",
        usage_pattern=":COMMAND",
        accepts_user_content=False,
        has_prompt_document=True,
    ),
    CMD_SEARCH: CommandInfo(
        name=CMD_SEARCH,
        description="Search project content",
        usage=':search "query text"',
        help_text="Search across all project content",
        category="utility",
        usage_pattern=":COMMAND",
        accepts_user_content=True,
        has_prompt_document=True,
    ),
    CMD_HELP: CommandInfo(
        name=CMD_HELP,
        description="Show help information",
        usage=":help",
        help_text="Display help information and available commands",
        category="utility",
        usage_pattern=":COMMAND",
        accepts_user_content=False,
        has_prompt_document=True,
    ),
    CMD_CONFIG: CommandInfo(
        name=CMD_CONFIG,
        description="Display project configuration",
        usage=":config [project] [--verbose] [--projects]",
        help_text="View or manage project configuration",
        category="utility",
        usage_pattern=":COMMAND",
        accepts_user_content=False,
        has_prompt_document=False,
    ),
    CMD_CLONE: CommandInfo(
        name=CMD_CLONE,
        description="Clone project configuration",
        usage=":clone <source> [target] [--force]",
        help_text="Clone project configuration from source to target",
        category="utility",
        usage_pattern=":COMMAND",
        accepts_user_content=False,
        has_prompt_document=False,
    ),
    CMD_AGENT_INFO: CommandInfo(
        name=CMD_AGENT_INFO,
        description="Show detected agent information",
        usage=":agent-info",
        help_text="Display information about the detected MCP agent",
        category="utility",
        usage_pattern=":COMMAND",
        accepts_user_content=False,
        has_prompt_document=False,
    ),
    CMD_CATEGORY: CommandInfo(
        name=CMD_CATEGORY,
        description="Manage categories",
        usage=":category <subcommand> [args]",
        help_text="Create, update, list, or remove categories",
        category="management",
        usage_pattern=":COMMAND",
        accepts_user_content=False,
        has_prompt_document=False,
    ),
    CMD_COLLECTION: CommandInfo(
        name=CMD_COLLECTION,
        description="Manage collections",
        usage=":collection <subcommand> [args]",
        help_text="Create, update, list, or remove collections",
        category="management",
        usage_pattern=":COMMAND",
        accepts_user_content=False,
        has_prompt_document=False,
    ),
    CMD_DOCUMENT: CommandInfo(
        name=CMD_DOCUMENT,
        description="Manage documents",
        usage=":document <subcommand> [args]",
        help_text="Create, update, list, or remove documents",
        category="management",
        usage_pattern=":COMMAND",
        accepts_user_content=False,
        has_prompt_document=False,
    ),
}

# Convenience accessors
ALL_COMMANDS = set(COMMANDS.keys())
PHASE_COMMANDS = {k for k, v in COMMANDS.items() if v.category == "phase"}
UTILITY_COMMANDS = {k for k, v in COMMANDS.items() if v.category == "utility"}
MANAGEMENT_COMMANDS = {k for k, v in COMMANDS.items() if v.category == "management"}
COMMANDS_WITH_PROMPTS = {k for k, v in COMMANDS.items() if v.has_prompt_document}


def get_command_info(command: str) -> Optional[CommandInfo]:
    """Get metadata for a command.

    Args:
        command: Command name to look up

    Returns:
        CommandInfo if command exists, None otherwise
    """
    return COMMANDS.get(command)
