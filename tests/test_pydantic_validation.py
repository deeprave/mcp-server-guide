"""Tests for Pydantic validation in project_config.py"""

import pytest
from pydantic import ValidationError

from mcp_server_guide.project_config import ProjectConfig, ConfigFile
from mcp_server_guide.models.category import Category


def test_category_empty_dir():
    """Test Category validation with empty directory"""
    with pytest.raises(ValidationError, match="Directory path cannot be empty"):
        Category(dir="", patterns=["*.md"], description="test")


def test_category_leading_slash_removal():
    """Test Category validation removes leading slash"""
    category = Category(dir="/some/path", patterns=["*.md"], description="test")
    assert category.dir == "some/path/"


def test_category_empty_description_allowed():
    """Test Category validation allows empty description"""
    category = Category(dir="path", patterns=["*.md"], description="")
    assert category.description == ""  # Should be allowed and normalized


def test_project_config_empty_name():
    """Test ConfigFile validation rejects empty project names"""
    # Project names are validated as keys in ConfigFile.projects dict
    with pytest.raises(ValidationError, match="Project name cannot be empty"):
        ConfigFile(projects={"": ProjectConfig(categories={})})


def test_project_config_invalid_categories():
    """Test ProjectConfig validation with invalid categories"""
    with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
        ProjectConfig(categories="invalid")


def test_config_file_invalid_projects():
    """Test ConfigFile validation with invalid projects"""
    with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
        ConfigFile(projects="invalid")


def test_category_invalid_patterns():
    """Test Category validation with invalid patterns"""
    with pytest.raises(ValidationError, match="Input should be a valid string"):
        Category(dir="path", patterns=[123], description="test")


def test_project_config_docroot_validation():
    """Test ConfigFile docroot validation"""
    config = ConfigFile(docroot=None)
    assert config.docroot == "."  # Should default to current directory


def test_config_file_docroot_path_traversal():
    """Test ConfigFile docroot path traversal validation"""
    with pytest.raises(ValidationError, match="Global document root cannot contain path traversal sequences"):
        ConfigFile(docroot="../dangerous")


def test_config_file_empty_docroot():
    """Test ConfigFile empty docroot validation"""
    config = ConfigFile(docroot="  ")  # Empty/whitespace string
    assert config.docroot == "."  # Should default to current directory


def test_category_empty_patterns():
    """Test Category validation with empty patterns in list"""
    with pytest.raises(ValidationError, match="File patterns cannot be empty"):
        Category(dir="path", patterns=[""], description="test")


def test_category_path_traversal_patterns():
    """Test Category validation with path traversal in patterns"""
    with pytest.raises(ValidationError, match="File patterns cannot contain path traversal sequences"):
        Category(dir="path", patterns=["../dangerous"], description="test")


def test_category_long_description_allowed():
    """Test Category validation allows long descriptions"""
    long_desc = "x" * 500  # Long description should be allowed
    category = Category(dir="path", patterns=["*.md"], description=long_desc)
    assert category.description == long_desc  # Should be preserved


def test_category_no_description_provided():
    """Test Category can be created without providing description"""
    category = Category(dir="path", patterns=["*.md"])
    assert category.description == ""  # Should default to empty string
