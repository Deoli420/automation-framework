"""
API Tests — Product endpoint validation.

Tests the API client framework against Nykaa's working product endpoints:
  - /gateway-api/inventory/data/json/ — inventory check
  - /gateway-api/offer/api/v2/product/customer/offer — product offers

The old /gateway-api/products/{id} endpoint is dead (404).
"""

import pytest

from services.api_client import ApiResponse
from services.product_service import ProductService
from services.schema_validator import SchemaValidator
from utils.data_generator import load_schema


# Real Nykaa product IDs (confirmed from live site inspection)
_KNOWN_PRODUCT_ID = "24700514"  # Maybelline Serum Matte Lipstick


@pytest.mark.api
@pytest.mark.product
class TestProductApi:
    """Product API validation tests."""

    def test_product_endpoint_returns_response(self, api_client):
        """Verify inventory endpoint returns a valid ApiResponse."""
        service = ProductService(client=api_client)
        response = service.get_product_details(_KNOWN_PRODUCT_ID)

        assert isinstance(response, ApiResponse), "Did not return ApiResponse"
        assert response.status_code > 0, "No HTTP status received"
        assert response.status_code != 500, (
            f"Server error: {response.error_message}"
        )

    def test_product_response_time_measured(self, api_client):
        """Verify response time is captured for product API."""
        service = ProductService(client=api_client)
        response = service.get_product_details(_KNOWN_PRODUCT_ID)

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
        response = service.get_product_by_slug(
            "maybelline-new-york-serum-matte-lipstick"
        )

        assert isinstance(response, ApiResponse)
        assert response.response_time_ms > 0

    def test_inventory_schema_validation(self, api_client):
        """Validate inventory response against JSON schema."""
        service = ProductService(client=api_client)
        response = service.get_product_details(_KNOWN_PRODUCT_ID)

        if response.status_code == 403:
            pytest.skip("WAF blocked request (403)")

        if response.body is None:
            pytest.skip("No response body to validate")

        schema = load_schema("product_response")
        valid, msg = SchemaValidator.validate(response.body, schema)
        assert valid, f"Inventory schema validation failed: {msg}"

    def test_product_offers_endpoint(self, api_client):
        """Verify product offers endpoint returns a response."""
        service = ProductService(client=api_client)
        response = service.get_product_offers([_KNOWN_PRODUCT_ID])

        assert isinstance(response, ApiResponse)
        assert response.status_code > 0, "No status received from offers API"
        assert response.response_time_ms > 0
