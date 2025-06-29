"""Tests for ArXiv search tool."""

import pytest
from mcp_research_server.tools.arxiv_search import ArxivSearchTool


class TestArxivSearchTool:
    """Test cases for ArxivSearchTool."""
    
    def test_init(self, test_config):
        """Test tool initialization."""
        tool = ArxivSearchTool(test_config)
        assert tool.config == test_config
        assert tool.file_handler is not None
