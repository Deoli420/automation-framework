"""
Cross-layer validation — UI price vs API price.

The highest-value test in the framework: navigates to a product page,
extracts the UI price from the DOM, then queries the inventory API for
the same product ID and compares prices.

Catches:
  - CDN cache staleness (UI shows old price, API has new one)
  - SSR hydration mismatch (server-rendered price differs from client)
  - Price propagation delays across microservices

This test bridges the UI and API layers — proving they can work together
to validate the same data from two independent sources.
"""

import logging

import pytest
from selenium.webdriver.support.ui import WebDriverWait

from core.config import settings
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.search_results_page import SearchResultsPage
from services.api_client import ApiClient
from services.product_service import ProductService
from utils.waits import window_count_greater_than, page_has_loaded

logger = logging.getLogger(__name__)


@pytest.mark.ui
@pytest.mark.cross_layer
@pytest.mark.regression
class TestCrossLayerPrice:
    """Cross-layer price validation: UI DOM vs inventory API."""

    def test_pdp_price_matches_api_price(self, driver):
        """
        Navigate to a product page, read the UI selling price,
        then query the inventory API for the same product ID.
        Assert they match within tolerance.
        """
        # ── Step 1: Navigate to a known product via search ──────────
        home = HomePage(driver)
        home.navigate()
        home.search_product("maybelline fit me foundation")

        results = SearchResultsPage(driver)
        assert results.has_results(), "No search results found"

        initial_windows = len(driver.window_handles)
        results.click_first_product()

        # Wait for PDP to open (may open in new tab)
        try:
            WebDriverWait(driver, settings.EXPLICIT_WAIT).until(
                window_count_greater_than(initial_windows)
            )
            driver.switch_to.window(driver.window_handles[-1])
        except Exception:
            pass

        product = ProductPage(driver)
        assert product.is_product_page(), "Not on a product detail page"

        # ── Step 2: Extract UI price and product ID ─────────────────
        ui_price = product.get_selling_price()
        product_id = product.get_product_id_from_url()

        logger.info(
            "UI layer: product_id=%s, price=%.2f", product_id, ui_price
        )

        assert ui_price > 0, f"UI price is invalid: {ui_price}"
        assert product_id, "Could not extract product ID from URL"

        # ── Step 3: Query inventory API for same product ────────────
        api_client = ApiClient()
        try:
            service = ProductService(client=api_client)
            api_response = service.get_product_details(product_id)

            if api_response.status_code == 403:
                pytest.skip(
                    "WAF blocked API request — cannot validate cross-layer"
                )

            assert api_response.status_code == 200, (
                f"Inventory API returned {api_response.status_code}"
            )

            # ── Step 4: Extract API price ───────────────────────────
            data = api_response.json_body
            assert data, "API returned empty response body"

            # Navigate the inventory response structure
            response = data.get("response", {})
            inventory = response.get("inventory_details", {})

            if not inventory:
                pytest.skip(
                    f"No inventory data for product {product_id} — "
                    "endpoint may have changed structure"
                )

            # inventory_details is keyed by SKU ID
            sku_data = next(iter(inventory.values()), {})
            api_price = float(sku_data.get("price", 0) or 0)

            if api_price == 0:
                # Try alternate field names
                api_price = float(
                    sku_data.get("selling_price", 0)
                    or sku_data.get("sp", 0)
                    or 0
                )

            logger.info("API layer: price=%.2f", api_price)

            if api_price == 0:
                pytest.skip(
                    "Could not extract price from API response — "
                    "field names may have changed"
                )

            # ── Step 5: Compare with tolerance ──────────────────────
            tolerance = 1.0  # ₹1 tolerance for rounding
            diff = abs(ui_price - api_price)

            assert diff <= tolerance, (
                f"Price mismatch! UI={ui_price}, API={api_price}, "
                f"diff={diff} (tolerance={tolerance})"
            )

            logger.info(
                "✅ Cross-layer price match: UI=%.2f, API=%.2f (diff=%.2f)",
                ui_price,
                api_price,
                diff,
            )

        finally:
            api_client.close()
