"""Tests for file handler utilities."""

import pytest
from mcp_research_server.utils.file_handler import FileHandler


class TestFileHandler:
    """Test cases for FileHandler."""
    
    def test_init(self, test_config):
        """Test file handler initialization."""
        handler = FileHandler(test_config)
        assert handler.config == test_config
        assert handler.papers_dir == test_config.papers_dir
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        sanitized = FileHandler._sanitize_filename("Machine Learning & AI")
        assert sanitized == "machine_learning_ai"
