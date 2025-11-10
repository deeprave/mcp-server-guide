"""Test CLI help generation specifically."""

import pytest
import click
from src.mcp_server_guide.cli_parser_click import generate_cli_help, generate_context_help
from src.mcp_server_guide.help_system import format_guide_help


class TestCliHelpGeneration:
    """Test CLI help generation functions."""

    def test_generate_cli_help_safe(self):
        """Test that generate_cli_help doesn't raise exceptions."""
        try:
            result = generate_cli_help()
            assert isinstance(result, str)
            assert len(result) > 0
            assert "Usage:" in result
        except (SystemExit, click.exceptions.Exit) as e:
            pytest.fail(f"generate_cli_help raised {type(e).__name__}: {e}")

    @pytest.mark.asyncio
    async def test_format_guide_help_safe(self):
        """Test that format_guide_help doesn't raise exceptions."""
        try:
            result = await format_guide_help()
            assert isinstance(result, str)
            assert len(result) > 0
        except (SystemExit, click.exceptions.Exit) as e:
            pytest.fail(f"format_guide_help raised {type(e).__name__}: {e}")

    def test_generate_context_help_all_targets(self):
        """Test generate_context_help with all possible targets."""
        targets = [None, "category", "collection", "document", "invalid"]

        for target in targets:
            try:
                result = generate_context_help(target)
                assert isinstance(result, str)
                assert len(result) > 0
            except (SystemExit, click.exceptions.Exit) as e:
                pytest.fail(f"generate_context_help({target}) raised {type(e).__name__}: {e}")

    def test_click_context_creation_safe(self):
        """Test that Click context creation is safe."""
        from src.mcp_server_guide.cli_parser_click import guide, category, collection, document

        commands = [guide, category, collection, document]

        for cmd in commands:
            try:
                ctx = click.Context(cmd)
                help_text = cmd.get_help(ctx)
                assert isinstance(help_text, str)
                assert len(help_text) > 0
            except (SystemExit, click.exceptions.Exit) as e:
                pytest.fail(f"Context creation for {cmd.name} raised {type(e).__name__}: {e}")
