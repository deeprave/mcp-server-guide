"""Tests for DAIC command functionality."""

import pytest
from mcp_server_guide.server import mcp
from mcp.types import GetPromptResult


@pytest.mark.asyncio
async def test_daic_prompt_returns_current_state(tmp_path, monkeypatch):
    """Test that @daic returns current DAIC state."""
    from mcp_server_guide.client_path import ClientPath

    # Mock ClientPath to be initialized and return the test directory
    monkeypatch.setattr(ClientPath, "_initialized", True)
    monkeypatch.setattr(ClientPath, "_primary_root", tmp_path)

    # Test ENABLED state (no .consent file)
    consent_file = tmp_path / ".consent"
    if consent_file.exists():
        consent_file.unlink()

    result = await mcp.get_prompt("daic", {})
    assert isinstance(result, GetPromptResult)
    assert len(result.messages) > 0
    assert "DAIC mode: ENABLED (Discussion-Alignment-Implementation-Check)" in result.messages[0].content.text

    # Test DISABLED state (.consent file exists)
    consent_file.touch()

    result = await mcp.get_prompt("daic", {})
    assert isinstance(result, GetPromptResult)
    assert len(result.messages) > 0
    assert "DAIC mode: DISABLED (Implementation allowed)" in result.messages[0].content.text


@pytest.mark.asyncio
async def test_daic_prompt_error_when_client_dir_none(monkeypatch):
    """Test that @daic returns error when ClientPath.get_primary_root returns None."""
    from mcp_server_guide.client_path import ClientPath

    # Mock ClientPath to be initialized and return None
    monkeypatch.setattr(ClientPath, "_initialized", True)
    monkeypatch.setattr(ClientPath, "_primary_root", None)

    result = await mcp.get_prompt("daic", {})
    assert isinstance(result, GetPromptResult)
    assert len(result.messages) > 0
    assert "Error: Client working directory not available" in result.messages[0].content.text


@pytest.mark.asyncio
async def test_daic_prompt_with_custom_message(tmp_path, monkeypatch):
    """Test that @daic properly handles custom disable messages."""
    from mcp_server_guide.client_path import ClientPath

    # Mock ClientPath to be initialized and return the test directory
    monkeypatch.setattr(ClientPath, "_initialized", True)
    monkeypatch.setattr(ClientPath, "_primary_root", tmp_path)

    # Test custom disable message with multiple words
    result = await mcp.get_prompt("daic", {"arg": "Custom disable message with multiple words"})
    assert isinstance(result, GetPromptResult)
    assert len(result.messages) > 0
    assert "DAIC mode: DISABLED - Custom disable message with multiple words" in result.messages[0].content.text

    # Verify .consent file was created
    consent_file = tmp_path / ".consent"
    assert consent_file.exists()


@pytest.mark.asyncio
async def test_daic_prompt_disable_action(tmp_path, monkeypatch):
    """Test that @daic with any argument disables DAIC mode."""
    from mcp_server_guide.client_path import ClientPath

    # Mock ClientPath to be initialized and return the test directory
    monkeypatch.setattr(ClientPath, "_initialized", True)
    monkeypatch.setattr(ClientPath, "_primary_root", tmp_path)

    # Test disable action with simple message
    result = await mcp.get_prompt("daic", {"arg": "working on feature X"})
    assert isinstance(result, GetPromptResult)
    assert len(result.messages) > 0
    assert "DAIC mode: DISABLED - working on feature X" in result.messages[0].content.text

    # Verify .consent file was created
    consent_file = tmp_path / ".consent"
    assert consent_file.exists()

@pytest.mark.asyncio
async def test_daic_prompt_enable_with_on(tmp_path, monkeypatch):
    """Test that @daic on enables DAIC mode."""
    from mcp_server_guide.client_path import ClientPath

    # Mock ClientPath to be initialized and return the test directory
    monkeypatch.setattr(ClientPath, "_initialized", True)
    monkeypatch.setattr(ClientPath, "_primary_root", tmp_path)

    # Create .consent file first (DAIC disabled)
    consent_file = tmp_path / ".consent"
    consent_file.touch()
    assert consent_file.exists()

    # Test enable with "on"
    result = await mcp.get_prompt("daic", {"arg": "on"})
    assert isinstance(result, GetPromptResult)
    assert len(result.messages) > 0
    assert "DAIC mode: ENABLED (Discussion-Alignment-Implementation-Check)" in result.messages[0].content.text

    # Verify .consent file was removed
    assert not consent_file.exists()


@pytest.mark.asyncio
async def test_daic_prompt_enable_with_true(tmp_path, monkeypatch):
    """Test that @daic true enables DAIC mode."""
    from mcp_server_guide.client_path import ClientPath

    # Mock ClientPath to be initialized and return the test directory
    monkeypatch.setattr(ClientPath, "_initialized", True)
    monkeypatch.setattr(ClientPath, "_primary_root", tmp_path)

    # Create .consent file first (DAIC disabled)
    consent_file = tmp_path / ".consent"
    consent_file.touch()
    assert consent_file.exists()

    # Test enable with "true"
    result = await mcp.get_prompt("daic", {"arg": "true"})
    assert isinstance(result, GetPromptResult)
    assert len(result.messages) > 0
    assert "DAIC mode: ENABLED (Discussion-Alignment-Implementation-Check)" in result.messages[0].content.text

    # Verify .consent file was removed
    assert not consent_file.exists()
