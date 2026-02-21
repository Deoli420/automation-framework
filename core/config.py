"""
Configuration management using pydantic-settings.

All environment variables are prefixed with AUTO_ to avoid collision
with host environment. Supports local/ci/staging configs via env files.

Usage:
    from core.config import settings
    settings.BASE_URL  # "https://www.nykaa.com"
"""

from pydantic_settings import BaseSettings


class AutomationSettings(BaseSettings):
    """Central configuration for the automation framework."""

    # ── Target ────────────────────────────────────────────────────────
    BASE_URL: str = "https://www.nykaa.com"
    API_BASE_URL: str = "https://www.nykaa.com"

    # ── Browser ───────────────────────────────────────────────────────
    BROWSER: str = "chrome"
    HEADLESS: bool = True
    WINDOW_WIDTH: int = 1920
    WINDOW_HEIGHT: int = 1080
    IMPLICIT_WAIT: int = 10
    EXPLICIT_WAIT: int = 15
    PAGE_LOAD_TIMEOUT: int = 30

    # ── Selenium Grid (empty = local driver) ──────────────────────────
    SELENIUM_REMOTE_URL: str = ""

    # ── API Validation ────────────────────────────────────────────────
    API_TIMEOUT: int = 15
    API_MAX_RETRIES: int = 2
    API_RETRY_BACKOFF: float = 1.0

    # ── Test Execution ────────────────────────────────────────────────
    RERUNS: int = 2
    RERUNS_DELAY: int = 3
    PARALLEL_WORKERS: int = 2

    # ── Reporting ─────────────────────────────────────────────────────
    REPORT_DIR: str = "reports"
    SCREENSHOT_ON_FAILURE: bool = True

    # ── Logging ───────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # ── Environment Tag ───────────────────────────────────────────────
    ENVIRONMENT: str = "local"

    model_config = {
        "env_file": ".env",
        "env_prefix": "AUTO_",
        "extra": "ignore",
    }


settings = AutomationSettings()
