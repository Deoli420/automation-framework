"""
API Tests — HTTP method framework validation.

Tests that ApiClient correctly handles all HTTP methods (POST, PUT,
DELETE, HEAD). These hit Nykaa endpoints which will return 403/405 —
we're testing the framework's resilience, not API correctness.
"""

import pytest

from services.api_client import ApiClient, ApiResponse


@pytest.mark.api
class TestHttpMethods:
    """Validate ApiClient handles all HTTP methods correctly."""

    def test_post_returns_response(self, api_client):
        """Verify POST request returns a structured ApiResponse."""
        response = api_client.post(
            "/gateway-api/offer/api/v2/product/customer/offer",
            json_body={"skuId": ["12345"]},
        )

        assert isinstance(response, ApiResponse)
        assert response.status_code > 0, "No status code on POST"
        assert response.response_time_ms > 0, "Timing not captured on POST"

    def test_head_returns_response(self, api_client):
        """Verify HEAD request returns a structured ApiResponse."""
        response = api_client.head("/")

        assert isinstance(response, ApiResponse)
        assert response.status_code > 0, "No status code on HEAD"
        assert response.response_time_ms > 0, "Timing not captured on HEAD"

    def test_put_handled_gracefully(self, api_client):
        """Verify PUT request doesn't crash (will get 403/405)."""
        response = api_client.put(
            "/gateway-api/inventory/data/json/",
            json_body={"test": "data"},
        )

        assert isinstance(response, ApiResponse)
        assert response.response_time_ms > 0

    def test_delete_handled_gracefully(self, api_client):
        """Verify DELETE request doesn't crash (will get 403/405)."""
        response = api_client.delete("/gateway-api/inventory/data/json/")

        assert isinstance(response, ApiResponse)
        assert response.response_time_ms > 0

    def test_all_methods_measure_timing(self, api_client):
        """Verify all HTTP methods capture response timing."""
        methods = {
            "GET": api_client.get("/"),
            "HEAD": api_client.head("/"),
            "POST": api_client.post("/", json_body={}),
        }

        for method_name, response in methods.items():
            assert response.response_time_ms > 0, (
                f"{method_name} did not capture timing"
            )
            assert isinstance(response, ApiResponse), (
                f"{method_name} did not return ApiResponse"
            )
