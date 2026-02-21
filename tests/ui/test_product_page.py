"""
UI Tests — Product Detail Page (PDP).

Tests product page structure: title, price, images, add-to-bag button.
"""

import pytest

from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.search_results_page import SearchResultsPage


@pytest.mark.ui
@pytest.mark.product
class TestProductPage:
    """Product detail page tests."""

    def _navigate_to_first_product(self, driver) -> ProductPage:
        """Helper: search and click first product."""
        home = HomePage(driver)
        home.navigate()
        home.search_product("lipstick")

        results = SearchResultsPage(driver)
        assert results.has_results(), "No search results to click"

        # Store main window
        main_window = driver.current_window_handle
        results.click_first_product()

        # Product may open in new tab
        import time
        time.sleep(2)
        windows = driver.window_handles
        if len(windows) > 1:
            driver.switch_to.window(windows[-1])

        return ProductPage(driver)

    def test_product_page_has_title(self, driver):
        """Verify product page displays a title."""
        product = self._navigate_to_first_product(driver)
        assert product.is_product_page(), "Not on a product page"

        title = product.get_product_title()
        assert len(title) > 0, "Product title is empty"

    def test_product_page_has_price(self, driver):
        """Verify product page displays a valid price."""
        product = self._navigate_to_first_product(driver)
        assert product.is_product_page(), "Not on a product page"

        price = product.get_selling_price()
        assert price > 0, f"Invalid price: {price}"

    def test_product_page_has_image(self, driver):
        """Verify product page shows at least one product image."""
        product = self._navigate_to_first_product(driver)
        assert product.has_product_image(), "No product image found"

    def test_product_page_has_add_to_bag(self, driver):
        """Verify 'Add to Bag' button is present."""
        product = self._navigate_to_first_product(driver)
        assert product.is_add_to_bag_visible(), "Add to Bag button not found"
