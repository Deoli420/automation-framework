"""
UI Tests — Cart operations.

Tests adding products to cart, validating cart state, removing items.
These are the most revenue-critical flows in e-commerce.

IMPORTANT: Nykaa's cart (/checkout/cart) requires authentication.
Guest users see an error/redirect. The class-level
``@pytest.mark.auth_required`` marker triggers auto-skip via
``conftest.pytest_collection_modifyitems``. Provide a login fixture
to activate these tests.
"""

import pytest
from selenium.webdriver.support.ui import WebDriverWait

from core.config import settings
from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.search_results_page import SearchResultsPage
from utils.waits import window_count_greater_than, page_has_loaded


@pytest.mark.ui
@pytest.mark.cart
@pytest.mark.auth_required
class TestCart:
    """Shopping cart operation tests (require authentication)."""

    def _add_product_to_cart(self, driver) -> ProductPage:
        """Helper: navigate to a product and add it to cart."""
        home = HomePage(driver)
        home.navigate()
        home.search_product("cetaphil gentle cleanser")

        results = SearchResultsPage(driver)
        assert results.has_results(), "No search results"

        initial_windows = len(driver.window_handles)
        results.click_first_product()

        # Wait for new tab instead of time.sleep
        try:
            WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
                window_count_greater_than(initial_windows)
            )
            driver.switch_to.window(driver.window_handles[-1])
        except Exception:
            pass

        product = ProductPage(driver)
        assert product.is_product_page(), "Not on product page"

        product.click_add_to_bag()
        # Wait for cart icon to update
        WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
            page_has_loaded()
        )
        return product

    def test_add_product_to_cart(self, driver):
        """Verify a product can be added to the cart."""
        self._add_product_to_cart(driver)

        cart = CartPage(driver)
        cart.navigate()
        WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
            page_has_loaded()
        )

        count = cart.get_cart_items_count()
        assert count > 0, "Cart is empty after adding a product"

    def test_cart_shows_product_price(self, driver):
        """Verify cart displays item prices."""
        self._add_product_to_cart(driver)

        cart = CartPage(driver)
        cart.navigate()
        WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
            page_has_loaded()
        )

        prices = cart.get_item_prices()
        assert len(prices) > 0, "No prices displayed in cart"
        assert all(p > 0 for p in prices), f"Invalid prices found: {prices}"

    def test_remove_product_from_cart(self, driver):
        """Verify a product can be removed from the cart."""
        self._add_product_to_cart(driver)

        cart = CartPage(driver)
        cart.navigate()
        WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
            page_has_loaded()
        )

        initial_count = cart.get_cart_items_count()
        assert initial_count > 0, "Cart is empty — nothing to remove"

        cart.remove_first_item()
        WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
            page_has_loaded()
        )

        # After removal, count should decrease or cart should be empty
        new_count = cart.get_cart_items_count()
        assert new_count < initial_count or cart.is_cart_empty(), (
            f"Item not removed: was {initial_count}, now {new_count}"
        )

    def test_empty_cart_shows_message(self, driver):
        """Verify empty cart page shows appropriate message."""
        cart = CartPage(driver)
        cart.navigate()
        WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
            page_has_loaded()
        )

        # Fresh session should have empty cart
        assert cart.is_cart_empty(), "Fresh session cart should be empty"
