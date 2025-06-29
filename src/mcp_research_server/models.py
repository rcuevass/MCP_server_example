"""Data models for MCP Research Server."""

from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, HttpUrl
from pathlib import Path
import json


class Author(BaseModel):
    """Model for paper author."""
    name: str = Field(..., description="Full name of the author")
    
    class Config:
        frozen = True


class PaperInfo(BaseModel):
    """Model for paper information."""
    
    paper_id: str = Field(..., description="ArXiv paper ID")
    title: str = Field(..., description="Paper title")
    authors: List[Author] = Field(default_factory=list, description="List of authors")
    summary: str = Field(..., description="Paper abstract/summary")
    pdf_url: HttpUrl = Field(..., description="URL to the PDF")
    published: date = Field(..., description="Publication date")
    category: Optional[str] = Field(None, description="ArXiv category")
    updated: Optional[date] = Field(None, description="Last update date")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    
    @validator('paper_id')
    def validate_paper_id(cls, v):
        """Validate paper ID format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Paper ID cannot be empty")
        return v.strip()
    
    @validator('title')
    def validate_title(cls, v):
        """Validate and clean title."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Title cannot be empty")
        return v.strip()
    
    @validator('summary')
    def validate_summary(cls, v):
        """Validate and clean summary."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Summary cannot be empty")
        return v.strip()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = self.dict()
        # Convert dates to strings
        data['published'] = self.published.isoformat()
        if self.updated:
            data['updated'] = self.updated.isoformat()
        # Convert authors to list of names for backward compatibility
        data['authors'] = [author.name for author in self.authors]
        # Convert HttpUrl to string for JSON serialization
        data['pdf_url'] = str(self.pdf_url)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaperInfo':
        """Create instance from dictionary."""
        # Handle different author formats
        if 'authors' in data:
            if isinstance(data['authors'][0], str):
                # Backward compatibility with old format
                data['authors'] = [{'name': name} for name in data['authors']]
        
        # Handle date parsing
        if isinstance(data.get('published'), str):
            data['published'] = datetime.fromisoformat(data['published']).date()
        if isinstance(data.get('updated'), str):
            data['updated'] = datetime.fromisoformat(data['updated']).date()
        
        return cls(**data)
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            HttpUrl: str
        }


class SearchRequest(BaseModel):
    """Model for paper search request."""
    
    topic: str = Field(..., min_length=1, description="Search topic")
    max_results: int = Field(
        default=5, 
        ge=1, 
        le=50, 
        description="Maximum number of results"
    )
    
    @validator('topic')
    def validate_topic(cls, v):
        """Validate and clean topic."""
        return v.strip()


class SearchResult(BaseModel):
    """Model for search results."""
    
    topic: str = Field(..., description="Search topic used")
    paper_ids: List[str] = Field(default_factory=list, description="List of found paper IDs")
    total_found: int = Field(default=0, description="Total papers found")
    saved_to: Optional[str] = Field(None, description="Path where results were saved")
    timestamp: datetime = Field(default_factory=datetime.now, description="Search timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Path: str
        }


class PaperDatabase(BaseModel):
    """Model for managing paper database files."""
    
    papers: Dict[str, PaperInfo] = Field(default_factory=dict, description="Papers by ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Database metadata")
    
    def add_paper(self, paper: PaperInfo) -> None:
        """Add a paper to the database."""
        self.papers[paper.paper_id] = paper
    
    def get_paper(self, paper_id: str) -> Optional[PaperInfo]:
        """Get a paper by ID."""
        return self.papers.get(paper_id)
    
    def has_paper(self, paper_id: str) -> bool:
        """Check if paper exists in database."""
        return paper_id in self.papers
    
    def to_json_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            paper_id: paper.to_dict() 
            for paper_id, paper in self.papers.items()
        }
    
    @classmethod
    def from_json_dict(cls, data: Dict[str, Any]) -> 'PaperDatabase':
        """Create database from JSON dictionary."""
        papers = {}
        for paper_id, paper_data in data.items():
            papers[paper_id] = PaperInfo.from_dict(paper_data)
        
        return cls(papers=papers)
    
    def save_to_file(self, file_path: Path, indent: int = 2) -> None:
        """Save database to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_json_dict(), f, indent=indent, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> 'PaperDatabase':
        """Load database from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_json_dict(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return cls()  # Return empty database


class ErrorResponse(BaseModel):
    """Model for error responses."""
    
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
