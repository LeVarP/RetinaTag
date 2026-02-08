"""
Configuration management for OCT B-Scan Labeler backend.
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/database/oct_labeler.db"

    # Data directories
    data_dir: Path = Path("./data")
    cache_dir: Path = Path("./data/cache")
    scans_dir: Path = Path("./data/scans")

    # Preview generation
    preview_format: str = "webp"  # Options: webp, png, jpeg
    preview_quality: int = 85  # Quality for lossy formats (0-100)
    normalization_method: str = "percentile"  # Options: percentile, fixed_window
    percentile_low: float = 1.0  # Lower percentile for normalization
    percentile_high: float = 99.0  # Upper percentile for normalization

    # Prefetch configuration
    prefetch_count: int = 10  # Number of frames to prefetch

    # CORS settings
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost",
    ]

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.scans_dir.mkdir(parents=True, exist_ok=True)
        (self.cache_dir / "previews").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "database").mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

# Ensure directories exist on import
settings.ensure_directories()
