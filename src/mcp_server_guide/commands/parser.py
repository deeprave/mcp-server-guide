"""Command parser for slash commands."""

import csv
import io
import logging
import shlex
from typing import Dict, List, Optional, Any, Union


class CommandParser:
    """Parser for slash commands from AI agents."""

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

        command = parts[0]

        if command != "guide":
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

        return {"command": command, "args": args, "params": params}

    @staticmethod
    def _parse_parameter_value(value: str) -> Union[str, List[str], bool]:
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
                # Fall back to a simple split if CSV parsing fails
                return [item.strip() for item in value.split(",") if item.strip()]

        # Return as string
        return value
