"""
UI Tests — Cart pricing consistency.

The #1 automated check in e-commerce: verify that individual item
prices sum up to the displayed cart total. Catches stale caches,
rounding errors, and calculation mismatches.

IMPORTANT: Nykaa's cart (/checkout/cart) requires authentication.
Guest users see an error/redirect. All cart pricing tests are marked
with ``@pytest.mark.auth_required`` and skipped by default.
"""

import pytest
from selenium.webdriver.support.ui import WebDriverWait

from core.config import settings
from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.search_results_page import SearchResultsPage
from utils.waits import window_count_greater_than, page_has_loaded


_AUTH_SKIP = "Cart requires authentication — no login fixture available"


@pytest.mark.ui
@pytest.mark.cart
@pytest.mark.pricing
@pytest.mark.auth_required
class TestCartPricing:
    """Cart pricing validation tests (require authentication)."""

    def _add_product_and_go_to_cart(self, driver) -> CartPage:
        """Helper: search, click product, add to bag, navigate to cart."""
        home = HomePage(driver)
        home.navigate()
        home.search_product("vitamin c serum for oily skin")

        results = SearchResultsPage(driver)
        assert results.has_results(), "No search results for serum"

        initial_windows = len(driver.window_handles)
        results.click_first_product()

        # Wait for new tab
        try:
            WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
                window_count_greater_than(initial_windows)
            )
            driver.switch_to.window(driver.window_handles[-1])
        except Exception:
            pass

        product = ProductPage(driver)
        if product.is_product_page():
            product.click_add_to_bag()
            WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
                page_has_loaded()
            )

        cart = CartPage(driver)
        cart.navigate()
        WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
            page_has_loaded()
        )
        return cart

    @pytest.mark.skip(reason=_AUTH_SKIP)
    def test_cart_total_matches_item_sum(self, driver):
        """
        Verify displayed total matches sum of individual item prices.

        This is the most critical pricing check — catches:
        - Stale price caches
        - Rounding errors in tax/discount calculations
        - Frontend-backend price mismatches
        """
        cart = self._add_product_and_go_to_cart(driver)

        assert cart.get_cart_items_count() > 0, (
            "Cart is empty — could not add product"
        )

        breakdown = cart.validate_pricing()

        assert breakdown.is_consistent, (
            f"Price mismatch! Items sum to {breakdown.calculated_sum}, "
            f"but total shows {breakdown.displayed_total} "
            f"(difference: {breakdown.difference})"
        )

    @pytest.mark.skip(reason=_AUTH_SKIP)
    def test_product_price_matches_cart_price(self, driver):
        """
        Verify the price shown on PDP matches the price in cart.

        Catches: CDN caching issues, price update propagation delays.
        """
        home = HomePage(driver)
        home.navigate()
        home.search_product("mac studio fix foundation")

        results = SearchResultsPage(driver)
        assert results.has_results(), "No search results"

        initial_windows = len(driver.window_handles)
        results.click_first_product()

        try:
            WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
                window_count_greater_than(initial_windows)
            )
            driver.switch_to.window(driver.window_handles[-1])
        except Exception:
            pass

        product = ProductPage(driver)
        assert product.is_product_page(), "Could not navigate to product page"

        pdp_price = product.get_selling_price()
        assert pdp_price > 0, "Could not read PDP price"

        product.click_add_to_bag()
        WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
            page_has_loaded()
        )

        cart = CartPage(driver)
        cart.navigate()
        WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
            page_has_loaded()
        )

        assert cart.get_cart_items_count() > 0, "Cart empty after add-to-bag"

        cart_prices = cart.get_item_prices()
        assert len(cart_prices) > 0, "No prices in cart"

        # The PDP price should appear in cart prices (allow ₹1 tolerance)
        price_found = any(
            abs(cp - pdp_price) < 1.0 for cp in cart_prices
        )
        assert price_found, (
            f"PDP price {pdp_price} not found in cart prices {cart_prices}"
        )
