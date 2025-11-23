"""Tests for kiro_install script."""

import stat
from unittest.mock import patch

import pytest
from anyio import Path as AsyncPath
from click.testing import CliRunner


class TestKiroCliCheck:
    """Test kiro-cli installation check."""

    def test_kiro_cli_not_installed(self):
        """Test that script fails if kiro-cli not in PATH."""
        from kiro_install import check_kiro_cli_installed

        with patch("shutil.which", return_value=None):
            assert check_kiro_cli_installed() is False

    def test_kiro_cli_installed(self):
        """Test that script succeeds if kiro-cli in PATH."""
        from kiro_install import check_kiro_cli_installed

        with patch("shutil.which", return_value="/usr/local/bin/kiro-cli"):
            assert check_kiro_cli_installed() is True


class TestDirectoryCreation:
    """Test directory creation."""

    @pytest.mark.asyncio
    async def test_create_directories(self, tmp_path):
        """Test that all required directories are created."""
        from kiro_install import create_directories

        base_path = AsyncPath(tmp_path / ".kiro")
        await create_directories(base_path)

        assert await base_path.exists()
        assert await (base_path / "agents").exists()
        assert await (base_path / "scripts").exists()
        assert await (base_path / "scripts" / "consent").exists()
        assert await (base_path / "scripts" / "review").exists()


class TestFileOperations:
    """Test file comparison and copying."""

    @pytest.mark.asyncio
    async def test_files_are_identical_when_same(self, tmp_path):
        """Test that identical files are detected."""
        from kiro_install import files_are_identical

        src = AsyncPath(tmp_path / "src.txt")
        dst = AsyncPath(tmp_path / "dst.txt")

        await src.write_text("test content")
        await dst.write_text("test content")

        assert await files_are_identical(src, dst) is True

    @pytest.mark.asyncio
    async def test_files_are_not_identical_when_different(self, tmp_path):
        """Test that different files are detected."""
        from kiro_install import files_are_identical

        src = AsyncPath(tmp_path / "src.txt")
        dst = AsyncPath(tmp_path / "dst.txt")

        await src.write_text("content A")
        await dst.write_text("content B")

        assert await files_are_identical(src, dst) is False

    @pytest.mark.asyncio
    async def test_files_not_identical_when_dst_missing(self, tmp_path):
        """Test that missing destination is not identical."""
        from kiro_install import files_are_identical

        src = AsyncPath(tmp_path / "src.txt")
        dst = AsyncPath(tmp_path / "dst.txt")

        await src.write_text("content")

        assert await files_are_identical(src, dst) is False

    @pytest.mark.asyncio
    async def test_copy_file_skips_identical(self, tmp_path):
        """Test that identical files are skipped."""
        from kiro_install import copy_file_if_needed

        src = AsyncPath(tmp_path / "src.txt")
        dst = AsyncPath(tmp_path / "dst.txt")

        await src.write_text("same content")
        await dst.write_text("same content")

        await copy_file_if_needed(src, dst, auto_yes=False)

        # File should remain unchanged
        assert await dst.read_text() == "same content"

    @pytest.mark.asyncio
    async def test_copy_file_with_auto_yes(self, tmp_path):
        """Test that --yes flag bypasses prompts."""
        from kiro_install import copy_file_if_needed

        src = AsyncPath(tmp_path / "src.txt")
        dst = AsyncPath(tmp_path / "dst.txt")

        await src.write_text("new content")
        await dst.write_text("old content")

        await copy_file_if_needed(src, dst, auto_yes=True)

        assert await dst.read_text() == "new content"

    @pytest.mark.asyncio
    async def test_prompt_user_confirmation_yes(self, tmp_path):
        """Test user confirmation with yes response."""
        from kiro_install import prompt_user_confirmation

        file_path = AsyncPath(tmp_path / "test.txt")

        with patch("builtins.input", return_value="y"):
            assert await prompt_user_confirmation(file_path) is True

    @pytest.mark.asyncio
    async def test_prompt_user_confirmation_no(self, tmp_path):
        """Test user confirmation with no response."""
        from kiro_install import prompt_user_confirmation

        file_path = AsyncPath(tmp_path / "test.txt")

        with patch("builtins.input", return_value="n"):
            assert await prompt_user_confirmation(file_path) is False


class TestDirectoryCopying:
    """Test recursive directory copying."""

    @pytest.mark.asyncio
    async def test_copy_directory_recursive(self, tmp_path):
        """Test that directories are copied recursively."""
        from kiro_install import copy_directory

        src = AsyncPath(tmp_path / "src")
        dst = AsyncPath(tmp_path / "dst")

        await src.mkdir()
        await (src / "file1.txt").write_text("content1")
        await (src / "subdir").mkdir()
        await (src / "subdir" / "file2.txt").write_text("content2")

        await copy_directory(src, dst, auto_yes=True)

        assert await (dst / "file1.txt").exists()
        assert await (dst / "subdir" / "file2.txt").exists()
        assert await (dst / "file1.txt").read_text() == "content1"
        assert await (dst / "subdir" / "file2.txt").read_text() == "content2"

    @pytest.mark.asyncio
    async def test_make_executable(self, tmp_path):
        """Test that files are made executable."""
        from kiro_install import make_executable

        file_path = AsyncPath(tmp_path / "script.sh")
        await file_path.write_text("#!/bin/bash\necho test")

        await make_executable(file_path)

        file_stat = await file_path.stat()
        assert file_stat.st_mode & stat.S_IXUSR
        assert file_stat.st_mode & stat.S_IXGRP
        assert file_stat.st_mode & stat.S_IXOTH

    @pytest.mark.asyncio
    async def test_copy_directory_with_executable(self, tmp_path):
        """Test that scripts are made executable when copied."""
        from kiro_install import copy_directory

        src = AsyncPath(tmp_path / "src")
        dst = AsyncPath(tmp_path / "dst")

        await src.mkdir()
        await (src / "script.sh").write_text("#!/bin/bash\necho test")

        await copy_directory(src, dst, auto_yes=True, make_scripts_executable=True)

        file_stat = await (dst / "script.sh").stat()
        assert file_stat.st_mode & stat.S_IXUSR


class TestClickCommand:
    """Test Click command interface."""

    def test_click_command_with_yes_flag(self):
        """Test Click command accepts --yes flag."""
        from kiro_install import main

        runner = CliRunner()
        with patch("shutil.which", return_value=None):
            result = runner.invoke(main, ["--yes"])
            assert result.exit_code == 1
            assert "kiro-cli not found" in result.output

    def test_click_command_with_y_flag(self):
        """Test Click command accepts -y flag."""
        from kiro_install import main

        runner = CliRunner()
        with patch("shutil.which", return_value=None):
            result = runner.invoke(main, ["-y"])
            assert result.exit_code == 1
            assert "kiro-cli not found" in result.output

    def test_click_command_with_verbose_flag(self):
        """Test Click command accepts --verbose flag."""
        from kiro_install import main

        runner = CliRunner()
        with patch("shutil.which", return_value=None):
            result = runner.invoke(main, ["--verbose"])
            assert result.exit_code == 1
            assert "kiro-cli not found" in result.output

    def test_click_command_with_v_flag(self):
        """Test Click command accepts -v flag."""
        from kiro_install import main

        runner = CliRunner()
        with patch("shutil.which", return_value=None):
            result = runner.invoke(main, ["-v"])
            assert result.exit_code == 1
            assert "kiro-cli not found" in result.output

    def test_click_command_with_both_flags(self):
        """Test Click command accepts both --yes and --verbose flags."""
        from kiro_install import main

        runner = CliRunner()
        with patch("shutil.which", return_value=None):
            result = runner.invoke(main, ["--yes", "--verbose"])
            assert result.exit_code == 1
            assert "kiro-cli not found" in result.output

    def test_help_flag(self):
        """Test that --help flag works."""
        from kiro_install import main

        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Install Kiro configuration files" in result.output

    def test_h_flag(self):
        """Test that -h flag works."""
        from kiro_install import main

        runner = CliRunner()
        result = runner.invoke(main, ["-h"])
        assert result.exit_code == 0
        assert "Install Kiro configuration files" in result.output


class TestMainFlow:
    """Test main flow orchestration."""

    def test_cli_main_exits_on_missing_kiro_cli(self):
        """Test that script exits if kiro-cli not found."""
        from kiro_install import main

        runner = CliRunner()
        with patch("shutil.which", return_value=None):
            result = runner.invoke(main, ["--yes"])
            assert result.exit_code == 1
            assert "kiro-cli not found" in result.output
