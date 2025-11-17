"""Tests for error handling in project_config.py"""

import tempfile
import os
from unittest.mock import patch
import pytest
import yaml
from pathlib import Path

from mcp_server_guide.project_config import ProjectConfig, _save_config_locked


@pytest.mark.asyncio
async def test_yaml_parse_error():
    """Test handling of invalid YAML in _save_config_locked"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("invalid: yaml: content: [")
        config_file = Path(f.name)

    try:
        config = ProjectConfig(categories={})
        await _save_config_locked(config_file, "test", config)
        # Should succeed by creating new config
        assert config_file.exists()
    finally:
        os.unlink(config_file)


@pytest.mark.asyncio
async def test_yaml_serialization_error():
    """Test handling of YAML serialization errors in _save_config_locked"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("docroot: /test/docs")
        config_file = Path(f.name)

    try:
        with patch("yaml.dump") as mock_dump:
            mock_dump.side_effect = yaml.YAMLError("Serialization failed")

            config = ProjectConfig(categories={})
            with pytest.raises(ValueError, match="Cannot serialize configuration to YAML"):
                await _save_config_locked(config_file, "test", config)
    finally:
        os.unlink(config_file)


@pytest.mark.asyncio
async def test_validation_error():
    """Test handling of Pydantic validation errors in _save_config_locked"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("projects:\n  test:\n    categories:\n      invalid: data")
        config_file = Path(f.name)

    try:
        config = ProjectConfig(categories={})
        await _save_config_locked(config_file, "test", config)
        # Should succeed by creating new config
        assert config_file.exists()
    finally:
        os.unlink(config_file)
