"""
UI Tests — Product Detail Page (PDP).

Tests product page structure: title, price, images, add-to-bag button.

Selectors target real Nykaa PDP DOM:
  - h1 for title (only one on page)
  - Price spans within container
  - img[alt="product-thumbnail"] for images
  - XPath text match for "Add to Bag" button
"""

import pytest
from selenium.webdriver.support.ui import WebDriverWait

from core.config import settings
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.search_results_page import SearchResultsPage
from utils.waits import window_count_greater_than, page_has_loaded


@pytest.mark.ui
@pytest.mark.product
class TestProductPage:
    """Product detail page tests."""

    def _navigate_to_first_product(self, driver) -> ProductPage:
        """Helper: search and click first product."""
        home = HomePage(driver)
        home.navigate()
        # Multi-word query stays on search results page
        home.search_product("nykaa matte lipstick")

        results = SearchResultsPage(driver)
        assert results.has_results(), "No search results to click"

        initial_windows = len(driver.window_handles)
        results.click_first_product()

        # Wait for new tab instead of time.sleep(2)
        try:
            WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
                window_count_greater_than(initial_windows)
            )
            driver.switch_to.window(driver.window_handles[-1])
        except Exception:
            pass  # Product opened in same tab

        # Wait for PDP to fully load
        WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
            page_has_loaded()
        )
        return ProductPage(driver)

    @pytest.mark.smoke
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
