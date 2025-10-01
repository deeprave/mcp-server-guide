"""Command parser for slash commands."""

import shlex
from typing import Dict, List, Optional, Any, Union


class CommandParser:
    """Parser for slash commands from AI agents."""

    def parse_command(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse slash command from text.

        Args:
            text: Input text to parse

        Returns:
            Dict with command, subcommand, args, and params, or None if not a valid slash command
        """
        if not text or not text.strip():
            return None

        text = text.strip()
        if not text.startswith("/"):
            return None

        # Remove leading slash
        command_text = text[1:].strip()
        if not command_text:
            return None

        # Use shlex to split the text, supporting quoted arguments, but fall back to simple split
        try:
            parts = shlex.split(command_text)
        except ValueError:
            # Fall back to simple split if shlex fails
            parts = command_text.split()

        command_part = parts[0]

        # Check for colon syntax (e.g., "guide:lang", "g:new")
        command = command_part
        subcommand = None

        if ":" in command_part:
            command, subcommand = command_part.split(":", 1)

        # Separate args from parameters
        args = []
        params = {}

        for part in parts[1:]:
            if "=" in part:
                # This is a parameter
                key, value = part.split("=", 1)
                params[key] = self._parse_parameter_value(value)
            else:
                # This is an argument
                args.append(part)

        result = {"command": command, "args": args, "params": params}

        if subcommand is not None:
            result["subcommand"] = subcommand

        return result

    def _parse_parameter_value(self, value: str) -> Union[str, List[str], bool]:
        """Parse parameter value with type conversion.

        Args:
            value: Raw parameter value

        Returns:
            Parsed value (string, list, or boolean)
        """
        # Handle boolean values
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False

        # Handle comma-separated values
        if "," in value:
            return [item.strip() for item in value.split(",")]

        # Return as string
        return value
