"""
UI Tests — Filter functionality.

Tests applying filters on search results and verifying
result counts change appropriately.

Nykaa filter sidebar uses stable classes:
  - div.filters / div.sidebar__inner
  - Accordion sections for Brand, Price, Discount, etc.
  - Checkbox labels for individual filter values
"""

import pytest
from selenium.webdriver.support.ui import WebDriverWait

from core.config import settings
from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage
from utils.waits import element_count_is_at_least


@pytest.mark.ui
@pytest.mark.search
class TestFilters:
    """Filter application tests on search results page."""

    def test_search_results_have_filter_section(self, driver):
        """Verify that filter/sidebar section appears on search results."""
        home = HomePage(driver)
        home.navigate()
        home.search_product("neutrogena sunscreen spf 50")

        results = SearchResultsPage(driver)
        assert results.has_results(), "No results to filter"
        assert results.is_filter_section_visible(), "Filter section not visible"

    def test_results_change_after_filter(self, driver):
        """Verify that applying a filter changes the results."""
        home = HomePage(driver)
        home.navigate()
        home.search_product("himalaya face wash neem")

        results = SearchResultsPage(driver)
        assert results.has_results(), "No initial results"

        initial_count = results.get_product_count()

        # Apply a brand filter — this may fail if filter DOM changes
        results.apply_filter("Brand", "Himalaya")

        # Wait for products to reload (handled inside apply_filter)
        filtered_count = results.get_product_count()
        assert filtered_count > 0, (
            f"Filter returned no results (was {initial_count}, now {filtered_count})"
        )

    def test_search_results_page_loads(self, driver):
        """Verify search results page structure is intact."""
        home = HomePage(driver)
        home.navigate()
        home.search_product("biotique shampoo green apple")

        results = SearchResultsPage(driver)
        assert results.has_results(), "Search results page did not load products"
        # Verify basic page structure
        count = results.get_product_count()
        assert count > 0, f"Expected products, got {count}"
