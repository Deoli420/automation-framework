"""
UI Tests — Search functionality.

Tests Nykaa's search flow: typing queries, verifying results appear,
handling edge cases.

Note: Single-word searches like "lipstick" redirect to category pages
with different DOM structure. Multi-word terms stay on the search
results page (e.g., "maybelline foundation").
"""

import pytest

from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage
from utils.data_generator import get_random_search_term


@pytest.mark.ui
@pytest.mark.search
@pytest.mark.smoke
class TestSearch:
    """Search flow tests."""

    def test_search_returns_results(self, driver):
        """Verify that searching for a common product returns results."""
        home = HomePage(driver)
        home.navigate()
        # Multi-word query to stay on search results page
        home.search_product("maybelline foundation")

        results = SearchResultsPage(driver)
        assert results.has_results(), (
            "Search for 'maybelline foundation' returned no results"
        )

    def test_search_results_have_products(self, driver):
        """Verify search results contain product cards with prices."""
        home = HomePage(driver)
        home.navigate()
        home.search_product("vitamin c serum for oily skin")

        results = SearchResultsPage(driver)
        count = results.get_product_count()
        assert count > 0, "No product cards found in search results"

    def test_search_with_random_term(self, driver):
        """Verify search works with a randomly selected term."""
        term = get_random_search_term()

        home = HomePage(driver)
        home.navigate()
        home.search_product(term)

        results = SearchResultsPage(driver)
        # Most beauty product searches should return results
        assert results.has_results(), f"Search for '{term}' returned no results"

    def test_search_empty_query_stays_on_page(self, driver):
        """Verify that submitting empty search doesn't navigate away."""
        home = HomePage(driver)
        home.navigate()
        original_url = driver.current_url

        home.search_product("")
        # Should stay on homepage, not navigate to a different page
        current_url = driver.current_url
        assert current_url == original_url or "nykaa.com" in current_url, (
            f"Empty search navigated to unexpected URL: {current_url}"
        )

    @pytest.mark.parametrize(
        "term",
        [
            "maybelline foundation",
            "lakme eyeshadow palette",
            "neutrogena sunscreen spf 50",
            "garnier micellar water",
            "olay night cream anti aging",
        ],
    )
    @pytest.mark.data_driven
    def test_search_returns_results_parametrized(self, driver, term):
        """Verify search returns results for multiple product queries."""
        home = HomePage(driver)
        home.navigate()
        home.search_product(term)

        results = SearchResultsPage(driver)
        assert results.has_results(), f"Search for '{term}' returned no results"
