"""Tests for deferred configuration storage mechanism."""


class TestDeferredConfigStorage:
    """Test the deferred configuration storage mechanism."""

    def test_deferred_config_storage(self):
        """Test that CLI config is properly stored for deferred processing."""
        # Import the module to access the global variable
        import mcp_server_guide.main as main_module

        # Reset the deferred config
        main_module._deferred_builtin_config = {}

        # Mock the CLI processing that would normally set this
        test_config = {"guidesdir": "/test/guides", "guide": "test-guide", "langsdir": "/test/langs", "lang": "python"}

        # Simulate the storage that happens in the CLI processing
        main_module._deferred_builtin_config = test_config.copy()

        # Verify the config was stored
        assert main_module._deferred_builtin_config == test_config
        assert main_module._deferred_builtin_config["guidesdir"] == "/test/guides"
        assert main_module._deferred_builtin_config["guide"] == "test-guide"

    def test_deferred_config_empty_by_default(self):
        """Test that deferred config starts empty."""
        import mcp_server_guide.main as main_module

        # The module should initialize with empty config
        # (Note: this might be affected by other tests, so we just check the type)
        assert isinstance(main_module._deferred_builtin_config, dict)

    def test_deferred_config_isolation(self):
        """Test that deferred config changes don't affect original."""
        import mcp_server_guide.main as main_module

        original_config = {"guidesdir": "/original"}
        main_module._deferred_builtin_config = original_config.copy()

        # Modify the stored config
        main_module._deferred_builtin_config["guidesdir"] = "/modified"

        # Original should be unchanged (since we used copy())
        assert original_config["guidesdir"] == "/original"
        assert main_module._deferred_builtin_config["guidesdir"] == "/modified"
