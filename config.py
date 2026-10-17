"""
Configuration management for the Multi-Agent Job Application Assistant.
Loads environment variables and provides centralized config access.
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Centralized configuration for API keys and settings."""

    # Google Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini/gemini-3.8-flash"

    # USAJobs API
    USAJOBS_API_KEY: str = os.getenv("USAJOBS_API_KEY", "")
    USAJOBS_EMAIL: str = os.getenv("USAJOBS_EMAIL", "")
    USAJOBS_BASE_URL: str = "https://data.usajobs.gov/api/search"

    # Application settings
    LOG_DIR: str = os.path.join(os.path.dirname(__file__), "logs")
    OUTPUT_DIR: str = os.path.join(os.path.dirname(__file__), "output")

    @classmethod
    def validate(cls) -> list[str]:
        """Validate that required config values are set. Returns list of missing keys."""
        missing = []
        if not cls.GEMINI_API_KEY or cls.GEMINI_API_KEY == "your_gemini_api_key_here":
            missing.append("GEMINI_API_KEY")
        if not cls.USAJOBS_API_KEY or cls.USAJOBS_API_KEY == "your_usajobs_api_key_here":
            missing.append("USAJOBS_API_KEY")
        if not cls.USAJOBS_EMAIL or cls.USAJOBS_EMAIL == "your_email@example.com":
            missing.append("USAJOBS_EMAIL")
        return missing

    @classmethod
    def ensure_dirs(cls):
        """Create log and output directories if they don't exist."""
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
