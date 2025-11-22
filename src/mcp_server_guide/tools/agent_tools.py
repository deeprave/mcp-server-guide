"""Agent detection tools."""

from mcp.server.fastmcp import Context

from ..agent_detection import detect_agent, format_agent_info
from ..logging_config import get_logger

logger = get_logger(__name__)


async def guide_get_agent_info(ctx: Context) -> str:
    """Get agent information from MCP client.

    Captures agent name, version, and prompt prefix from the MCP session.
    Caches the result in ServerExtensions for subsequent calls.

    Returns formatted agent information with explicit display instruction.
    """
    try:
        logger.debug("guide_get_agent_info called")

        from ..server import get_current_server

        server = await get_current_server()
        if not server:
            logger.error("Server not available")
            return "Error: Server not available"

        # Check cache first
        if server.extensions.agent_info:
            logger.debug("Using cached agent info")
            agent_info = server.extensions.agent_info
        else:
            # Capture from context and cache
            try:
                agent_info = detect_agent(ctx.session.client_params)
                server.extensions.agent_info = agent_info
                logger.debug(f"Agent info detected and cached: {agent_info.name}")
            except (AttributeError, ValueError) as e:
                logger.error(f"Cannot access session.client_params: {e}")
                return "Error: Agent detection requires an active MCP session"

        return format_agent_info(agent_info, server.name, markdown=False)

    except Exception as e:
        logger.error(f"Exception in guide_get_agent_info: {type(e).__name__}: {str(e)}", exc_info=True)
        return f"Error: {type(e).__name__}: {str(e)}"
