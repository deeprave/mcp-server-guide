"""Command parser for slash commands."""

import csv
import io
import logging
import shlex
from typing import Dict, List, Optional, Any, Union


class CommandParser:
    """Parser for slash commands from AI agents."""

    ALLOWED_COLON_COMMANDS = ["guide", "g"]

    def parse_command(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse command from text with selective matching.

        Args:
            text: Input text to parse

        Returns:
            Dict with command, subcommand, args, and params, or None if not a command
        """
        if not text or not text.strip():
            return None

        text = text.strip()

        # Use shlex to split the text, supporting quoted arguments. If shlex fails, return None.
        try:
            parts = shlex.split(text)
        except ValueError as e:
            logging.warning("shlex.split failed to parse command text: %r; error: %s", text, e)
            # If shlex fails, return None to indicate parsing error
            return None

        if not parts:
            return None

        command_part = parts[0]

        # Only match specific command patterns
        if command_part == "guide":
            # Check if it's just "guide" or "guide <single_word>"
            if len(parts) == 1:
                # Just "guide"
                command = "guide"
                subcommand = None
            elif len(parts) == 2 and not parts[1].startswith("="):
                # "guide <category>" - single word category
                command = "guide"
                subcommand = None
            else:
                # Multiple words or parameters - let AI handle it
                return None
        elif ":" in command_part:
            # Handle colon syntax (guide:*, g:*)
            if command_part.count(":") > 1:
                # Reject commands with multiple colons to prevent ambiguity
                return None
            command, subcommand = command_part.split(":", 1)
            if command not in self.ALLOWED_COLON_COMMANDS:
                return None
        else:
            # Not a recognized command pattern
            return None

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

        # Handle comma-separated values, respecting quoted commas
        if "," in value:
            try:
                reader = csv.reader(io.StringIO(value))
                return [item.strip() for item in next(reader) if item.strip()]
            except (csv.Error, StopIteration):
                # Fall back to simple split if CSV parsing fails
                return [item.strip() for item in value.split(",") if item.strip()]

        # Return as string
        return value
