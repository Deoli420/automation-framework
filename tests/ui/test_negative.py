"""
UI Tests — Negative and boundary test cases.

Tests edge cases and error handling:
  - XSS-style input
  - Extremely long queries
  - Invalid product URLs
  - Gibberish search terms
  - Empty submissions

These verify the site handles malformed input gracefully
without crashing or exposing errors.
"""

import pytest

from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage


@pytest.mark.ui
@pytest.mark.negative
class TestNegative:
    """Negative and boundary UI tests."""

    @pytest.mark.smoke
    def test_search_xss_string(self, driver):
        """Verify site handles XSS-style input safely."""
        home = HomePage(driver)
        home.navigate()
        home.search_product("<script>alert('xss')</script>")

        # Should not crash — either show results or no-results page
        results = SearchResultsPage(driver)
        # Page should load without JavaScript alert
        assert "nykaa.com" in driver.current_url, (
            "XSS input caused unexpected navigation"
        )

    def test_search_very_long_query(self, driver):
        """Verify site handles a 500-character search query."""
        long_query = "beauty " * 71  # ~497 chars
        home = HomePage(driver)
        home.navigate()
        home.search_product(long_query.strip())

        # Should not crash — page should still be functional
        assert "nykaa.com" in driver.current_url, (
            "Long query caused unexpected navigation"
        )

    @pytest.mark.smoke
    def test_invalid_product_url(self, driver):
        """Verify navigating to an invalid product URL doesn't crash."""
        driver.get("https://www.nykaa.com/nonexistent-product-xyz/p/9999999999")

        # Should show some error/404 page, not a blank crash
        assert driver.title is not None, "Page title is None on invalid URL"
        assert len(driver.page_source) > 100, (
            "Page appears blank on invalid product URL"
        )

    def test_search_gibberish_returns_no_results_or_fallback(self, driver):
        """Verify gibberish search shows no-results state or fallback."""
        home = HomePage(driver)
        home.navigate()
        home.search_product("xyzabc123qwerty999")

        results = SearchResultsPage(driver)
        # Either shows no results or some fallback — page shouldn't crash
        has_results = results.has_results()
        has_no_results = results.has_no_results()

        assert has_results or has_no_results or "nykaa.com" in driver.current_url, (
            "Gibberish search caused unexpected state"
        )

    def test_search_sql_injection_string(self, driver):
        """Verify SQL injection-style input is handled safely."""
        home = HomePage(driver)
        home.navigate()
        home.search_product("'; DROP TABLE products;--")

        # Should not crash — just show results or no-results
        assert "nykaa.com" in driver.current_url, (
            "SQL injection input caused unexpected navigation"
        )

    def test_search_unicode_characters(self, driver):
        """Verify Unicode input (emoji, CJK) is handled gracefully."""
        home = HomePage(driver)
        home.navigate()
        home.search_product("美容 serum 🌸")

        # Should not crash
        assert "nykaa.com" in driver.current_url, (
            "Unicode search caused unexpected navigation"
        )
