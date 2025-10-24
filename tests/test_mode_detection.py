"""Tests for mode detection functionality - Updated for instruction-based approach."""

import pytest
from pathlib import Path
from mcp_server_guide.prompts import status_prompt


@pytest.fixture
def temp_dir(tmp_path):
    """Provide temporary directory for tests."""
    import os

    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old_cwd)


@pytest.mark.asyncio
async def test_status_provides_mode_detection_instructions(temp_dir):
    """Test that status prompt provides mode detection instructions."""
    result = await status_prompt()

    # Should provide instructions for mode detection
    assert "Mode Status Check" in result or "check" in result.lower()
    assert ".consent" in result
    assert ".issue" in result


@pytest.mark.asyncio
async def test_status_explains_mode_hierarchy(temp_dir):
    """Test that status explains the mode detection hierarchy."""
    result = await status_prompt()

    # Should explain the mode detection logic
    assert "Implementation" in result or "implementation" in result.lower()
    assert "Check" in result or "check" in result.lower()
    assert "Discussion" in result or "discussion" in result.lower()
    assert "Plan" in result or "plan" in result.lower()


@pytest.mark.asyncio
async def test_status_with_files_present_still_provides_instructions(temp_dir):
    """Test that status provides instructions regardless of file presence."""
    # Create files
    Path(".consent").write_text("implementation")
    Path(".issue").write_text("test.md")

    result = await status_prompt()

    # Should still provide instructions, not read files
    assert "Status Check" in result or "check" in result.lower()
    # Should not contain actual file contents since server doesn't read them
    assert "test.md" not in result or "Mode Status Check" in result


class TestCorruptedAndUnreadableFiles:
    """Test prompt robustness with corrupted or unreadable files."""

    @pytest.mark.asyncio
    async def test_status_with_corrupted_consent_file(self, temp_dir):
        """Test status prompt with corrupted .consent file."""
        # Create corrupted binary file
        Path(".consent").write_bytes(b"\x00\x01\x02\xff\xfe")

        result = await status_prompt()

        # Should still provide instructions
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Status" in result or "check" in result.lower()

    @pytest.mark.asyncio
    async def test_status_with_corrupted_issue_file(self, temp_dir):
        """Test status prompt with corrupted .issue file."""
        # Create corrupted binary file
        Path(".issue").write_bytes(b"\x00\x01\x02\xff\xfe")

        result = await status_prompt()

        # Should still provide instructions
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_status_with_unreadable_files(self, temp_dir):
        """Test status prompt when files exist but are unreadable."""
        import os

        # Skip on Windows as permission handling is different
        if os.name != "nt":
            # Create files with no read permissions
            consent_file = Path(".consent")
            issue_file = Path(".issue")

            consent_file.write_text("test")
            issue_file.write_text("test")

            consent_file.chmod(0o000)  # No permissions
            issue_file.chmod(0o000)  # No permissions

            result = await status_prompt()

            # Should still provide instructions since server doesn't read files
            assert isinstance(result, str)
            assert len(result) > 0

            # Restore permissions for cleanup
            consent_file.chmod(0o644)
            issue_file.chmod(0o644)

    @pytest.mark.asyncio
    async def test_status_with_directory_instead_of_file(self, temp_dir):
        """Test status prompt when .consent/.issue are directories instead of files."""
        # Create directories with same names as expected files
        Path(".consent").mkdir()
        Path(".issue").mkdir()

        result = await status_prompt()

        # Should still provide instructions
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_status_with_very_large_files(self, temp_dir):
        """Test status prompt with very large files."""
        # Create large files (server shouldn't read them anyway)
        large_content = "x" * 1000000  # 1MB of 'x'

        Path(".consent").write_text(large_content)
        Path(".issue").write_text(large_content)

        result = await status_prompt()

        # Should complete quickly since server doesn't read files
        assert isinstance(result, str)
        assert len(result) > 0
