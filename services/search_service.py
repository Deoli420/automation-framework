"""
Nykaa search API service wrapper.

Encapsulates search endpoint interactions for API validation tests.
"""

import logging
from typing import Optional

from services.api_client import ApiClient, ApiResponse

logger = logging.getLogger(__name__)


class SearchService:
    """API wrapper for Nykaa search functionality."""

    # Nykaa's public search endpoint pattern
    SEARCH_PATH = "/gateway-api/search/products"

    def __init__(self, client: Optional[ApiClient] = None) -> None:
        self.client = client or ApiClient()

    def search_products(
        self,
        query: str,
        page: int = 1,
        count: int = 20,
    ) -> ApiResponse:
        """
        Search for products via Nykaa's API.

        Args:
            query: Search term
            page: Page number (1-based)
            count: Results per page

        Returns:
            ApiResponse with search results
        """
        logger.info("API search: query='%s' page=%d count=%d", query, page, count)
        params = {
            "keyword": query,
            "page_no": page,
            "count": count,
        }
        return self.client.get(self.SEARCH_PATH, params=params)

    def get_search_suggestions(self, query: str) -> ApiResponse:
        """Get search autocomplete suggestions."""
        logger.info("API suggestions: query='%s'", query)
        return self.client.get(
            "/gateway-api/search/suggest",
            params={"keyword": query},
        )
