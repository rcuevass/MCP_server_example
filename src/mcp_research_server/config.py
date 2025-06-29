"""Configuration management for MCP Research Server."""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


@dataclass
class ServerConfig:
    """Configuration settings for the MCP Research Server."""
    
    # Server settings
    server_name: str = field(default_factory=lambda: os.getenv("MCP_SERVER_NAME", "research"))
    transport: str = field(default_factory=lambda: os.getenv("MCP_TRANSPORT", "stdio"))
    
    # Data directories
    base_dir: Path = field(default_factory=lambda: Path(os.getenv("MCP_BASE_DIR", ".")))
    papers_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    
    # ArXiv settings
    arxiv_max_results_default: int = field(
        default_factory=lambda: int(os.getenv("MCP_ARXIV_MAX_RESULTS", "5"))
    )
    arxiv_max_results_limit: int = field(
        default_factory=lambda: int(os.getenv("MCP_ARXIV_MAX_RESULTS_LIMIT", "50"))
    )
    
    # Logging settings
    log_level: str = field(default_factory=lambda: os.getenv("MCP_LOG_LEVEL", "INFO"))
    log_format: str = field(
        default_factory=lambda: os.getenv(
            "MCP_LOG_FORMAT", 
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )
    log_max_bytes: int = field(
        default_factory=lambda: int(os.getenv("MCP_LOG_MAX_BYTES", "10485760"))  # 10MB
    )
    log_backup_count: int = field(
        default_factory=lambda: int(os.getenv("MCP_LOG_BACKUP_COUNT", "5"))
    )
    
    # File handling settings
    json_indent: int = field(default_factory=lambda: int(os.getenv("MCP_JSON_INDENT", "2")))
    create_dirs: bool = field(
        default_factory=lambda: os.getenv("MCP_CREATE_DIRS", "true").lower() == "true"
    )
    
    def __post_init__(self):
        """Initialize computed fields and create directories if needed."""
        self.papers_dir = self.base_dir / "data" / "papers"
        self.logs_dir = self.base_dir / "logs"
        
        if self.create_dirs:
            self.papers_dir.mkdir(parents=True, exist_ok=True)
            self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> None:
        """Validate configuration settings."""
        if self.arxiv_max_results_default > self.arxiv_max_results_limit:
            raise ValueError(
                f"Default max results ({self.arxiv_max_results_default}) "
                f"cannot exceed limit ({self.arxiv_max_results_limit})"
            )
        
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {self.log_level}")
        
        if self.transport not in ["stdio", "http", "sse"]:
            raise ValueError(f"Invalid transport: {self.transport}")


# Global config instance
_config: Optional[ServerConfig] = None


def get_config() -> ServerConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = ServerConfig()
        _config.validate()
    return _config


def reload_config() -> ServerConfig:
    """Reload configuration from environment."""
    global _config
    _config = None
    return get_config()


def set_config(config: ServerConfig) -> None:
    """Set a custom configuration instance."""
    global _config
    config.validate()
    _config = config
