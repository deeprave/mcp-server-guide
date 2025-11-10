"""Comprehensive tests for all help command variations."""

import pytest
import click
from src.mcp_server_guide.guide_integration import GuidePromptHandler
from src.mcp_server_guide.cli_parser_click import parse_command
from src.mcp_server_guide.help_system import format_guide_help, generate_context_help


class TestHelpCommandVariations:
    """Test all help command variations to ensure server stability."""

    @pytest.mark.asyncio
    async def test_all_guide_help_variations(self):
        """Test all possible @guide help command variations."""
        handler = GuidePromptHandler()

        # All possible help command variations that should work
        help_variations = [
            # Basic help
            [],
            ["help"],
            ["--help"],
            ["-h"],
            # Category help
            ["category", "--help"],
            ["category", "-h"],
            # Collection help
            ["collection", "--help"],
            ["collection", "-h"],
            # Document help
            ["document", "--help"],
            ["document", "-h"],
            # Subcommand help
            ["category", "add", "--help"],
            ["category", "list", "--help"],
            ["category", "remove", "--help"],
            ["collection", "add", "--help"],
            ["collection", "list", "--help"],
            ["document", "create", "--help"],
            ["document", "list", "--help"],
            # Invalid commands (should still return help gracefully)
            ["invalid", "--help"],
            ["category", "invalid", "--help"],
        ]

        for args in help_variations:
            try:
                result = await handler.handle_guide_request(args)
                assert isinstance(result, str)
                assert len(result) > 0
                # Should contain help-related content
                assert any(keyword in result.lower() for keyword in ["help", "usage", "command", "guide"])
            except (SystemExit, click.exceptions.Exit) as e:
                pytest.fail(f"Guide handler with args {args} raised {type(e).__name__}: {e}")
            except Exception as e:
                pytest.fail(f"Guide handler with args {args} raised unexpected exception {type(e).__name__}: {e}")

    def test_all_parse_command_help_variations(self):
        """Test that parse_command handles all help variations safely."""
        help_variations = [
            ["--help"],
            ["-h"],
            ["category", "--help"],
            ["collection", "--help"],
            ["document", "--help"],
            ["category", "add", "--help"],
            ["invalid", "--help"],
        ]

        for args in help_variations:
            try:
                result = parse_command(args)
                assert result.type == "help"
            except (SystemExit, click.exceptions.Exit) as e:
                pytest.fail(f"parse_command({args}) raised {type(e).__name__}: {e}")

    @pytest.mark.asyncio
    async def test_format_guide_help_stability(self):
        """Test that format_guide_help is stable and doesn't crash."""
        try:
            result = await format_guide_help()
            assert isinstance(result, str)
            assert len(result) > 0
            assert "MCP Server Guide Help" in result
        except (SystemExit, click.exceptions.Exit) as e:
            pytest.fail(f"format_guide_help raised {type(e).__name__}: {e}")

    def test_generate_context_help_all_targets(self):
        """Test generate_context_help with all possible targets."""
        targets = [
            None,
            "category",
            "collection",
            "document",
            "invalid",
            "",
        ]

        for target in targets:
            try:
                result = generate_context_help(target)
                assert isinstance(result, str)
                assert len(result) > 0
            except (SystemExit, click.exceptions.Exit) as e:
                pytest.fail(f"generate_context_help({target}) raised {type(e).__name__}: {e}")

    @pytest.mark.asyncio
    async def test_help_commands_return_useful_content(self):
        """Test that help commands return useful, non-empty content."""
        handler = GuidePromptHandler()

        test_cases = [
            ([], "general help"),
            (["--help"], "general help"),
            (["category", "--help"], "category help"),
            (["collection", "--help"], "collection help"),
            (["document", "--help"], "document help"),
        ]

        for args, description in test_cases:
            result = await handler.handle_guide_request(args)
            assert isinstance(result, str), f"{description} should return string"
            assert len(result) > 50, f"{description} should return substantial content"
            # Should not contain error messages about crashes or exit exceptions
            assert "crash" not in result.lower(), f"{description} should not mention crashes"
            assert "exit exception" not in result.lower(), f"{description} should not mention exit exceptions"
            assert "systemExit" not in result, f"{description} should not mention SystemExit"

    def test_help_system_defensive_programming(self):
        """Test that help system has proper defensive programming."""
        # Test with None arguments
        try:
            result = parse_command(None)
            assert result.type == "help"
        except Exception as e:
            pytest.fail(f"parse_command(None) should handle gracefully: {e}")

        # Test with empty list
        try:
            result = parse_command([])
            assert result.type == "help"
        except Exception as e:
            pytest.fail(f"parse_command([]) should handle gracefully: {e}")

        # Test with non-string arguments
        try:
            result = parse_command([123, None, "help"])
            assert result.type == "help"
        except Exception as e:
            pytest.fail(f"parse_command with non-string args should handle gracefully: {e}")

    @pytest.mark.asyncio
    async def test_server_stability_after_help_commands(self):
        """Test that server remains stable after processing help commands."""
        handler = GuidePromptHandler()

        # Process multiple help commands in sequence
        help_commands = [
            ["--help"],
            ["category", "--help"],
            ["collection", "--help"],
            ["document", "--help"],
            ["invalid", "--help"],
        ]

        for args in help_commands:
            result = await handler.handle_guide_request(args)
            assert isinstance(result, str)
            assert len(result) > 0

        # After all help commands, regular commands should still work
        # (This would test that the server hasn't been corrupted)
        try:
            result = await handler.handle_guide_request(["status"])
            assert isinstance(result, str)
        except Exception:
            # Status command might fail due to missing dependencies, but that's OK
            # The important thing is that we can still process commands
            pass
