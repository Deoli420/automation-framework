"""
Page object for Nykaa product detail page (PDP).

Handles: product title, price, images, add-to-bag.

Selectors verified against live Nykaa DOM (Feb 2025):
  - Title: h1 (only one h1 on PDP — reliable)
  - Price container: div.css-1d0jf8e with 3 spans (MRP, selling, discount)
  - Add to Bag: button text match via XPath (two instances on page)
  - Product image: img[alt="product-thumbnail"]
  - Wishlist: button.custom-wishlist-button (stable class)
  - URL format confirmed: /product-name/p/NUMERIC_ID
"""

import logging
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from core.base_page import BasePage
from core.config import settings
from utils.waits import page_has_loaded

logger = logging.getLogger(__name__)


class ProductPage(BasePage):
    """Nykaa product detail page interactions."""

    # ── Locators (verified against live DOM) ──────────────────────────
    # Only one h1 on PDP — most reliable selector
    PRODUCT_TITLE = (By.CSS_SELECTOR, "h1")
    # Price container has 3 child spans: MRP, selling price, discount %
    SELLING_PRICE = (
        By.CSS_SELECTOR,
        "[class*='price'] span:nth-child(2), "
        "[class*='css-1d0jf8e'] span:nth-child(2), "
        "[class*='selling-price'], [class*='final-price']",
    )
    MRP_PRICE = (
        By.CSS_SELECTOR,
        "[class*='price'] span:first-child, "
        "[class*='css-1d0jf8e'] span:first-child, "
        "[class*='mrp'], [class*='strike']",
    )
    DISCOUNT = (
        By.CSS_SELECTOR,
        "[class*='price'] span:nth-child(3), "
        "[class*='discount'], [class*='off']",
    )
    # XPath text match — catches both the main and bottom-bar buttons
    ADD_TO_BAG = (
        By.XPATH,
        "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),'add to bag')]",
    )
    # Stable alt attribute and class for product images
    PRODUCT_IMAGE = (
        By.CSS_SELECTOR,
        "img[alt='product-thumbnail'], "
        ".slide-view-container img, "
        "img[class*='product']",
    )
    # Stable non-hashed class
    WISHLIST_BUTTON = (By.CSS_SELECTOR, "button.custom-wishlist-button")
    SIZE_VARIANT = (By.CSS_SELECTOR, "[class*='variant'], [class*='size-selector']")
    BREADCRUMB = (By.CSS_SELECTOR, "[class*='breadcrumb']")
    CART_ICON = (
        By.CSS_SELECTOR,
        "[class*='cart'] [class*='count'], [class*='bag-count']",
    )

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
        WebDriverWait(self.driver, settings.EXPLICIT_WAIT).until(
            page_has_loaded()
        )
        return (
            self.is_element_visible(self.PRODUCT_TITLE, timeout=10)
            and self.is_element_visible(self.SELLING_PRICE, timeout=5)
        )

    def get_product_id_from_url(self) -> str:
        """Extract product ID from current URL."""
        url = self.get_current_url()
        # Nykaa URLs: /product-name/p/SKU_ID (confirmed format)
        match = re.search(r"/p/(\d+)", url)
        return match.group(1) if match else ""
