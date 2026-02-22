"""
Nykaa search API service wrapper.

Encapsulates search endpoint interactions for API validation tests.

Working endpoints (verified Feb 2025):
  - /gludo/searchSuggestions?q=...  — autocomplete suggestions
  - /search/trending                — trending searches

Dead endpoints (404):
  - /gateway-api/search/products    — returns 404 "no Route matched"
  - /gateway-api/search/suggest     — dead
"""

import logging
from typing import Optional

from services.api_client import ApiClient, ApiResponse

logger = logging.getLogger(__name__)


class SearchService:
    """API wrapper for Nykaa search functionality."""

    # Working endpoint — autocomplete/search suggestions
    SUGGESTIONS_PATH = "/gludo/searchSuggestions"
    # Working endpoint — trending searches
    TRENDING_PATH = "/search/trending"

    def __init__(self, client: Optional[ApiClient] = None) -> None:
        self.client = client or ApiClient()

    def search_products(self, query: str) -> ApiResponse:
        """
        Search for product suggestions via Nykaa's autocomplete API.

        This uses the working /gludo/searchSuggestions endpoint.
        The old /gateway-api/search/products endpoint returns 404.

        Args:
            query: Search term

        Returns:
            ApiResponse with suggestion results
        """
        logger.info("API search suggestions: query='%s'", query)
        return self.client.get(
            self.SUGGESTIONS_PATH,
            params={"q": query},
        )

    def get_search_suggestions(self, query: str) -> ApiResponse:
        """Get search autocomplete suggestions (alias)."""
        return self.search_products(query)

    def get_trending_searches(self) -> ApiResponse:
        """Fetch trending/popular search terms."""
        logger.info("API trending searches")
        return self.client.get(self.TRENDING_PATH)
