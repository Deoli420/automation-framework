"""
Page object for Nykaa homepage.

Handles: search bar interaction, popup dismissal, navigation.

Selectors verified against live Nykaa DOM (Feb 2025):
  - Search input: input[name="search-suggestions-nykaa"]
  - Logo: header img
  - Suggestions: dropdown below search input
"""

import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.base_page import BasePage
from core.config import settings
from utils.waits import page_has_loaded

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    """Nykaa homepage interactions."""

    # ── Locators (verified against live DOM) ──────────────────────────
    SEARCH_INPUT = (By.CSS_SELECTOR, 'input[name="search-suggestions-nykaa"]')
    SEARCH_SUGGESTIONS = (
        By.CSS_SELECTOR,
        "[class*='suggestion'], [class*='autocomplete'], "
        "[class*='searchSuggestion']",
    )
    LOGO = (By.CSS_SELECTOR, "a[title='logo'], header svg, a[href*='logo'], header a[href='/'], header img, a[href='/'] img")
    NAV_CATEGORIES = (By.CSS_SELECTOR, "nav a, header nav a")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def navigate(self) -> "HomePage":
        """Open the Nykaa homepage and dismiss any popups."""
        self.open("/")
        # Wait for page to fully load before interacting
        WebDriverWait(self.driver, settings.EXPLICIT_WAIT).until(
            page_has_loaded()
        )
        self.dismiss_popups()
        logger.info("HomePage loaded")
        return self

    def search_product(self, query: str) -> None:
        """Type search query and press Enter."""
        logger.info("Searching for: '%s'", query)
        search_el = self.find_element(self.SEARCH_INPUT)
        search_el.clear()
        search_el.send_keys(query)
        search_el.send_keys(Keys.RETURN)
        # Wait for navigation away from homepage
        if query.strip():
            try:
                WebDriverWait(self.driver, settings.EXPLICIT_WAIT).until(
                    EC.url_changes(self.driver.current_url)
                )
            except Exception:
                logger.debug("URL did not change after search — may be empty query")

    def is_loaded(self) -> bool:
        """Check if homepage loaded by verifying search input presence."""
        return self.is_element_visible(self.SEARCH_INPUT)

    def get_search_suggestions(self, query: str) -> bool:
        """Type partial query and check if suggestions appear."""
        self.type_text(self.SEARCH_INPUT, query)
        return self.is_element_visible(self.SEARCH_SUGGESTIONS, timeout=5)

    def has_navigation_categories(self) -> bool:
        """Check if top-level navigation categories are present."""
        return self.is_element_visible(self.NAV_CATEGORIES, timeout=5)
