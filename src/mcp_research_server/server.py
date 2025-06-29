"""Main MCP Research Server implementation."""

import sys
import traceback
from typing import List, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP

from .config import get_config
from .tools.arxiv_search import ArxivSearchTool, ArxivSearchError
from .tools.paper_info import PaperInfoTool, PaperInfoError
from .utils.logger import setup_logger, get_logger
from .models import ErrorResponse


class MCPResearchServer:
    """Main MCP Research Server class."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.logger = setup_logger("mcp_research_server", self.config)
        
        # Initialize tools
        self.arxiv_tool = ArxivSearchTool(self.config)
        self.paper_info_tool = PaperInfoTool(self.config)
        
        # Initialize FastMCP server
        self.mcp = FastMCP(self.config.server_name)
        
        # Register tools
        self._register_tools()
        
        self.logger.info(f"MCP Research Server initialized with name: {self.config.server_name}")
    
    def _register_tools(self):
        """Register all tools with the FastMCP server."""
        
        @self.mcp.tool()
        def search_papers(topic: str, max_results: int = 5) -> List[str]:
            """
            Search for papers on arXiv based on a topic and store their information.
            
            Args:
                topic: The topic to search for
                max_results: Maximum number of results to retrieve (default: 5, max: 50)
                
            Returns:
                List of paper IDs found in the search
            """
            try:
                self.logger.info(f"Tool called: search_papers(topic='{topic}', max_results={max_results})")
                
                # Validate inputs
                if not topic or not topic.strip():
                    raise ValueError("Topic cannot be empty")
                
                if max_results < 1:
                    raise ValueError("max_results must be at least 1")
                
                if max_results > self.config.arxiv_max_results_limit:
                    self.logger.warning(
                        f"max_results {max_results} exceeds limit {self.config.arxiv_max_results_limit}, "
                        f"using limit"
                    )
                    max_results = self.config.arxiv_max_results_limit
                
                # Perform search
                search_result = self.arxiv_tool.search_papers(topic.strip(), max_results)
                
                self.logger.info(
                    f"Search completed successfully: {len(search_result.paper_ids)} papers found"
                )
                
                return search_result.paper_ids
                
            except ArxivSearchError as e:
                self.logger.error(f"ArXiv search error: {e}")
                raise
            except ValueError as e:
                self.logger.error(f"Validation error in search_papers: {e}")
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error in search_papers: {e}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                raise RuntimeError(f"Search failed: {str(e)}")
        
        @self.mcp.tool()
        def extract_info(paper_id: str) -> str:
            """
            Search for information about a specific paper across all topic directories.
            
            Args:
                paper_id: The ID of the paper to look for
                
            Returns:
                JSON string with paper information if found, error message if not found
            """
            try:
                self.logger.info(f"Tool called: extract_info(paper_id='{paper_id}')")
                
                if not paper_id or not paper_id.strip():
                    raise ValueError("Paper ID cannot be empty")
                
                result = self.paper_info_tool.extract_info(paper_id.strip())
                
                self.logger.info(f"Info extraction completed for paper {paper_id}")
                return result
                
            except PaperInfoError as e:
                self.logger.error(f"Paper info error: {e}")
                raise
            except ValueError as e:
                self.logger.error(f"Validation error in extract_info: {e}")
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error in extract_info: {e}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                raise RuntimeError(f"Info extraction failed: {str(e)}")
        
        @self.mcp.tool()
        def get_database_stats() -> str:
            """
            Get statistics about the entire paper database.
            
            Returns:
                JSON string with database statistics
            """
            try:
                self.logger.info("Tool called: get_database_stats()")
                
                stats = self.paper_info_tool.get_database_stats()
                
                import json
                return json.dumps(stats, indent=self.config.json_indent, ensure_ascii=False)
                
            except Exception as e:
                self.logger.error(f"Error in get_database_stats: {e}")
                error = ErrorResponse(
                    error=f"Failed to get database stats: {str(e)}",
                    error_type="InternalError"
                )
                import json
                return json.dumps(error.dict(), indent=self.config.json_indent)
    
    def run(self, transport: Optional[str] = None):
        """Run the MCP server."""
        transport = transport or self.config.transport
        
        self.logger.info(f"Starting MCP Research Server with transport: {transport}")
        
        try:
            self.mcp.run(transport=transport)
        except KeyboardInterrupt:
            self.logger.info("Server shutdown requested by user")
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        finally:
            self.logger.info("MCP Research Server stopped")


def main():
    """Main entry point for the server."""
    try:
        # Initialize configuration
        config = get_config()
        
        # Create and run server
        server = MCPResearchServer(config)
        server.run()
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to start server: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
