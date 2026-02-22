"""
API Tests — Search endpoint validation.

Tests the API client framework behavior against Nykaa's working
search endpoints:
  - /gludo/searchSuggestions — autocomplete suggestions
  - /search/trending — trending searches

Note: Nykaa uses Akamai WAF which may block direct API requests (403).
Tests validate framework behavior regardless of response code.
"""

import pytest

from services.api_client import ApiResponse
from services.schema_validator import SchemaValidator
from services.search_service import SearchService
from utils.data_generator import get_random_search_term, load_schema


@pytest.mark.api
@pytest.mark.search
class TestSearchApi:
    """Search API validation tests."""

    def test_search_returns_response(self, api_client):
        """Verify search suggestions endpoint returns a valid ApiResponse."""
        service = SearchService(client=api_client)
        response = service.search_products("lipstick")

        assert isinstance(response, ApiResponse), "Did not return ApiResponse"
        assert response.status_code > 0, "No HTTP status code received"
        assert response.response_time_ms > 0, "Response time not measured"

    def test_search_response_time_is_measured(self, api_client):
        """Verify response time is accurately captured."""
        service = SearchService(client=api_client)
        response = service.search_products("moisturizer")

        assert response.response_time_ms > 0, "Response time is zero"
        assert response.response_time_ms < 30000, (
            f"Response took {response.response_time_ms}ms — likely hung"
        )

    def test_search_with_random_term(self, api_client):
        """Verify API client handles various search terms without crashing."""
        term = get_random_search_term()
        service = SearchService(client=api_client)
        response = service.search_products(term)

        assert isinstance(response, ApiResponse), (
            f"Search for '{term}' did not return ApiResponse"
        )
        assert response.status_code != 0, (
            f"Search for '{term}' got no response: {response.error_message}"
        )

    def test_search_handles_special_characters(self, api_client):
        """Verify API client handles special characters without crashing."""
        service = SearchService(client=api_client)
        response = service.search_products("l'oreal & co <script>")

        # Framework should handle this gracefully — no exception, no crash
        assert isinstance(response, ApiResponse)
        assert response.status_code != 500, "Server error on special characters"

    def test_search_empty_query(self, api_client):
        """Verify API client handles empty search query gracefully."""
        service = SearchService(client=api_client)
        response = service.search_products("")

        assert isinstance(response, ApiResponse)
        assert response.status_code != 500, "Server error on empty query"

    def test_search_response_headers_captured(self, api_client):
        """Verify response headers are captured in ApiResponse."""
        service = SearchService(client=api_client)
        response = service.search_products("sunscreen")

        assert isinstance(response.headers, dict), "Headers not captured"
        assert len(response.headers) > 0, "Headers dict is empty"

    def test_api_client_reuse(self, api_client):
        """Verify API client can be reused for multiple sequential requests."""
        service = SearchService(client=api_client)

        r1 = service.search_products("lipstick")
        r2 = service.search_products("mascara")
        r3 = service.search_products("kajal")

        for r in [r1, r2, r3]:
            assert isinstance(r, ApiResponse)
            assert r.response_time_ms > 0

    def test_search_suggestions_schema(self, api_client):
        """Validate search suggestions response against JSON schema."""
        service = SearchService(client=api_client)
        response = service.search_products("lipstick")

        if response.status_code == 403:
            pytest.skip("WAF blocked request (403)")

        if response.body is None:
            pytest.skip("No response body to validate")

        schema = load_schema("search_response")
        valid, msg = SchemaValidator.validate(response.body, schema)
        assert valid, f"Schema validation failed: {msg}"

    def test_search_suggestions_returns_data(self, api_client):
        """Verify search suggestions endpoint returns actual data."""
        service = SearchService(client=api_client)
        response = service.search_products("lipstick")

        if response.status_code == 403:
            pytest.skip("WAF blocked request (403)")

        assert response.is_success, (
            f"Search suggestions failed: {response.error_message}"
        )
        assert response.body is not None, "Response body is empty"

    def test_trending_searches(self, api_client):
        """Verify trending searches endpoint returns a response."""
        service = SearchService(client=api_client)
        response = service.get_trending_searches()

        assert isinstance(response, ApiResponse)
        assert response.status_code > 0, "No status code received"
        assert response.response_time_ms > 0, "Timing not captured"

    @pytest.mark.parametrize(
        "term",
        ["lipstick", "vitamin c serum", "maybelline foundation"],
    )
    @pytest.mark.data_driven
    def test_search_parametrized(self, api_client, term):
        """Verify search suggestions work across multiple terms."""
        service = SearchService(client=api_client)
        response = service.search_products(term)

        assert isinstance(response, ApiResponse)
        assert response.status_code > 0, (
            f"No status for '{term}': {response.error_message}"
        )
        assert response.response_time_ms > 0
