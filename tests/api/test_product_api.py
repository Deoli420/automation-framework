"""
API Tests — Product detail endpoint validation.

Tests the API client framework against Nykaa's product endpoints.
Validates framework resilience, timing, and error handling.
"""

import pytest

from services.api_client import ApiResponse
from services.product_service import ProductService


@pytest.mark.api
@pytest.mark.product
class TestProductApi:
    """Product API validation tests."""

    def test_product_endpoint_returns_response(self, api_client):
        """Verify product endpoint returns a valid ApiResponse."""
        service = ProductService(client=api_client)
        response = service.get_product_details("1")

        assert isinstance(response, ApiResponse), "Did not return ApiResponse"
        assert response.status_code > 0, "No HTTP status received"
        assert response.status_code != 500, (
            f"Server error: {response.error_message}"
        )

    def test_product_response_time_measured(self, api_client):
        """Verify response time is captured for product API."""
        service = ProductService(client=api_client)
        response = service.get_product_details("1")

        assert response.response_time_ms > 0, "Response time not measured"
        assert response.response_time_ms < 15000, (
            f"Product API took {response.response_time_ms}ms"
        )

    def test_product_nonexistent_id_handled(self, api_client):
        """Verify framework handles nonexistent product IDs gracefully."""
        service = ProductService(client=api_client)
        response = service.get_product_details("nonexistent_99999999")

        # Should return an ApiResponse, not crash
        assert isinstance(response, ApiResponse)
        assert response.response_time_ms > 0

    def test_product_by_slug(self, api_client):
        """Verify slug-based product lookup returns a response."""
        service = ProductService(client=api_client)
        response = service.get_product_by_slug("test-product")

        assert isinstance(response, ApiResponse)
        assert response.response_time_ms > 0
