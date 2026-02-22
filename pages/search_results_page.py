"""
Page object for Nykaa search results page.

Handles: product grid, filters, sorting, result counting.

Selectors verified against live Nykaa DOM (Feb 2025):
  - Product cards: div.productWrapper wraps a[href*="/p/"]
  - Result count: span.result-count (stable, non-hashed)
  - Filter sidebar: div.filters / div.sidebar__inner (stable)
  - Filters use expandable accordion divs with checkbox labels

Note: Single-word searches (e.g., "lipstick") redirect to category
pages with different DOM. Use multi-word terms to stay on search
results (e.g., "maybelline foundation").
"""

import logging
import re
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.base_page import BasePage
from core.config import settings
from utils.waits import element_count_is_at_least

logger = logging.getLogger(__name__)


class SearchResultsPage(BasePage):
    """Nykaa search results page interactions."""

    # ── Locators (verified against live DOM) ──────────────────────────
    # Stable class 'productWrapper' is non-hashed and reliable
    PRODUCT_CARDS = (
        By.CSS_SELECTOR,
        ".productWrapper a[href*='/p/'], div.productWrapper",
    )
    PRODUCT_TITLE = (By.CSS_SELECTOR, ".productWrapper [class*='title']")
    PRODUCT_PRICE = (By.CSS_SELECTOR, ".productWrapper [class*='price']")
    FILTER_SECTION = (
        By.CSS_SELECTOR,
        "div.filters, div.sidebar__inner, [class*='filter']",
    )
    SORT_DROPDOWN = (By.CSS_SELECTOR, "[class*='sort']")
    # Stable class — shows "Showing X of Y results"
    RESULTS_COUNT = (By.CSS_SELECTOR, "span.result-count, [class*='result-count']")
    NO_RESULTS = (
        By.CSS_SELECTOR,
        "[class*='no-result'], [class*='empty'], [class*='noResult']",
    )

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def get_product_cards(self) -> List[WebElement]:
        """Get all product card elements on the page."""
        try:
            # Wait for at least 1 product card to appear
            WebDriverWait(self.driver, settings.EXPLICIT_WAIT).until(
                element_count_is_at_least(self.PRODUCT_CARDS, 1)
            )
            return self.driver.find_elements(*self.PRODUCT_CARDS)
        except Exception:
            return []

    def get_product_count(self) -> int:
        """Get number of product cards displayed."""
        return len(self.get_product_cards())

    def get_result_count_text(self) -> str:
        """Get the results count text (e.g., 'Showing 1 - 20 of 1234')."""
        try:
            return self.get_text(self.RESULTS_COUNT)
        except Exception:
            return ""

    def get_result_count(self) -> int:
        """Parse total result count from text like 'Showing 1 - 20 of 1234'."""
        text = self.get_result_count_text()
        # Extract last number — "Showing 1 - 20 of 1234" → 1234
        numbers = re.findall(r"\d+", text.replace(",", ""))
        return int(numbers[-1]) if numbers else 0

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
            logger.warning(
                "Product index %d out of range (%d cards)", index, len(cards)
            )

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
        """
        Apply a filter by category and value.

        Nykaa's filter sidebar uses expandable accordion sections.
        Filter categories are text-labeled divs; values are checkbox
        labels within each expanded section.
        """
        logger.info("Applying filter: %s > %s", filter_category, filter_value)
        # Click the filter category heading to expand it
        category_locator = (
            By.XPATH,
            f"//div[contains(@class, 'filter')]"
            f"//div[contains(text(), '{filter_category}')] | "
            f"//div[contains(@class, 'filter')]"
            f"//span[contains(text(), '{filter_category}')]",
        )
        self.click(category_locator)

        # Click the specific filter value (checkbox label)
        value_locator = (
            By.XPATH,
            f"//label[contains(text(), '{filter_value}')] | "
            f"//span[contains(text(), '{filter_value}')]",
        )
        self.click(value_locator)

        # Wait for products to reload after filter
        WebDriverWait(self.driver, settings.EXPLICIT_WAIT).until(
            element_count_is_at_least(self.PRODUCT_CARDS, 1)
        )

    def is_filter_section_visible(self) -> bool:
        """Check if filter sidebar is present."""
        return self.is_element_visible(self.FILTER_SECTION, timeout=5)
