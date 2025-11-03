"""Tests for spec prompt functionality."""

import pytest
from unittest.mock import AsyncMock, patch

from mcp_server_guide.prompts import register_prompts


class TestSpecPrompt:
    """Test spec prompt registration and basic functionality."""

    @pytest.mark.asyncio
    async def test_spec_prompt_registration(self):
        """Test that spec_prompt is registered with MCP server."""
        # Create a mock server
        mock_server = AsyncMock()
        mock_server._prompts_registered = False

        # Mock the prompt decorator
        prompt_calls = []

        def mock_prompt(name):
            def decorator(func):
                prompt_calls.append(name)
                return func

            return decorator

        mock_server.prompt = mock_prompt

        # Register prompts
        register_prompts(mock_server)

        # Verify spec prompt is registered
        assert "spec" in prompt_calls

    @pytest.mark.asyncio
    async def test_spec_prompt_exists(self):
        """Test that spec_prompt function exists."""
        from mcp_server_guide.prompts import spec_prompt

        # Function should exist
        assert callable(spec_prompt)

        # Should handle no arguments
        result = await spec_prompt()
        assert isinstance(result, str)
        assert "spec" in result.lower()

    @pytest.mark.asyncio
    async def test_spec_command_parsing(self):
        """Test parsing of spec init/update/sync commands."""
        from mcp_server_guide.prompts import spec_prompt

        # Test init command
        result = await spec_prompt("init")
        assert "init" in result.lower()

        # Test update command
        result = await spec_prompt("update")
        assert "update" in result.lower()

        # Test sync command
        result = await spec_prompt("sync")
        assert "sync" in result.lower()

        # Test unknown command
        result = await spec_prompt("unknown")
        assert "unknown" in result.lower()
        assert "error" in result.lower() or "unknown" in result.lower()

    @pytest.mark.asyncio
    async def test_spec_input_validation(self):
        """Test input validation and error handling."""
        from mcp_server_guide.prompts import spec_prompt

        # Test empty string
        result = await spec_prompt("")
        assert "Available Commands" in result

        # Test whitespace only
        result = await spec_prompt("   ")
        assert "Available Commands" in result

        # Test None
        result = await spec_prompt(None)
        assert "Available Commands" in result

    def test_spec_instruction_model(self):
        """Test SpecInstruction model creation and serialization."""
        from mcp_server_guide.models.spec_instruction import SpecInstruction, SpecInstructionSet

        # Test basic instruction
        instruction = SpecInstruction(action="create_file", description="Create pyproject.toml")

        assert instruction.action == "create_file"
        assert instruction.description == "Create pyproject.toml"

        # Test to_dict
        inst_dict = instruction.to_dict()
        assert inst_dict["action"] == "create_file"
        assert inst_dict["description"] == "Create pyproject.toml"
        assert inst_dict["description"] == "Create pyproject.toml"

        # Test instruction set
        instruction_set = SpecInstructionSet(instructions=[instruction], summary="Initialize spec-kit")

        assert len(instruction_set.instructions) == 1
        assert instruction_set.summary == "Initialize spec-kit"

        # Test JSON serialization
        json_str = instruction_set.to_json()
        assert "create_file" in json_str
        assert "Initialize spec-kit" in json_str

    @pytest.mark.asyncio
    async def test_spec_prompt_disabled_state(self):
        """Test spec prompt behavior when SpecKit is disabled."""
        from mcp_server_guide.prompts import spec_prompt

        # Mock disabled state
        with patch("mcp_server_guide.prompts.is_speckit_enabled", return_value=False):
            # Test help shows only init command
            result = await spec_prompt()
            assert "spec init" in result
            assert "spec upgrade" not in result

            # Test init command works
            result = await spec_prompt("init")
            assert "init" in result.lower()

            # Test upgrade command is rejected
            result = await spec_prompt("upgrade")
            assert "must be initialized first" in result.lower() or "unknown" in result.lower()

    @pytest.mark.asyncio
    async def test_spec_prompt_enabled_state(self):
        """Test spec prompt behavior when SpecKit is enabled."""
        from mcp_server_guide.prompts import spec_prompt

        # Mock enabled state and GitHub API
        with patch("mcp_server_guide.prompts.is_speckit_enabled", return_value=True):
            with patch("mcp_server_guide.prompts.fetch_latest_github_release", return_value={"tag_name": "v1.0.0"}):
                with patch("mcp_server_guide.services.speckit_manager.update_speckit_config"):
                    # Test help shows only upgrade command when enabled
                    result = await spec_prompt()
                    assert "spec init" not in result
                    assert "spec upgrade" in result

                    # Test init command is blocked when enabled
                    result = await spec_prompt("init")
                    assert "already initialized" in result.lower()

                    # Test upgrade command works
                    result = await spec_prompt("upgrade")
                    assert "upgrade" in result.lower()

    @pytest.mark.asyncio
    async def test_spec_init_blocked_when_enabled(self):
        """Test that spec init is blocked when SpecKit is already enabled."""
        from mcp_server_guide.prompts import spec_prompt

        # Mock enabled state
        with patch("mcp_server_guide.prompts.is_speckit_enabled", return_value=True):
            result = await spec_prompt("init")
            assert "already initialized" in result.lower()
            assert "spec upgrade" in result

    @pytest.mark.asyncio
    async def test_spec_init_command_basic(self):
        """Test basic spec init command functionality."""
        from mcp_server_guide.prompts import spec_prompt
        from unittest.mock import AsyncMock

        mock_init = AsyncMock(return_value="✅ SpecKit initialized successfully!")
        with patch("mcp_server_guide.prompts.is_speckit_enabled", return_value=False):
            with patch("mcp_server_guide.prompts.handle_spec_init", mock_init):
                result = await spec_prompt("init")
                assert "initialized successfully" in result
                mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_spec_init_with_parameters(self):
        """Test spec init command with url and version parameters."""
        from mcp_server_guide.prompts import spec_prompt
        from unittest.mock import AsyncMock

        mock_init = AsyncMock(return_value="✅ SpecKit initialized with custom settings!")
        with patch("mcp_server_guide.prompts.is_speckit_enabled", return_value=False):
            with patch("mcp_server_guide.prompts.handle_spec_init", mock_init):
                result = await spec_prompt("init url=https://github.com/custom/repo version=v2.0.0")
                assert "initialized" in result
                mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_spec_init_parameter_parsing(self):
        """Test parameter parsing for spec init command."""
        from mcp_server_guide.prompts import parse_spec_kwargs

        # Test basic parameters
        kwargs = parse_spec_kwargs(["url=https://github.com/test/repo", "version=v1.0.0"])
        assert kwargs["url"] == "https://github.com/test/repo"
        assert kwargs["version"] == "v1.0.0"

        # Test with defaults
        kwargs = parse_spec_kwargs([])
        assert kwargs.get("url") is None
        assert kwargs.get("version") is None

    @pytest.mark.asyncio
    async def test_spec_upgrade_requires_enabled_state(self):
        """Test that spec upgrade only works when SpecKit is enabled."""
        from mcp_server_guide.prompts import spec_prompt

        # Mock disabled state
        with patch("mcp_server_guide.prompts.is_speckit_enabled", return_value=False):
            result = await spec_prompt("upgrade")
            assert "must be initialized first" in result.lower()
            assert "spec init" in result

    @pytest.mark.asyncio
    async def test_spec_upgrade_basic_functionality(self):
        """Test basic spec upgrade command functionality."""
        from mcp_server_guide.prompts import spec_prompt
        from unittest.mock import AsyncMock

        # Mock enabled state and upgrade function
        mock_upgrade = AsyncMock(return_value="✅ SpecKit upgraded successfully!")
        with patch("mcp_server_guide.prompts.is_speckit_enabled", return_value=True):
            with patch("mcp_server_guide.prompts.handle_spec_upgrade", mock_upgrade):
                result = await spec_prompt("upgrade")
                assert "upgraded successfully" in result
                mock_upgrade.assert_called_once()

    @pytest.mark.asyncio
    async def test_spec_upgrade_with_version_parameter(self):
        """Test spec upgrade with version parameter."""
        from mcp_server_guide.prompts import spec_prompt
        from unittest.mock import AsyncMock

        # Mock enabled state and upgrade function
        mock_upgrade = AsyncMock(return_value="✅ SpecKit upgraded to v2.0.0!")
        with patch("mcp_server_guide.prompts.is_speckit_enabled", return_value=True):
            with patch("mcp_server_guide.prompts.handle_spec_upgrade", mock_upgrade):
                result = await spec_prompt("upgrade version=v2.0.0")
                assert "upgraded" in result
                mock_upgrade.assert_called_once()
                # Check that version parameter was passed
                call_args = mock_upgrade.call_args[0][0]
                assert call_args.get("version") == "v2.0.0"

    @pytest.mark.asyncio
    async def test_spec_upgrade_github_integration(self):
        """Test spec upgrade GitHub API integration."""
        from mcp_server_guide.prompts import handle_spec_upgrade
        from mcp_server_guide.models.speckit_config import SpecKitConfig

        # Mock current configuration with older version
        mock_speckit_config = SpecKitConfig(enabled=True, url="https://github.com/spec-kit/spec-kit", version="v1.0.0")

        # Mock GitHub API response
        mock_response = {"tag_name": "v1.5.0", "name": "Release v1.5.0", "published_at": "2024-01-15T10:00:00Z"}

        with patch("mcp_server_guide.prompts.get_speckit_config", return_value=mock_speckit_config):
            with patch("mcp_server_guide.prompts.fetch_latest_github_release", return_value=mock_response):
                with patch("mcp_server_guide.prompts.update_speckit_config") as mock_update:
                    result = await handle_spec_upgrade({})
                    assert "v1.5.0" in result
                    assert "upgraded" in result.lower()
                    mock_update.assert_called_once()
