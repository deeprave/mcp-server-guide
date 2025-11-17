"""Tests for SpecKit manager service."""

from unittest.mock import patch, AsyncMock
from mcp_server_guide.services.speckit_manager import (
    is_speckit_enabled,
    get_speckit_config,
    enable_speckit,
    update_speckit_config,
)
from mcp_server_guide.models.speckit_config import SpecKitConfig


class TestIsSpeckitEnabled:
    """Test is_speckit_enabled function."""

    async def test_enabled_when_speckit_is_true(self):
        """Test that function returns True when SpecKit is enabled."""
        with patch("mcp_server_guide.services.speckit_manager.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.is_speckit_enabled.return_value = True
            mock_session_class.return_value = mock_session

            result = await is_speckit_enabled()
            assert result is True

    async def test_disabled_when_speckit_is_false(self):
        """Test that function returns False when SpecKit is disabled."""
        with patch("mcp_server_guide.services.speckit_manager.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.is_speckit_enabled.return_value = False
            mock_session_class.return_value = mock_session

            result = await is_speckit_enabled()
            assert result is False

    async def test_disabled_when_speckit_is_none(self):
        """Test that function returns False when SpecKit config is None."""
        with patch("mcp_server_guide.services.speckit_manager.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.is_speckit_enabled.return_value = False
            mock_session_class.return_value = mock_session

            result = await is_speckit_enabled()
            assert result is False


class TestGetSpeckitConfig:
    """Test get_speckit_config function."""

    async def test_returns_config_when_exists(self):
        """Test that function returns config when it exists."""
        expected_config = SpecKitConfig(enabled=True, url="https://github.com/test/repo", version="v1.0.0")

        with patch("mcp_server_guide.services.speckit_manager.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get_speckit_config.return_value = expected_config
            mock_session_class.return_value = mock_session

            result = await get_speckit_config()
            assert result == expected_config

    async def test_returns_default_when_none(self):
        """Test that function returns default config when none exists."""
        with patch("mcp_server_guide.services.speckit_manager.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get_speckit_config.return_value = None
            mock_session_class.return_value = mock_session

            result = await get_speckit_config()
            assert result.enabled is False
            assert result.url == "https://github.com/spec-kit/spec-kit"
            assert result.version == "latest"


class TestEnableSpeckit:
    """Test enable_speckit function."""

    async def test_enable_with_defaults(self):
        """Test enabling SpecKit with default values."""
        with patch("mcp_server_guide.services.speckit_manager.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session

            await enable_speckit()

            mock_session.set_speckit_config.assert_called_once()
            config_arg = mock_session.set_speckit_config.call_args[0][0]
            assert config_arg.enabled is True
            assert config_arg.url == "https://github.com/spec-kit/spec-kit"
            assert config_arg.version == "latest"

    async def test_enable_with_custom_values(self):
        """Test enabling SpecKit with custom values."""
        with patch("mcp_server_guide.services.speckit_manager.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session

            await enable_speckit("https://github.com/custom/repo", "v2.0.0")

            mock_session.set_speckit_config.assert_called_once()
            config_arg = mock_session.set_speckit_config.call_args[0][0]
            assert config_arg.enabled is True
            assert config_arg.url == "https://github.com/custom/repo"
            assert config_arg.version == "v2.0.0"

    async def test_enable_overwrites_existing(self):
        """Test that enabling overwrites existing configuration."""
        with patch("mcp_server_guide.services.speckit_manager.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session

            await enable_speckit("https://github.com/new/repo", "v3.0.0")

            mock_session.set_speckit_config.assert_called_once()
            config_arg = mock_session.set_speckit_config.call_args[0][0]
            assert config_arg.enabled is True
            assert config_arg.url == "https://github.com/new/repo"
            assert config_arg.version == "v3.0.0"


class TestUpdateSpeckitConfig:
    """Test update_speckit_config function."""

    async def test_update_existing_config(self):
        """Test updating existing SpecKit configuration."""
        existing_config = SpecKitConfig(enabled=True, url="https://github.com/old/repo", version="v1.0.0")

        with patch("mcp_server_guide.services.speckit_manager.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get_speckit_config.return_value = existing_config
            mock_session_class.return_value = mock_session

            await update_speckit_config({"version": "v2.0.0"})

            mock_session.set_speckit_config.assert_called_once()
            config_arg = mock_session.set_speckit_config.call_args[0][0]
            assert config_arg.version == "v2.0.0"
            assert config_arg.url == "https://github.com/old/repo"  # Should preserve existing

    async def test_update_nonexistent_config(self):
        """Test updating when no config exists."""
        with patch("mcp_server_guide.services.speckit_manager.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.get_speckit_config.return_value = None
            mock_session_class.return_value = mock_session

            await update_speckit_config({"enabled": True, "version": "v1.5.0"})

            mock_session.set_speckit_config.assert_called_once()
            config_arg = mock_session.set_speckit_config.call_args[0][0]
            assert config_arg.enabled is True
            assert config_arg.version == "v1.5.0"
