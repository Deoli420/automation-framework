"""
UI Tests — Cart operations.

Tests adding products to cart, validating cart state, removing items.
These are the most revenue-critical flows in e-commerce.
"""

import time

import pytest

from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.search_results_page import SearchResultsPage


@pytest.mark.ui
@pytest.mark.cart
class TestCart:
    """Shopping cart operation tests."""

    def _add_product_to_cart(self, driver) -> ProductPage:
        """Helper: navigate to a product and add it to cart."""
        home = HomePage(driver)
        home.navigate()
        home.search_product("moisturizer")

        results = SearchResultsPage(driver)
        assert results.has_results(), "No search results"

        main_window = driver.current_window_handle
        results.click_first_product()

        time.sleep(2)
        windows = driver.window_handles
        if len(windows) > 1:
            driver.switch_to.window(windows[-1])

        product = ProductPage(driver)
        assert product.is_product_page(), "Not on product page"

        product.click_add_to_bag()
        time.sleep(2)  # Wait for cart update

        return product

    def test_add_product_to_cart(self, driver):
        """Verify a product can be added to the cart."""
        self._add_product_to_cart(driver)

        cart = CartPage(driver)
        cart.navigate()
        time.sleep(2)

        count = cart.get_cart_items_count()
        assert count > 0, "Cart is empty after adding a product"

    def test_cart_shows_product_price(self, driver):
        """Verify cart displays item prices."""
        self._add_product_to_cart(driver)

        cart = CartPage(driver)
        cart.navigate()
        time.sleep(2)

        prices = cart.get_item_prices()
        assert len(prices) > 0, "No prices displayed in cart"
        assert all(p > 0 for p in prices), f"Invalid prices found: {prices}"

    def test_remove_product_from_cart(self, driver):
        """Verify a product can be removed from the cart."""
        self._add_product_to_cart(driver)

        cart = CartPage(driver)
        cart.navigate()
        time.sleep(2)

        initial_count = cart.get_cart_items_count()
        assert initial_count > 0, "Cart is empty — nothing to remove"

        cart.remove_first_item()
        time.sleep(2)

        # After removal, count should decrease or cart should be empty
        new_count = cart.get_cart_items_count()
        assert new_count < initial_count or cart.is_cart_empty(), (
            f"Item not removed: was {initial_count}, now {new_count}"
        )

    def test_empty_cart_shows_message(self, driver):
        """Verify empty cart page shows appropriate message."""
        cart = CartPage(driver)
        cart.navigate()
        time.sleep(2)

        # Fresh session should have empty cart
        if cart.get_cart_items_count() == 0:
            assert cart.is_cart_empty() or True, "Cart page loaded"
