"""MCP Research Server - A production-ready ArXiv research tool for Model Context Protocol."""

from .config import get_config, ServerConfig
from .server import MCPResearchServer
from .models import PaperInfo, Author, SearchResult, PaperDatabase
from .tools.arxiv_search import ArxivSearchTool
from .tools.paper_info import PaperInfoTool

__version__ = "1.0.0"
__author__ = "MCP Research Server Team"
__email__ = "your-email@example.com"
__description__ = "Production-ready MCP server for ArXiv paper research"

__all__ = [
    "MCPResearchServer",
    "get_config",
    "ServerConfig", 
    "PaperInfo",
    "Author",
    "SearchResult", 
    "PaperDatabase",
    "ArxivSearchTool",
    "PaperInfoTool",
]
