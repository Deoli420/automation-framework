"""
API Tests — Negative and boundary test cases.

Tests edge cases for the API client framework:
  - Very long query strings (1000+ chars)
  - SQL injection patterns
  - Unicode characters
  - Empty/null parameters
  - Malformed requests

Validates framework resilience — not API correctness.
"""

import pytest

from services.api_client import ApiResponse
from services.search_service import SearchService


@pytest.mark.api
@pytest.mark.negative
class TestNegativeApi:
    """Negative API test cases."""

    def test_very_long_query(self, api_client):
        """Verify API client handles a 1000-character query."""
        service = SearchService(client=api_client)
        long_query = "lipstick " * 125  # ~1000 chars
        response = service.search_products(long_query.strip())

        assert isinstance(response, ApiResponse)
        assert response.response_time_ms > 0, "Timing not captured"

    def test_sql_injection_string(self, api_client):
        """Verify API client handles SQL injection-style input."""
        service = SearchService(client=api_client)
        response = service.search_products("'; DROP TABLE products;--")

        assert isinstance(response, ApiResponse)
        assert response.status_code != 500, (
            f"Server error on SQL injection: {response.error_message}"
        )

    def test_unicode_characters(self, api_client):
        """Verify API client handles Unicode characters."""
        service = SearchService(client=api_client)
        response = service.search_products("美容 serum 🌸")

        assert isinstance(response, ApiResponse)
        assert response.response_time_ms > 0

    def test_empty_parameter(self, api_client):
        """Verify API client handles empty string parameter."""
        service = SearchService(client=api_client)
        response = service.search_products("")

        assert isinstance(response, ApiResponse)
        # Should not crash — may return 400 or empty results
        assert response.response_time_ms > 0

    def test_special_url_characters(self, api_client):
        """Verify API client handles URL-unsafe characters."""
        service = SearchService(client=api_client)
        response = service.search_products("test?param=value&other=1#hash")

        assert isinstance(response, ApiResponse)
        assert response.response_time_ms > 0

    def test_html_tags_in_query(self, api_client):
        """Verify API client handles HTML tags in query."""
        service = SearchService(client=api_client)
        response = service.search_products(
            "<img src=x onerror=alert(1)>"
        )

        assert isinstance(response, ApiResponse)
        assert response.status_code != 500, "Server error on HTML tags"
