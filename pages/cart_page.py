"""
Page object for Nykaa shopping cart page.

Handles: cart items, pricing breakdown, remove items.

IMPORTANT: The Nykaa cart page at /checkout/cart **requires
authentication**. Guest users see an error/redirect to login.
Cart tests should be marked with ``@pytest.mark.auth_required``
and skipped when running without credentials.

The page object and pricing validation logic are kept intact to
demonstrate cart testing architecture — they can be activated once
a login fixture is available.
"""

import logging
import re
from dataclasses import dataclass
from typing import Dict, List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from core.base_page import BasePage

logger = logging.getLogger(__name__)


@dataclass
class PricingBreakdown:
    """Cart pricing validation result."""

    item_prices: List[float]
    displayed_total: float
    calculated_sum: float
    difference: float
    is_consistent: bool


class CartPage(BasePage):
    """Nykaa shopping cart interactions (requires authentication)."""

    # ── Locators ──────────────────────────────────────────────────────
    # These selectors target common cart element patterns. They will
    # be validated once a login fixture enables authenticated sessions.
    CART_ITEMS = (By.CSS_SELECTOR, "[class*='cart-item'], [class*='product-in-cart']")
    ITEM_PRICE = (By.CSS_SELECTOR, "[class*='item-price'], [class*='selling-price']")
    ITEM_TITLE = (By.CSS_SELECTOR, "[class*='item-name'], [class*='product-name']")
    REMOVE_BUTTON = (By.CSS_SELECTOR, "button[class*='remove'], [class*='delete']")
    CART_TOTAL = (By.CSS_SELECTOR, "[class*='total-price'], [class*='grand-total']")
    CART_SUBTOTAL = (By.CSS_SELECTOR, "[class*='sub-total']")
    EMPTY_CART_MSG = (By.CSS_SELECTOR, "[class*='empty-cart'], [class*='no-items']")
    CART_ICON = (By.CSS_SELECTOR, "[class*='cart-icon'], a[href*='cart']")
    QUANTITY_SELECTOR = (By.CSS_SELECTOR, "[class*='quantity'], select[class*='qty']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def navigate(self) -> "CartPage":
        """Navigate directly to the cart page."""
        self.open("/checkout/cart")
        logger.info("CartPage loaded")
        return self

    def get_cart_items_count(self) -> int:
        """Count items currently in cart."""
        items = self.driver.find_elements(*self.CART_ITEMS)
        return len(items)

    def get_cart_total(self) -> float:
        """Get the displayed cart total as float."""
        text = self.get_text(self.CART_TOTAL)
        return self.parse_price(text)

    def get_item_prices(self) -> List[float]:
        """Get all individual item prices in the cart."""
        elements = self.driver.find_elements(*self.ITEM_PRICE)
        prices = []
        for el in elements:
            price = self.parse_price(el.text)
            if price > 0:
                prices.append(price)
        return prices

    def get_item_titles(self) -> List[str]:
        """Get all item titles in the cart."""
        elements = self.driver.find_elements(*self.ITEM_TITLE)
        return [el.text for el in elements if el.text.strip()]

    def remove_first_item(self) -> None:
        """Click remove button on the first cart item."""
        logger.info("Removing first cart item")
        self.click(self.REMOVE_BUTTON)

    def is_cart_empty(self) -> bool:
        """Check if cart shows empty state."""
        return self.is_element_visible(self.EMPTY_CART_MSG, timeout=5)

    def validate_pricing(self) -> PricingBreakdown:
        """
        Cross-check item prices against displayed total.

        Returns a PricingBreakdown with consistency result.
        """
        item_prices = self.get_item_prices()
        total = self.get_cart_total()
        calculated_sum = sum(item_prices)
        difference = abs(total - calculated_sum)

        breakdown = PricingBreakdown(
            item_prices=item_prices,
            displayed_total=total,
            calculated_sum=calculated_sum,
            difference=difference,
            is_consistent=difference < 1.0,  # Allow ₹1 rounding tolerance
        )

        logger.info(
            "Pricing validation: items=%s, total=%.2f, sum=%.2f, diff=%.2f, consistent=%s",
            item_prices,
            total,
            calculated_sum,
            difference,
            breakdown.is_consistent,
        )
        return breakdown
