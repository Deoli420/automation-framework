"""
UI Tests — Cart pricing consistency.

The #1 automated check in e-commerce: verify that individual item
prices sum up to the displayed cart total. Catches stale caches,
rounding errors, and calculation mismatches.
"""

import time

import pytest

from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.search_results_page import SearchResultsPage


@pytest.mark.ui
@pytest.mark.cart
@pytest.mark.pricing
class TestCartPricing:
    """Cart pricing validation tests."""

    def _add_product_and_go_to_cart(self, driver) -> CartPage:
        """Helper: search, click product, add to bag, navigate to cart."""
        home = HomePage(driver)
        home.navigate()
        home.search_product("serum")

        results = SearchResultsPage(driver)
        assert results.has_results(), "No search results for serum"

        main_window = driver.current_window_handle
        results.click_first_product()

        time.sleep(2)
        windows = driver.window_handles
        if len(windows) > 1:
            driver.switch_to.window(windows[-1])

        product = ProductPage(driver)
        if product.is_product_page():
            product.click_add_to_bag()
            time.sleep(2)

        cart = CartPage(driver)
        cart.navigate()
        time.sleep(2)
        return cart

    def test_cart_total_matches_item_sum(self, driver):
        """
        Verify displayed total matches sum of individual item prices.

        This is the most critical pricing check — catches:
        - Stale price caches
        - Rounding errors in tax/discount calculations
        - Frontend-backend price mismatches
        """
        cart = self._add_product_and_go_to_cart(driver)

        if cart.get_cart_items_count() == 0:
            pytest.skip("Cart is empty — could not add product")

        breakdown = cart.validate_pricing()

        assert breakdown.is_consistent, (
            f"Price mismatch! Items sum to {breakdown.calculated_sum}, "
            f"but total shows {breakdown.displayed_total} "
            f"(difference: {breakdown.difference})"
        )

    def test_product_price_matches_cart_price(self, driver):
        """
        Verify the price shown on PDP matches the price in cart.

        Catches: CDN caching issues, price update propagation delays.
        """
        home = HomePage(driver)
        home.navigate()
        home.search_product("foundation")

        results = SearchResultsPage(driver)
        assert results.has_results(), "No search results"

        main_window = driver.current_window_handle
        results.click_first_product()

        time.sleep(2)
        windows = driver.window_handles
        if len(windows) > 1:
            driver.switch_to.window(windows[-1])

        product = ProductPage(driver)
        if not product.is_product_page():
            pytest.skip("Could not navigate to product page")

        pdp_price = product.get_selling_price()
        assert pdp_price > 0, "Could not read PDP price"

        product.click_add_to_bag()
        time.sleep(2)

        cart = CartPage(driver)
        cart.navigate()
        time.sleep(2)

        if cart.get_cart_items_count() == 0:
            pytest.skip("Cart empty after add-to-bag")

        cart_prices = cart.get_item_prices()
        assert len(cart_prices) > 0, "No prices in cart"

        # The PDP price should appear in cart prices (allow ₹1 tolerance)
        price_found = any(
            abs(cp - pdp_price) < 1.0 for cp in cart_prices
        )
        assert price_found, (
            f"PDP price {pdp_price} not found in cart prices {cart_prices}"
        )
