"""
Page object for Nykaa search results page.

Handles: product grid, filters, sorting, result counting.
"""

import logging
import re
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from core.base_page import BasePage

logger = logging.getLogger(__name__)


class SearchResultsPage(BasePage):
    """Nykaa search results page interactions."""

    # ── Locators ──────────────────────────────────────────────────────
    PRODUCT_CARDS = (By.CSS_SELECTOR, "[class*='product-listing'] a, [class*='productWrapper']")
    PRODUCT_TITLE = (By.CSS_SELECTOR, "[class*='product-name'], [class*='title']")
    PRODUCT_PRICE = (By.CSS_SELECTOR, "[class*='price']")
    FILTER_SECTION = (By.CSS_SELECTOR, "[class*='filter'], [class*='sidebar']")
    SORT_DROPDOWN = (By.CSS_SELECTOR, "[class*='sort']")
    RESULTS_COUNT = (By.CSS_SELECTOR, "[class*='result-count'], [class*='total']")
    NO_RESULTS = (By.CSS_SELECTOR, "[class*='no-result'], [class*='empty']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def get_product_cards(self) -> List[WebElement]:
        """Get all product card elements on the page."""
        try:
            return self.find_elements(self.PRODUCT_CARDS)
        except Exception:
            return []

    def get_product_count(self) -> int:
        """Get number of product cards displayed."""
        return len(self.get_product_cards())

    def get_result_count_text(self) -> str:
        """Get the results count text (e.g., '1234 products')."""
        try:
            return self.get_text(self.RESULTS_COUNT)
        except Exception:
            return ""

    def get_result_count(self) -> int:
        """Parse numeric result count from text."""
        text = self.get_result_count_text()
        match = re.search(r"\d+", text.replace(",", ""))
        return int(match.group()) if match else 0

    def click_first_product(self) -> None:
        """Click the first product card in results."""
        cards = self.get_product_cards()
        if cards:
            logger.info("Clicking first product card")
            cards[0].click()
        else:
            logger.warning("No product cards found to click")

    def click_product_at_index(self, index: int) -> None:
        """Click a product card at the given index."""
        cards = self.get_product_cards()
        if index < len(cards):
            logger.info("Clicking product at index %d", index)
            cards[index].click()
        else:
            logger.warning("Product index %d out of range (%d cards)", index, len(cards))

    def get_first_product_price_text(self) -> str:
        """Get price text of the first product."""
        prices = self.driver.find_elements(*self.PRODUCT_PRICE)
        return prices[0].text if prices else ""

    def get_first_product_price(self) -> float:
        """Get numeric price of the first product."""
        return self.parse_price(self.get_first_product_price_text())

    def has_results(self) -> bool:
        """Check if search returned results."""
        return self.get_product_count() > 0

    def has_no_results(self) -> bool:
        """Check if 'no results' message is displayed."""
        return self.is_element_visible(self.NO_RESULTS, timeout=5)

    def apply_filter(self, filter_category: str, filter_value: str) -> None:
        """Apply a filter by category and value."""
        logger.info("Applying filter: %s > %s", filter_category, filter_value)
        category_locator = (
            By.XPATH,
            f"//div[contains(text(), '{filter_category}')] | "
            f"//span[contains(text(), '{filter_category}')]",
        )
        self.click(category_locator)

        value_locator = (
            By.XPATH,
            f"//label[contains(text(), '{filter_value}')] | "
            f"//span[contains(text(), '{filter_value}')]",
        )
        self.click(value_locator)

    def is_filter_section_visible(self) -> bool:
        """Check if filter sidebar is present."""
        return self.is_element_visible(self.FILTER_SECTION, timeout=5)
