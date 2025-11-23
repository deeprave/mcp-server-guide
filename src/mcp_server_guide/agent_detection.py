"""Agent detection for MCP clients."""

from dataclasses import dataclass
from typing import Optional

from mcp.types import InitializeRequestParams


@dataclass
class AgentInfo:
    """Information about the connected MCP agent."""

    name: str
    normalized_name: str
    version: Optional[str]
    prompt_prefix: str


AGENT_PREFIX_MAP = {
    "kiro": "@",
    "cursor": "@",
    "claude": "/{mcp_name}:",
    "copilot": "/",
    "gemini": "@",
    "windsurf": "/",
}

# Agent name patterns for detection
AGENT_PATTERNS = {
    "kiro": ["kiro", "amazon", "q dev"],
    "claude": ["claude"],
    "copilot": ["copilot"],
    "gemini": ["gemini"],
    "cursor": ["cursor"],
    "windsurf": ["windsurf"],
}


def normalize_agent_name(name: str) -> str:
    """Normalize agent name to standard identifier."""
    name_lower = name.lower()

    for agent, patterns in AGENT_PATTERNS.items():
        if any(pattern in name_lower for pattern in patterns):
            return agent

    return "unknown"


def detect_agent(client_params: InitializeRequestParams) -> AgentInfo:
    """Detect agent from MCP client parameters."""
    client_name = client_params.clientInfo.name
    client_version = client_params.clientInfo.version

    normalized = normalize_agent_name(client_name)
    prefix = AGENT_PREFIX_MAP.get(normalized, "/")

    return AgentInfo(
        name=client_name,
        normalized_name=normalized,
        version=client_version,
        prompt_prefix=prefix,
    )


def format_agent_info(agent_info: AgentInfo, server_name: str, markdown: bool = False) -> str:
    """Format agent information for display.

    Args:
        agent_info: The agent information to format
        server_name: The MCP server name
        markdown: If True, use markdown formatting with heading and bold

    Returns:
        Formatted agent information string
    """
    if markdown:
        output = f"""# Agent Information

**Agent Name**: {agent_info.name}
**Normalized Name**: {agent_info.normalized_name}
**Version**: {agent_info.version or "Unknown"}
**Prompt Prefix**: {agent_info.prompt_prefix}
**Server Name**: {server_name}"""
    else:
        output = f"""Agent Name: {agent_info.name}
Normalized Name: {agent_info.normalized_name}
Version: {agent_info.version or "Unknown"}
Prompt Prefix: {agent_info.prompt_prefix}
Server Name: {server_name}"""

    # Add Claude-specific note
    if agent_info.normalized_name == "claude":
        note = "Note: For Claude, use your mcpServers config key (not the server name above) in the prompt prefix."
        if markdown:
            output += f"\n\n*{note}*"
        else:
            output += f"\n\n{note}"

    output += "\n\nThis information is used to provide agent-specific help and examples."
    return output
