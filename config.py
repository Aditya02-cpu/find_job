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
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini/gemini-3.8-flash")
    # Fallbacks used when the primary model is overloaded (503) or unavailable (404).
    # Multiple models are tried in order; each gets a few attempts with backoff.
    GEMINI_FALLBACK_MODEL: str = os.getenv("GEMINI_FALLBACK_MODEL", "gemini/gemini-3.5-flash-lite")
    GEMINI_FALLBACK_MODELS: list[str] = [
        model.strip()
        for model in os.getenv("GEMINI_FALLBACK_MODELS", "").split(",")
        if model.strip()
    ] or [GEMINI_FALLBACK_MODEL, "gemini/gemini-flash-lite-latest"]
    GEMINI_FALLBACK_RETRIES: int = int(os.getenv("GEMINI_FALLBACK_RETRIES", "2"))
    GEMINI_RETRY_DELAY_SECONDS: float = float(os.getenv("GEMINI_RETRY_DELAY_SECONDS", "2"))

    # Performance / agent behavior tuning
    # Disable Gemini "thinking" by default for faster responses (Gemini 2.5+ auto-enables it).
    GEMINI_THINKING_BUDGET: int = int(os.getenv("GEMINI_THINKING_BUDGET", "0"))
    GEMINI_INCLUDE_THOUGHTS: bool = os.getenv("GEMINI_INCLUDE_THOUGHTS", "false").lower() == "true"
    # Agent memory adds significant overhead (storage + recall/encoding LLM calls). Off by default.
    AGENT_MEMORY_ENABLED: bool = os.getenv("AGENT_MEMORY_ENABLED", "false").lower() == "true"
    AGENT_MAX_ITER: int = int(os.getenv("AGENT_MAX_ITER", "12"))
    CREW_VERBOSE: bool = os.getenv("CREW_VERBOSE", "true").lower() == "true"
    # Prompt/input size caps to reduce token latency
    MAX_JOB_TEXT_CHARS: int = int(os.getenv("MAX_JOB_TEXT_CHARS", "6000"))
    MAX_RESUME_CHARS: int = int(os.getenv("MAX_RESUME_CHARS", "12000"))

    # USAJobs API
    USAJOBS_API_KEY: str = os.getenv("USAJOBS_API_KEY", "")
    USAJOBS_EMAIL: str = os.getenv("USAJOBS_EMAIL", "")
    USAJOBS_BASE_URL: str = "https://data.usajobs.gov/api/search"

    # Indian Job APIs
    INDIAN_JOB_PROVIDER: str = os.getenv("INDIAN_JOB_PROVIDER", "adzuna").lower()

    # Adzuna
    ADZUNA_APP_ID: str = os.getenv("ADZUNA_APP_ID", "")
    ADZUNA_APP_KEY: str = os.getenv("ADZUNA_APP_KEY", "")
    ADZUNA_BASE_URL: str = "https://api.adzuna.com/v1/api/jobs"

    # JSearch (RapidAPI)
    RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")
    RAPIDAPI_JSEARCH_HOST: str = os.getenv("RAPIDAPI_JSEARCH_HOST", "jsearch.p.rapidapi.com")

    # Jooble
    JOOBLE_API_KEY: str = os.getenv("JOOBLE_API_KEY", "")

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
    def validate_indian(cls) -> list[str]:
        """Validate Indian job API keys based on selected provider."""
        missing = []
        provider = cls.INDIAN_JOB_PROVIDER
        if provider == "adzuna":
            if not cls.ADZUNA_APP_ID or cls.ADZUNA_APP_ID == "your_adzuna_app_id_here":
                missing.append("ADZUNA_APP_ID")
            if not cls.ADZUNA_APP_KEY or cls.ADZUNA_APP_KEY == "your_adzuna_app_key_here":
                missing.append("ADZUNA_APP_KEY")
        elif provider == "jsearch":
            if not cls.RAPIDAPI_KEY or cls.RAPIDAPI_KEY == "your_rapidapi_key_here":
                missing.append("RAPIDAPI_KEY")
        elif provider == "jooble":
            if not cls.JOOBLE_API_KEY or cls.JOOBLE_API_KEY == "your_jooble_api_key_here":
                missing.append("JOOBLE_API_KEY")
        return missing

    @classmethod
    def ensure_dirs(cls):
        """Create log and output directories if they don't exist."""
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
