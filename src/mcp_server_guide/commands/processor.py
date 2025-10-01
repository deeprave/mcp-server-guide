"""Main command processor for MCP integration."""

from typing import Dict, Any, Optional
from .parser import CommandParser
from .handler import CommandHandler


class CommandProcessor:
    """Main processor for slash commands from AI agents."""

    def __init__(self) -> None:
        """Initialize command processor."""
        self.parser = CommandParser()
        self.handler = CommandHandler()

    async def process_message(self, message: str) -> Optional[Dict[str, Any]]:
        """Process a message for slash commands.

        Args:
            message: Input message from AI agent

        Returns:
            Command result dict or None if not a command
        """
        # Parse the message
        parsed = self.parser.parse_command(message)
        if not parsed:
            return None

        try:
            # Execute the command
            result = await self.handler.execute_command(parsed["command"], parsed["args"], parsed.get("params", {}))

            return result

        except Exception as e:
            return {"success": False, "error": f"Command processing error: {str(e)}"}

    def get_help(self) -> Dict[str, Any]:
        """Get help information for available commands.

        Returns:
            Dict with help information
        """
        return {
            "success": True,
            "help": {
                "commands": {
                    "/guide": "Show all guides or specific category",
                    "/guide <category>": "Show specific category content",
                    "/<category>": "Shortcut to show category content",
                    "/guide-new <name> [params]": "Create new category",
                    "/guide-edit <name> [params]": "Edit existing category",
                    "/guide-del <name>": "Delete category (with confirmation)",
                },
                "parameters": {
                    "dir=<path>": "Directory path for category",
                    "patterns=<pattern>[,<pattern>]": "File patterns (comma-separated)",
                    "auto-load=true|false": "Auto-load category content",
                },
                "examples": [
                    "/guide",
                    "/guide lang",
                    "/lang",
                    "/guide-new typescript dir=lang/ts patterns=*.ts,*.tsx auto-load=true",
                    "/guide-edit typescript patterns=*.ts,*.tsx,*.d.ts",
                    "/guide-del typescript",
                ],
            },
        }
