"""
Page object for Nykaa product detail page (PDP).

Handles: product title, price, images, add-to-bag.
"""

import logging
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from core.base_page import BasePage

logger = logging.getLogger(__name__)


class ProductPage(BasePage):
    """Nykaa product detail page interactions."""

    # ── Locators ──────────────────────────────────────────────────────
    PRODUCT_TITLE = (By.CSS_SELECTOR, "h1[class*='title'], h1[class*='name'], h1")
    SELLING_PRICE = (
        By.CSS_SELECTOR,
        "[class*='selling-price'], [class*='final-price'], [class*='price']",
    )
    MRP_PRICE = (
        By.CSS_SELECTOR,
        "[class*='mrp'], [class*='original-price'], [class*='strike']",
    )
    DISCOUNT = (By.CSS_SELECTOR, "[class*='discount'], [class*='off']")
    ADD_TO_BAG = (
        By.CSS_SELECTOR,
        "button[class*='add-to-bag'], button[class*='add-to-cart'], "
        "button[class*='addToBag']",
    )
    PRODUCT_IMAGE = (By.CSS_SELECTOR, "img[class*='product'], img[class*='slider']")
    SIZE_VARIANT = (By.CSS_SELECTOR, "[class*='variant'], [class*='size-selector']")
    BREADCRUMB = (By.CSS_SELECTOR, "[class*='breadcrumb']")
    CART_ICON = (By.CSS_SELECTOR, "[class*='cart'] [class*='count'], [class*='bag-count']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__(driver)

    def get_product_title(self) -> str:
        """Get the product title text."""
        return self.get_text(self.PRODUCT_TITLE)

    def get_selling_price(self) -> float:
        """Get the selling price as a float."""
        text = self.get_text(self.SELLING_PRICE)
        return self.parse_price(text)

    def get_mrp_price(self) -> float:
        """Get the MRP (original) price as a float."""
        try:
            text = self.get_text(self.MRP_PRICE)
            return self.parse_price(text)
        except Exception:
            # MRP may not exist if product is not discounted
            return 0.0

    def get_discount_text(self) -> str:
        """Get discount percentage text (e.g., '20% Off')."""
        try:
            return self.get_text(self.DISCOUNT)
        except Exception:
            return ""

    def click_add_to_bag(self) -> None:
        """Scroll to and click the Add to Bag button."""
        logger.info("Adding product to bag")
        self.scroll_to_element(self.ADD_TO_BAG)
        self.click(self.ADD_TO_BAG)

    def is_add_to_bag_visible(self) -> bool:
        """Check if Add to Bag button is present."""
        return self.is_element_visible(self.ADD_TO_BAG)

    def has_product_image(self) -> bool:
        """Check if product image is loaded."""
        return self.is_element_visible(self.PRODUCT_IMAGE)

    def is_product_page(self) -> bool:
        """Verify we're on a product detail page."""
        return (
            self.is_element_visible(self.PRODUCT_TITLE, timeout=10)
            and self.is_element_visible(self.SELLING_PRICE, timeout=5)
        )

    def get_product_id_from_url(self) -> str:
        """Extract product ID from current URL."""
        url = self.get_current_url()
        # Nykaa URLs: /product-name/p/SKU_ID
        match = re.search(r"/p/(\d+)", url)
        return match.group(1) if match else ""
