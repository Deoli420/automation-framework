"""
Nykaa product API service wrapper.

Encapsulates product detail endpoint interactions for API validation.
"""

import logging
from typing import Optional

from services.api_client import ApiClient, ApiResponse

logger = logging.getLogger(__name__)


class ProductService:
    """API wrapper for Nykaa product detail functionality."""

    PRODUCT_PATH = "/gateway-api/products"

    def __init__(self, client: Optional[ApiClient] = None) -> None:
        self.client = client or ApiClient()

    def get_product_details(self, product_id: str) -> ApiResponse:
        """
        Fetch product details by ID.

        Args:
            product_id: Nykaa product SKU/ID

        Returns:
            ApiResponse with product detail payload
        """
        logger.info("API product detail: id=%s", product_id)
        return self.client.get(
            f"{self.PRODUCT_PATH}/{product_id}",
        )

    def get_product_by_slug(self, slug: str) -> ApiResponse:
        """
        Fetch product details by URL slug.

        Args:
            slug: Product URL slug

        Returns:
            ApiResponse with product payload
        """
        logger.info("API product by slug: %s", slug)
        return self.client.get(
            self.PRODUCT_PATH,
            params={"slug": slug},
        )
