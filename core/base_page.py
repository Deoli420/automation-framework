"""
Base page object — foundation for all page objects.

Provides:
  - Explicit waits with configurable timeout
  - Safe click / type / scroll operations
  - Popup dismissal for Nykaa login/cookie modals
  - Automatic screenshot capture
  - Structured logging for every interaction

All page objects inherit from this class.
"""

import logging
import os
import re
from datetime import datetime
from typing import List, Optional

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.config import settings
from core.exceptions import ElementNotFoundError, PageLoadError
from utils.retry import retry

logger = logging.getLogger(__name__)


class BasePage:
    """Base class for all page objects in the framework."""

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(
            driver,
            settings.EXPLICIT_WAIT,
            ignored_exceptions=[StaleElementReferenceException],
        )

    # ── Navigation ────────────────────────────────────────────────────

    def open(self, path: str = "") -> None:
        """Navigate to BASE_URL + path."""
        url = f"{settings.BASE_URL}{path}"
        logger.info("Navigating to %s", url)
        try:
            self.driver.get(url)
        except TimeoutException:
            raise PageLoadError(f"Page load timed out: {url}")

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_title(self) -> str:
        return self.driver.title

    # ── Popup dismissal ───────────────────────────────────────────────

    def dismiss_popups(self, timeout: int = 3) -> None:
        """
        Dismiss login/signup and cookie popups on Nykaa.

        Nykaa shows a login modal on first visit. This method
        tries multiple strategies to close it without failing if
        no popup is present.
        """
        # Strategy 1: Press Escape to close any modal
        try:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            logger.debug("Sent Escape key to dismiss popup")
        except Exception:
            pass

        # Strategy 2: Click modal overlay backdrop
        overlay_selectors = [
            "div.modal-backdrop",
            "div[class*='overlay']",
            "div[class*='Overlay']",
        ]
        for selector in overlay_selectors:
            try:
                overlay = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, selector)
                    )
                )
                overlay.click()
                logger.debug("Clicked overlay: %s", selector)
                return
            except (TimeoutException, NoSuchElementException):
                continue

        # Strategy 3: Click any close / dismiss button
        close_selectors = [
            "button[class*='close']",
            "span[class*='close']",
            "[class*='dismiss']",
            "[aria-label='Close']",
        ]
        for selector in close_selectors:
            try:
                btn = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, selector)
                    )
                )
                btn.click()
                logger.debug("Clicked close button: %s", selector)
                return
            except (TimeoutException, NoSuchElementException):
                continue

        logger.debug("No popup detected — nothing to dismiss")

    # ── Element interactions ──────────────────────────────────────────

    @retry(max_attempts=3, delay=0.5, exceptions=(StaleElementReferenceException,))
    def find_element(
        self, locator: tuple[str, str], timeout: Optional[int] = None
    ) -> WebElement:
        """Find a single element with explicit wait + stale-element retry."""
        try:
            wait = WebDriverWait(
                self.driver, timeout or settings.EXPLICIT_WAIT
            )
            return wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            raise ElementNotFoundError(
                f"Element not found within {timeout or settings.EXPLICIT_WAIT}s: {locator}"
            )

    def find_elements(self, locator: tuple[str, str]) -> List[WebElement]:
        """Find multiple elements with explicit wait."""
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    @retry(max_attempts=3, delay=0.5, exceptions=(StaleElementReferenceException,))
    def click(self, locator: tuple[str, str]) -> None:
        """Wait for element to be clickable, then click (with stale-element retry)."""
        logger.info("Clicking: %s", locator)
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def type_text(self, locator: tuple[str, str], text: str) -> None:
        """Clear field and type text."""
        logger.info("Typing into %s: '%s'", locator, text)
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple[str, str]) -> str:
        """Get visible text of an element."""
        return self.find_element(locator).text

    def get_attribute(self, locator: tuple[str, str], attribute: str) -> str:
        """Get an attribute value from an element."""
        return self.find_element(locator).get_attribute(attribute) or ""

    def is_element_visible(
        self, locator: tuple[str, str], timeout: int = 5
    ) -> bool:
        """Check if element is visible within timeout (no exception)."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    # ── Scrolling ─────────────────────────────────────────────────────

    def scroll_to_element(self, locator: tuple[str, str]) -> None:
        """Scroll element into viewport center."""
        element = self.find_element(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
            element,
        )

    def scroll_to_bottom(self) -> None:
        """Scroll to page bottom."""
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

    # ── Screenshots ───────────────────────────────────────────────────

    def take_screenshot(self, name: str) -> str:
        """Capture screenshot and return file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize name for filesystem
        safe_name = re.sub(r"[^\w\-]", "_", name)
        filepath = os.path.join(
            settings.REPORT_DIR, "screenshots", f"{safe_name}_{timestamp}.png"
        )
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.driver.save_screenshot(filepath)
        logger.info("Screenshot saved: %s", filepath)
        return filepath

    # ── Waits ─────────────────────────────────────────────────────────

    def wait_for_url_contains(
        self, partial_url: str, timeout: Optional[int] = None
    ) -> None:
        """Wait until current URL contains the given substring."""
        WebDriverWait(self.driver, timeout or settings.EXPLICIT_WAIT).until(
            EC.url_contains(partial_url)
        )

    def wait_for_text_in_element(
        self, locator: tuple[str, str], text: str, timeout: Optional[int] = None
    ) -> None:
        """Wait until element contains specific text."""
        WebDriverWait(self.driver, timeout or settings.EXPLICIT_WAIT).until(
            EC.text_to_be_present_in_element(locator, text)
        )

    # ── Utility ───────────────────────────────────────────────────────

    def parse_price(self, text: str) -> float:
        """Extract numeric price from text like 'Rs. 1,299' or '₹1299'."""
        cleaned = re.sub(r"[^\d.]", "", text)
        return float(cleaned) if cleaned else 0.0

    def get_browser_console_logs(self) -> list:
        """Capture browser console logs (Chrome only)."""
        try:
            return self.driver.get_log("browser")
        except Exception:
            return []
