"""
Page object for Nykaa homepage.

Handles: search bar interaction, navigation.
"""

import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from core.base_page import BasePage

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    """Nykaa homepage interactions."""

    # ── Locators ──────────────────────────────────────────────────────
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[type='text']")
    SEARCH_SUGGESTIONS = (By.CSS_SELECTOR, "[class*='suggestion'], [class*='autocomplete']")
    LOGO = (By.CSS_SELECTOR, "a[href='/'] img, [class*='logo']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def navigate(self) -> "HomePage":
        """Open the Nykaa homepage."""
        self.open("/")
        logger.info("HomePage loaded")
        return self

    def search_product(self, query: str) -> None:
        """Type search query and press Enter."""
        logger.info("Searching for: '%s'", query)
        self.type_text(self.SEARCH_INPUT, query)
        self.find_element(self.SEARCH_INPUT).send_keys(Keys.RETURN)

    def is_loaded(self) -> bool:
        """Check if homepage loaded by verifying search input presence."""
        return self.is_element_visible(self.SEARCH_INPUT)

    def get_search_suggestions(self, query: str) -> bool:
        """Type partial query and check if suggestions appear."""
        self.type_text(self.SEARCH_INPUT, query)
        return self.is_element_visible(self.SEARCH_SUGGESTIONS, timeout=5)
