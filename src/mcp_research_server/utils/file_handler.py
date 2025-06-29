"""File handling utilities for MCP Research Server."""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..config import get_config
from ..models import PaperDatabase, PaperInfo
from .logger import get_logger, LoggerMixin, log_execution_time


class FileHandler(LoggerMixin):
    """Handles file operations for the MCP Research Server."""
    
    def __init__(self, config: Optional[object] = None):
        self.config = config or get_config()
        self.papers_dir = self.config.papers_dir
        
    def get_topic_directory(self, topic: str) -> Path:
        """Get the directory path for a specific topic."""
        sanitized_topic = self._sanitize_filename(topic)
        return self.papers_dir / sanitized_topic
    
    def get_papers_info_file(self, topic: str) -> Path:
        """Get the path to the papers info JSON file for a topic."""
        return self.get_topic_directory(topic) / "papers_info.json"
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize a string to be used as a filename."""
        # Replace spaces with underscores and remove invalid characters
        sanitized = filename.lower().replace(" ", "_")
        # Remove characters that are invalid in filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            sanitized = sanitized.replace(char, "")
        # Remove multiple consecutive underscores
        while "__" in sanitized:
            sanitized = sanitized.replace("__", "_")
        # Remove leading/trailing underscores
        return sanitized.strip("_")
    
    @log_execution_time
    def create_topic_directory(self, topic: str) -> Path:
        """Create directory for a topic if it doesn't exist."""
        topic_dir = self.get_topic_directory(topic)
        topic_dir.mkdir(parents=True, exist_ok=True)
        self.logger.debug(f"Created/verified topic directory: {topic_dir}")
        return topic_dir
    
    @log_execution_time
    def load_papers_database(self, topic: str) -> PaperDatabase:
        """Load papers database for a specific topic."""
        papers_file = self.get_papers_info_file(topic)
        
        try:
            database = PaperDatabase.load_from_file(papers_file)
            self.logger.debug(f"Loaded {len(database.papers)} papers from {papers_file}")
            return database
        except Exception as e:
            self.logger.warning(f"Failed to load papers database from {papers_file}: {e}")
            return PaperDatabase()
    
    @log_execution_time
    def save_papers_database(self, topic: str, database: PaperDatabase) -> Path:
        """Save papers database for a specific topic."""
        # Ensure topic directory exists
        topic_dir = self.create_topic_directory(topic)
        papers_file = self.get_papers_info_file(topic)
        
        try:
            # Add metadata
            database.metadata.update({
                "last_updated": datetime.now().isoformat(),
                "topic": topic,
                "paper_count": len(database.papers)
            })
            
            database.save_to_file(papers_file, indent=self.config.json_indent)
            self.logger.info(f"Saved {len(database.papers)} papers to {papers_file}")
            return papers_file
        except Exception as e:
            self.logger.error(f"Failed to save papers database to {papers_file}: {e}")
            raise
    
    def find_paper_across_topics(self, paper_id: str) -> Optional[PaperInfo]:
        """Search for a paper across all topic directories."""
        self.logger.debug(f"Searching for paper {paper_id} across all topics")
        
        if not self.papers_dir.exists():
            self.logger.warning(f"Papers directory {self.papers_dir} does not exist")
            return None
        
        for topic_dir in self.papers_dir.iterdir():
            if not topic_dir.is_dir():
                continue
                
            papers_file = topic_dir / "papers_info.json"
            if not papers_file.exists():
                continue
            
            try:
                database = PaperDatabase.load_from_file(papers_file)
                paper = database.get_paper(paper_id)
                if paper:
                    self.logger.debug(f"Found paper {paper_id} in topic {topic_dir.name}")
                    return paper
            except Exception as e:
                self.logger.warning(f"Error reading {papers_file}: {e}")
                continue
        
        self.logger.debug(f"Paper {paper_id} not found in any topic")
        return None
    
    def list_all_topics(self) -> List[str]:
        """List all available topics (directories)."""
        if not self.papers_dir.exists():
            return []
        
        topics = []
        for item in self.papers_dir.iterdir():
            if item.is_dir() and (item / "papers_info.json").exists():
                # Convert back from sanitized format
                topic = item.name.replace("_", " ").title()
                topics.append(topic)
        
        return sorted(topics)
    
    def get_topic_stats(self, topic: str) -> Dict[str, Any]:
        """Get statistics for a specific topic."""
        database = self.load_papers_database(topic)
        
        if not database.papers:
            return {"paper_count": 0, "topic": topic}
        
        papers = list(database.papers.values())
        
        # Calculate stats
        stats = {
            "topic": topic,
            "paper_count": len(papers),
            "latest_paper": max(papers, key=lambda p: p.published).published.isoformat(),
            "oldest_paper": min(papers, key=lambda p: p.published).published.isoformat(),
            "last_updated": database.metadata.get("last_updated", "Unknown")
        }
        
        return stats
    
    def cleanup_empty_directories(self) -> int:
        """Remove empty topic directories and return count of removed directories."""
        if not self.papers_dir.exists():
            return 0
        
        removed_count = 0
        for topic_dir in self.papers_dir.iterdir():
            if topic_dir.is_dir():
                try:
                    # Check if directory is empty or only contains empty papers_info.json
                    files = list(topic_dir.glob("*"))
                    if not files:
                        topic_dir.rmdir()
                        removed_count += 1
                        self.logger.info(f"Removed empty directory: {topic_dir}")
                    elif len(files) == 1 and files[0].name == "papers_info.json":
                        # Check if papers_info.json is empty or contains no papers
                        try:
                            database = PaperDatabase.load_from_file(files[0])
                            if not database.papers:
                                shutil.rmtree(topic_dir)
                                removed_count += 1
                                self.logger.info(f"Removed directory with empty database: {topic_dir}")
                        except Exception:
                            pass
                except Exception as e:
                    self.logger.warning(f"Error cleaning up directory {topic_dir}: {e}")
        
        return removed_count
