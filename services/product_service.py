"""
Nykaa product API service wrapper.

Encapsulates product detail endpoint interactions for API validation.

Working endpoints (verified Feb 2025):
  - /gateway-api/inventory/data/json/  — inventory/stock check
  - /gateway-api/offer/api/v2/product/customer/offer — product offers

Dead endpoints (404):
  - /gateway-api/products/{id}   — returns 404 "no Route matched"

Note: Product data on Nykaa is primarily SSR'd into
``window.__PRELOADED_STATE__`` (Redux store), not fetched via XHR.
"""

import logging
from typing import List, Optional

from services.api_client import ApiClient, ApiResponse

logger = logging.getLogger(__name__)


class ProductService:
    """API wrapper for Nykaa product functionality."""

    # Working endpoints
    INVENTORY_PATH = "/gateway-api/inventory/data/json/"
    OFFERS_PATH = "/gateway-api/offer/api/v2/product/customer/offer"

    def __init__(self, client: Optional[ApiClient] = None) -> None:
        self.client = client or ApiClient()

    def get_product_details(self, product_id: str) -> ApiResponse:
        """
        Fetch product inventory/availability by ID.

        Uses the working inventory endpoint instead of the dead
        /gateway-api/products/ endpoint.

        Args:
            product_id: Nykaa product SKU/ID

        Returns:
            ApiResponse with inventory data
        """
        logger.info("API inventory check: id=%s", product_id)
        return self.client.get(
            self.INVENTORY_PATH,
            params={"productId": product_id},
        )

    def get_product_offers(self, product_ids: List[str]) -> ApiResponse:
        """
        Fetch offers/promotions for given product IDs.

        Args:
            product_ids: List of Nykaa product SKU/IDs

        Returns:
            ApiResponse with offer data
        """
        logger.info("API product offers: ids=%s", product_ids)
        return self.client.post(
            self.OFFERS_PATH,
            json_body={"skuId": product_ids},
        )

    def get_product_by_slug(self, slug: str) -> ApiResponse:
        """
        Fetch product details by URL slug via inventory endpoint.

        Args:
            slug: Product URL slug

        Returns:
            ApiResponse with product payload
        """
        logger.info("API product by slug: %s", slug)
        return self.client.get(
            self.INVENTORY_PATH,
            params={"slug": slug},
        )
