"""Pytest configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
from mcp_research_server.config import ServerConfig, set_config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def test_config(temp_dir):
    """Create a test configuration."""
    config = ServerConfig(
        base_dir=temp_dir,
        log_level="DEBUG",
        arxiv_max_results_default=3,
        arxiv_max_results_limit=10,
        create_dirs=True
    )
    set_config(config)
    return config
