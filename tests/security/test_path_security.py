"""Tests for path traversal security and file path validation."""

import pytest
import tempfile
from pathlib import Path
from mcp_server_guide.security.path_validator import PathValidator, SecurityError


class TestPathTraversalSecurity:
    """Test path traversal attack prevention."""

    def test_path_traversal_attack_blocked(self):
        """Test that path traversal attacks are blocked."""
        with tempfile.TemporaryDirectory() as temp_dir:
            allowed_root = Path(temp_dir).resolve()
            validator = PathValidator([allowed_root])

            # Test various path traversal attempts
            attack_paths = [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32",
                "../../sensitive/file.txt",
                "../outside.txt",
                "subdir/../../escape.txt",
            ]

            for attack_path in attack_paths:
                with pytest.raises(SecurityError, match="Path outside allowed boundaries"):
                    validator.validate_path(attack_path, allowed_root)

    def test_absolute_path_injection_blocked(self):
        """Test that absolute path injection is blocked."""
        with tempfile.TemporaryDirectory() as temp_dir:
            allowed_root = Path(temp_dir).resolve()
            validator = PathValidator([allowed_root])

            # Test absolute path injection attempts
            attack_paths = ["/etc/passwd", "/var/log/system.log", "/home/user/.ssh/id_rsa"]

            for attack_path in attack_paths:
                with pytest.raises(SecurityError, match="Path outside allowed boundaries"):
                    validator.validate_path(attack_path, allowed_root)

    def test_symlink_escape_blocked(self):
        """Test that symlink following cannot escape allowed boundaries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            allowed_root = Path(temp_dir).resolve()
            validator = PathValidator([allowed_root])

            # Create a symlink that points outside the allowed area
            outside_dir = Path(temp_dir).parent / "outside"
            outside_dir.mkdir(exist_ok=True)
            outside_file = outside_dir / "secret.txt"
            outside_file.write_text("secret data")

            symlink_path = allowed_root / "escape_link"
            symlink_path.symlink_to(outside_file)

            with pytest.raises(SecurityError, match="Path outside allowed boundaries"):
                validator.validate_path("escape_link", allowed_root)

    def test_valid_paths_allowed(self):
        """Test that valid paths within boundaries are allowed."""
        with tempfile.TemporaryDirectory() as temp_dir:
            allowed_root = Path(temp_dir).resolve()
            validator = PathValidator([allowed_root])

            # Create test files
            (allowed_root / "valid.txt").write_text("content")
            (allowed_root / "subdir").mkdir()
            (allowed_root / "subdir" / "nested.txt").write_text("nested content")

            valid_paths = [
                "valid.txt",
                "subdir/nested.txt",
                "./valid.txt",
                "subdir/../valid.txt",  # Resolves to valid.txt
            ]

            for valid_path in valid_paths:
                # Should not raise exception
                result = validator.validate_path(valid_path, allowed_root)
                assert result.is_absolute()
                # Check that result is within allowed_root
                assert validator._is_within_root(result, allowed_root)

    def test_multiple_allowed_roots(self):
        """Test validation with multiple allowed root directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root1 = Path(temp_dir).resolve() / "root1"
            root2 = Path(temp_dir).resolve() / "root2"
            outside_root = Path(temp_dir).resolve() / "outside"
            root1.mkdir()
            root2.mkdir()
            outside_root.mkdir()

            validator = PathValidator([root1, root2])

            # Create test files in both roots
            (root1 / "file1.txt").write_text("content1")
            (root2 / "file2.txt").write_text("content2")
            (outside_root / "outside.txt").write_text("outside content")

            # Both should be valid
            result1 = validator.validate_path("file1.txt", root1)
            result2 = validator.validate_path("file2.txt", root2)

            # Results should be within their respective roots
            assert validator._is_within_root(result1, root1)
            assert validator._is_within_root(result2, root2)

            # Cross-root access to another allowed root should work
            cross_result = validator.validate_path("../root2/file2.txt", root1)
            assert validator._is_within_root(cross_result, root2)

            # Access to outside root should be blocked
            with pytest.raises(SecurityError):
                validator.validate_path("../outside/outside.txt", root1)

    def test_empty_allowed_roots_blocks_all(self):
        """Test that empty allowed roots blocks all access."""
        validator = PathValidator([])

        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)

            with pytest.raises(SecurityError, match="Path outside allowed boundaries"):
                validator.validate_path("any_file.txt", base_path)

    def test_nonexistent_path_validation(self):
        """Test validation of nonexistent paths (should still validate bounds)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            allowed_root = Path(temp_dir).resolve()
            validator = PathValidator([allowed_root])

            # Valid nonexistent path should pass validation
            result = validator.validate_path("nonexistent.txt", allowed_root)
            assert validator._is_within_root(result, allowed_root)

            # Invalid nonexistent path should fail
            with pytest.raises(SecurityError):
                validator.validate_path("../nonexistent.txt", allowed_root)


class TestPathSanitization:
    """Test path sanitization utilities."""

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        from mcp_server_guide.security.path_validator import sanitize_filename

        test_cases = [
            ("normal.txt", "normal.txt"),
            ("file with spaces.txt", "file with spaces.txt"),
            ("../../../etc/passwd", "etc_passwd"),
            ("file\\with\\backslashes.txt", "file_with_backslashes.txt"),
            ("file/with/slashes.txt", "file_with_slashes.txt"),
            ("file:with:colons.txt", "file_with_colons.txt"),
            ("file<with>brackets.txt", "file_with_brackets.txt"),
            ("file|with|pipes.txt", "file_with_pipes.txt"),
            ('file"with"quotes.txt', "file_with_quotes.txt"),
            ("file*with*wildcards.txt", "file_with_wildcards.txt"),
        ]

        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            assert result == expected
            # Ensure no dangerous characters remain
            dangerous_chars = ["/", "\\", "..", ":", "<", ">", "|", '"', "*", "?"]
            assert not any(char in result for char in dangerous_chars if char != "..")

    def test_sanitize_empty_filename(self):
        """Test sanitization of empty or invalid filenames."""
        from mcp_server_guide.security.path_validator import sanitize_filename

        assert sanitize_filename("") == "unnamed"
        assert sanitize_filename("...") == "unnamed"
        assert sanitize_filename("../..") == "unnamed"
        assert sanitize_filename("   ") == "unnamed"
