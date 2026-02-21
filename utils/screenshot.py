"""
Screenshot capture utility.

Used by the conftest.py autouse fixture to capture screenshots on test failure.
Can also be called directly from test code.
"""

import logging
import os
import re
from datetime import datetime

from selenium.webdriver.remote.webdriver import WebDriver

from core.config import settings

logger = logging.getLogger(__name__)


def capture_screenshot(driver: WebDriver, name: str) -> str:
    """
    Save a screenshot and return the file path.

    Args:
        driver: Active WebDriver instance
        name: Descriptive name (sanitized for filesystem)

    Returns:
        Absolute path to the saved screenshot
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r"[^\w\-]", "_", name)
    filepath = os.path.join(
        settings.REPORT_DIR, "screenshots", f"{safe_name}_{timestamp}.png"
    )
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    try:
        driver.save_screenshot(filepath)
        logger.info("Screenshot captured: %s", filepath)
    except Exception as exc:
        logger.warning("Failed to capture screenshot: %s", exc)
        return ""

    return filepath
