"""Paper information extraction tool for MCP Research Server."""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..config import get_config
from ..models import PaperInfo, ErrorResponse
from ..utils.logger import get_logger, LoggerMixin, log_execution_time
from ..utils.file_handler import FileHandler


class PaperInfoError(Exception):
    """Custom exception for paper information errors."""
    pass


class PaperInfoTool(LoggerMixin):
    """Tool for extracting and managing paper information."""
    
    def __init__(self, config: Optional[object] = None):
        self.config = config or get_config()
        self.file_handler = FileHandler(config)
    
    @log_execution_time
    def extract_info(self, paper_id: str) -> str:
        """
        Extract information about a specific paper from stored data.
        
        Args:
            paper_id: The ID of the paper to look for
            
        Returns:
            JSON string with paper information if found, error message if not found
        """
        try:
            self.logger.info(f"Extracting info for paper: {paper_id}")
            
            # Validate paper ID
            if not paper_id or not paper_id.strip():
                error = ErrorResponse(
                    error="Paper ID cannot be empty",
                    error_type="ValidationError"
                )
                return json.dumps(error.dict(), indent=self.config.json_indent)
            
            paper_id = paper_id.strip()
            
            # Search for paper across all topics
            paper_info = self.file_handler.find_paper_across_topics(paper_id)
            
            if paper_info:
                self.logger.info(f"Found paper {paper_id}")
                return json.dumps(
                    paper_info.to_dict(), 
                    indent=self.config.json_indent,
                    ensure_ascii=False
                )
            else:
                self.logger.warning(f"Paper {paper_id} not found in any topic")
                error = ErrorResponse(
                    error=f"No saved information found for paper {paper_id}",
                    error_type="NotFoundError",
                    context={"paper_id": paper_id, "searched_topics": self.file_handler.list_all_topics()}
                )
                return json.dumps(error.dict(), indent=self.config.json_indent)
                
        except Exception as e:
            self.logger.error(f"Error extracting info for paper {paper_id}: {e}")
            error = ErrorResponse(
                error=f"Failed to extract paper information: {str(e)}",
                error_type="InternalError",
                context={"paper_id": paper_id}
            )
            return json.dumps(error.dict(), indent=self.config.json_indent)
    
    def get_paper_info(self, paper_id: str) -> Optional[PaperInfo]:
        """
        Get paper information as a PaperInfo object.
        
        Args:
            paper_id: The ID of the paper to look for
            
        Returns:
            PaperInfo object if found, None otherwise
        """
        try:
            return self.file_handler.find_paper_across_topics(paper_id.strip())
        except Exception as e:
            self.logger.error(f"Error getting paper info for {paper_id}: {e}")
            return None

    def search_papers_by_title(self, title_query: str) -> List[Dict[str, Any]]:
        """
        Search for papers by title across all topics.

        Args:
            title_query: Query string to search in titles

        Returns:
            List of matching papers with topic information
        """
        try:
            self.logger.debug(f"Searching papers by title: {title_query}")

            query_lower = title_query.lower().strip()
            matching_papers = []

            for topic in self.file_handler.list_all_topics():
                database = self.file_handler.load_papers_database(topic)

                for paper_id, paper_info in database.papers.items():
                    if query_lower in paper_info.title.lower():
                        matching_papers.append({
                            "id": paper_id,
                            "title": paper_info.title,
                            "authors": [author.name for author in paper_info.authors],
                            "published": paper_info.published.isoformat(),
                            "topic": topic,
                            "category": paper_info.category
                        })

            # Sort by relevance (exact matches first, then by publication date)
            matching_papers.sort(
                key=lambda x: (
                    query_lower not in x["title"].lower().split()[0:3],  # Boost if in first 3 words
                    -len([word for word in query_lower.split() if word in x["title"].lower()]),
                    # More matching words first
                    x["published"]  # Then by publication date
                ),
                reverse=True
            )

            return matching_papers

        except Exception as e:
            self.logger.error(f"Error searching papers by title '{title_query}': {e}")
            return []

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the entire paper database.

        Returns:
            Dictionary containing database statistics
        """
        try:
            self.logger.debug("Computing database statistics")

            topics = self.file_handler.list_all_topics()
            total_papers = 0
            topic_stats = []

            for topic in topics:
                stats = self.file_handler.get_topic_stats(topic)
                topic_stats.append(stats)
                total_papers += stats["paper_count"]

            # Sort topics by paper count
            topic_stats.sort(key=lambda x: x["paper_count"], reverse=True)

            result = {
                "total_topics": len(topics),
                "total_papers": total_papers,
                "topics": topic_stats,
                "generated_at": datetime.now().isoformat()
            }

            return result

        except Exception as e:
            self.logger.error(f"Error computing database stats: {e}")
            return {
                "error": str(e),
                "total_topics": 0,
                "total_papers": 0,
                "topics": []
            }

    def export_paper_data(self, paper_id: str, format: str = "json") -> Optional[str]:
        """
        Export paper data in specified format.

        Args:
            paper_id: The paper ID to export
            format: Export format ("json", "bibtex", "plain")

        Returns:
            Formatted paper data or None if not found
        """
        paper_info = self.get_paper_info(paper_id)
        if not paper_info:
            return None

        if format.lower() == "json":
            return json.dumps(paper_info.to_dict(), indent=2, ensure_ascii=False)

        elif format.lower() == "bibtex":
            # Generate BibTeX format
            authors = " and ".join([author.name for author in paper_info.authors])
            bibtex = f"""@article{{{paper_info.paper_id},
  title={{{paper_info.title}}},
  author={{{authors}}},
  year={{{paper_info.published.year}}},
  journal={{arXiv preprint arXiv:{paper_info.paper_id}}},
  url={{{paper_info.pdf_url}}}
}}"""
            return bibtex

        elif format.lower() == "plain":
            # Generate plain text format
            authors_str = ", ".join([author.name for author in paper_info.authors])
            plain = f"""Title: {paper_info.title}
Authors: {authors_str}
Published: {paper_info.published}
ArXiv ID: {paper_info.paper_id}
Category: {paper_info.category or 'N/A'}
PDF URL: {paper_info.pdf_url}

Abstract:
{paper_info.summary}"""
            return plain

        else:
            self.logger.warning(f"Unsupported export format: {format}")
            return None

    def list_papers_by_topic(self, topic: str) -> Dict[str, Any]:
        """
        List all papers for a specific topic.

        Args:
            topic: The topic to list papers for

        Returns:
            Dictionary containing paper list and metadata
        """
        try:
            self.logger.debug(f"Listing papers for topic: {topic}")

            database = self.file_handler.load_papers_database(topic)

            papers_list = []
            for paper_id, paper_info in database.papers.items():
                papers_list.append({
                    "id": paper_id,
                    "title": paper_info.title,
                    "authors": [author.name for author in paper_info.authors],
                    "published": paper_info.published.isoformat(),
                    "category": paper_info.category
                })

            # Sort by publication date (newest first)
            papers_list.sort(key=lambda x: x["published"], reverse=True)

            result = {
                "topic": topic,
                "paper_count": len(papers_list),
                "papers": papers_list,
                "metadata": database.metadata
            }

            return result

        except Exception as e:
            self.logger.error(f"Error listing papers for topic {topic}: {e}")
            return {
                "topic": topic,
                "error": str(e),
                "paper_count": 0,
                "papers": []
            }