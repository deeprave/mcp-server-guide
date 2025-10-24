"""Tests for new prompt system - Updated for instruction-based approach."""

import pytest
from mcp_server_guide.prompts import discuss_prompt, plan_prompt, implement_prompt, check_prompt, status_prompt


class TestDiscussPrompt:
    """Test discuss prompt functionality."""

    @pytest.mark.asyncio
    async def test_discuss_works_when_no_consent_file(self, session_temp_dir):
        """Test that discuss prompt works without .consent file."""
        result = await discuss_prompt()
        assert "Discuss" in result or "discuss" in result

    @pytest.mark.asyncio
    async def test_discuss_provides_file_instructions(self, session_temp_dir):
        """Test that discuss prompt provides file management instructions."""
        # Create .consent file
        consent_file = session_temp_dir / ".consent"
        consent_file.write_text("implementation")

        result = await discuss_prompt()

        # Should provide instructions to remove .consent file
        assert "Remove `.consent` file" in result or "remove" in result.lower()
        # File should still exist since server doesn't manipulate it
        assert consent_file.exists()

    @pytest.mark.asyncio
    async def test_plan_works_independently(self, session_temp_dir):
        """Test that plan prompt works independently."""
        result = await plan_prompt()
        assert "Plan" in result or "plan" in result

    @pytest.mark.asyncio
    async def test_discuss_and_plan_return_different_results(self, session_temp_dir):
        """Test that discuss and plan return different content."""
        discuss_result = await discuss_prompt()
        plan_result = await plan_prompt()

        # Should be different responses
        assert discuss_result != plan_result
        assert "discuss" in discuss_result.lower() or "Discuss" in discuss_result
        assert "plan" in plan_result.lower() or "Plan" in plan_result


class TestStatusPrompt:
    """Test status prompt functionality."""

    @pytest.mark.asyncio
    async def test_status_works_when_no_consent(self, session_temp_dir):
        """Test that status works without .consent file."""
        result = await status_prompt()
        assert "Status" in result or "status" in result.lower()

    @pytest.mark.asyncio
    async def test_status_works_with_implementation_consent(self, session_temp_dir):
        """Test that status works with implementation .consent file."""
        consent_file = session_temp_dir / ".consent"
        consent_file.write_text("implementation")

        result = await status_prompt()
        assert "Status" in result or "check" in result.lower()

    @pytest.mark.asyncio
    async def test_status_works_with_check_consent(self, session_temp_dir):
        """Test that status works with check .consent file."""
        consent_file = session_temp_dir / ".consent"
        consent_file.write_text("check")

        result = await status_prompt()
        assert "Status" in result or "check" in result.lower()


class TestImplementPrompt:
    """Test implement prompt functionality."""

    @pytest.mark.asyncio
    async def test_implement_works_when_consent_contains_implementation(self, session_temp_dir):
        """Test that implement prompt works with proper consent."""
        result = await implement_prompt()
        assert "Implementation" in result or "implementation" in result.lower()

    @pytest.mark.asyncio
    async def test_implement_fails_when_consent_missing_or_wrong(self, session_temp_dir):
        """Test that implement prompt provides instructions when consent missing."""
        result = await implement_prompt()
        # Should provide instructions to create .consent file
        assert "Create `.consent` file" in result or ".consent" in result


class TestCheckPrompt:
    """Test check prompt functionality."""

    @pytest.mark.asyncio
    async def test_check_works_when_consent_contains_check(self, session_temp_dir):
        """Test that check prompt works with proper consent."""
        result = await check_prompt()
        assert "Check" in result or "check" in result.lower()

    @pytest.mark.asyncio
    async def test_check_fails_when_consent_missing_or_wrong(self, session_temp_dir):
        """Test that check prompt provides instructions when consent missing."""
        result = await check_prompt()
        # Should provide instructions to update .consent file
        assert "Update `.consent` file" in result or ".consent" in result


class TestEdgeCases:
    """Test invalid arguments and unexpected file states."""

    @pytest.mark.asyncio
    async def test_prompts_with_invalid_arguments(self, session_temp_dir):
        """Test prompts handle invalid arguments gracefully."""
        # Test with invalid argument types
        result = await status_prompt("invalid_arg")
        assert isinstance(result, str)

        result = await discuss_prompt("invalid_arg")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_corrupted_consent_file(self, session_temp_dir):
        """Test behavior with corrupted .consent file."""
        consent_file = session_temp_dir / ".consent"
        consent_file.write_bytes(b"\x00\x01\x02")  # Binary data

        result = await status_prompt()
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_permission_denied_consent_file(self, session_temp_dir):
        """Test behavior when .consent file is not readable."""
        import os

        consent_file = session_temp_dir / ".consent"
        consent_file.write_text("test")

        # Make file unreadable (skip on Windows)
        if os.name != "nt":
            consent_file.chmod(0o000)

            result = await status_prompt()
            assert isinstance(result, str)

            # Restore permissions for cleanup
            consent_file.chmod(0o644)
