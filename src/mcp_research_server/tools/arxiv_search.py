"""ArXiv search tool for MCP Research Server."""

import arxiv
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from ..config import get_config
from ..models import PaperInfo, Author, SearchRequest, SearchResult, PaperDatabase
from ..utils.logger import get_logger, LoggerMixin, log_execution_time
from ..utils.file_handler import FileHandler


class ArxivSearchError(Exception):
    """Custom exception for ArXiv search errors."""
    pass


class ArxivSearchTool(LoggerMixin):
    """Tool for searching papers on ArXiv."""
    
    def __init__(self, config: Optional[object] = None):
        self.config = config or get_config()
        self.file_handler = FileHandler(config)
        self.client = arxiv.Client()
    
    @log_execution_time
    def search_papers(
        self, 
        topic: str, 
        max_results: Optional[int] = None
    ) -> SearchResult:
        """
        Search for papers on arXiv and store their information.
        
        Args:
            topic: The topic to search for
            max_results: Maximum number of results to retrieve
            
        Returns:
            SearchResult with paper IDs and metadata
            
        Raises:
            ArxivSearchError: If search fails
        """
        # Validate input
        if max_results is None:
            max_results = self.config.arxiv_max_results_default
        
        request = SearchRequest(topic=topic, max_results=max_results)
        
        # Ensure max_results doesn't exceed limit
        if request.max_results > self.config.arxiv_max_results_limit:
            self.logger.warning(
                f"Requested {request.max_results} results, limiting to {self.config.arxiv_max_results_limit}"
            )
            request.max_results = self.config.arxiv_max_results_limit
        
        self.logger.info(f"Searching ArXiv for '{request.topic}' with max_results={request.max_results}")
        
        try:
            # Perform ArXiv search
            search = arxiv.Search(
                query=request.topic,
                max_results=request.max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            papers = self.client.results(search)
            
            # Load existing database
            database = self.file_handler.load_papers_database(request.topic)
            
            # Process search results
            paper_ids = []
            new_papers_count = 0
            
            for paper in papers:
                paper_id = paper.get_short_id()
                paper_ids.append(paper_id)
                
                # Check if paper already exists
                if not database.has_paper(paper_id):
                    paper_info = self._convert_arxiv_paper(paper)
                    database.add_paper(paper_info)
                    new_papers_count += 1
                    self.logger.debug(f"Added new paper: {paper_id} - {paper.title}")
                else:
                    self.logger.debug(f"Paper already exists: {paper_id}")
            
            # Save updated database
            saved_path = self.file_handler.save_papers_database(request.topic, database)
            
            result = SearchResult(
                topic=request.topic,
                paper_ids=paper_ids,
                total_found=len(paper_ids),
                saved_to=str(saved_path),
                timestamp=datetime.now()
            )
            
            self.logger.info(
                f"Search completed: {len(paper_ids)} papers found, "
                f"{new_papers_count} new papers added"
            )
            
            return result
            
        except Exception as e:
            error_msg = f"ArXiv search failed for topic '{request.topic}': {str(e)}"
            self.logger.error(error_msg)
            raise ArxivSearchError(error_msg) from e
    
    def _convert_arxiv_paper(self, paper: arxiv.Result) -> PaperInfo:
        """Convert an ArXiv paper result to PaperInfo model."""
        try:
            # Convert authors
            authors = [Author(name=author.name) for author in paper.authors]
            
            # Extract category (primary category)
            category = None
            if paper.categories:
                category = paper.categories[0] if isinstance(paper.categories, list) else str(paper.categories)
            
            paper_info = PaperInfo(
                paper_id=paper.get_short_id(),
                title=paper.title.strip(),
                authors=authors,
                summary=paper.summary.strip(),
                pdf_url=paper.pdf_url,
                published=paper.published.date(),
                category=category,
                updated=paper.updated.date() if paper.updated else None,
                doi=paper.doi
            )
            
            return paper_info
            
        except Exception as e:
            self.logger.error(f"Failed to convert ArXiv paper {paper.get_short_id()}: {e}")
            raise
