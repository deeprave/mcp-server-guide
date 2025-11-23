"""Tests for SpecKit configuration management."""

from mcp_server_guide.models.config_file import ConfigFile


class TestSpecKitConfig:
    """Test SpecKit configuration in ConfigFile model."""

    def test_config_file_has_speckit_fields(self):
        """Test that ConfigFile model has speckit configuration fields."""
        # Test default state (disabled)
        config = ConfigFile()

        # Should have speckit field
        assert hasattr(config, "speckit")

        # Default should be None (disabled)
        assert config.speckit is None

    def test_speckit_config_structure(self):
        """Test speckit configuration structure."""
        from mcp_server_guide.models.speckit_config import SpecKitConfig

        # Test enabled speckit config
        speckit_config = SpecKitConfig(enabled=True, url="https://github.com/spec-kit/spec-kit", version="v1.2.3")

        assert speckit_config.enabled is True
        assert speckit_config.url == "https://github.com/spec-kit/spec-kit"
        assert speckit_config.version == "v1.2.3"

    def test_config_file_with_speckit(self):
        """Test ConfigFile with speckit configuration."""
        from mcp_server_guide.models.speckit_config import SpecKitConfig

        speckit_config = SpecKitConfig(enabled=True, url="https://github.com/spec-kit/spec-kit", version="v1.2.3")

        config = ConfigFile(speckit=speckit_config)

        assert config.speckit is not None
        assert config.speckit.enabled is True
        assert config.speckit.url == "https://github.com/spec-kit/spec-kit"
        assert config.speckit.version == "v1.2.3"

    def test_speckit_config_defaults(self):
        """Test SpecKit configuration default values."""
        from mcp_server_guide.models.speckit_config import SpecKitConfig

        # Test with defaults
        speckit_config = SpecKitConfig(enabled=True)

        assert speckit_config.enabled is True
        assert speckit_config.url == "https://github.com/spec-kit/spec-kit"  # Default
        assert speckit_config.version == "latest"  # Default

    async def test_speckit_state_detection_disabled(self):
        """Test detection of disabled SpecKit state."""
        from unittest.mock import AsyncMock, patch

        from mcp_server_guide.services.speckit_manager import is_speckit_enabled

        # Mock SessionManager to return disabled state
        with patch("mcp_server_guide.services.speckit_manager.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.is_speckit_enabled.return_value = False
            mock_session_class.return_value = mock_session

            result = await is_speckit_enabled()
            assert result is False

    async def test_speckit_state_detection_enabled(self):
        """Test detection of enabled SpecKit state."""
        from unittest.mock import AsyncMock, patch

        from mcp_server_guide.services.speckit_manager import is_speckit_enabled

        # Mock SessionManager to return enabled state
        with patch("mcp_server_guide.services.speckit_manager.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.is_speckit_enabled.return_value = True
            mock_session_class.return_value = mock_session

            result = await is_speckit_enabled()
            assert result is True

    async def test_speckit_state_detection_explicitly_disabled(self):
        """Test detection when SpecKit is explicitly disabled."""
        from unittest.mock import AsyncMock, patch

        from mcp_server_guide.services.speckit_manager import is_speckit_enabled

        # Mock SessionManager to return disabled state
        with patch("mcp_server_guide.services.speckit_manager.SessionManager") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.is_speckit_enabled.return_value = False
            mock_session_class.return_value = mock_session

            result = await is_speckit_enabled()
            assert result is False
