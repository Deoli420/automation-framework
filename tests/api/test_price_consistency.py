"""
API Tests — Framework validation and schema validator tests.

Tests the SchemaValidator, ApiClient resilience, and multi-request
consistency. These are unit-level tests of the framework itself.
"""

import pytest

from services.api_client import ApiResponse
from services.search_service import SearchService
from services.schema_validator import SchemaValidator


@pytest.mark.api
@pytest.mark.pricing
class TestFrameworkValidation:
    """Framework-level validation tests."""

    def test_multiple_requests_return_timing(self, api_client):
        """Verify response timing is captured across multiple calls."""
        service = SearchService(client=api_client)

        terms = ["lipstick", "sunscreen", "shampoo"]
        for term in terms:
            response = service.search_products(term)
            assert response.response_time_ms > 0, (
                f"Response time not measured for '{term}'"
            )
            assert response.response_time_ms < 15000, (
                f"Response for '{term}' took {response.response_time_ms}ms"
            )

    def test_api_response_has_body_or_status(self, api_client):
        """Verify every response has a status code or error message."""
        service = SearchService(client=api_client)
        response = service.search_products("serum")

        has_status = response.status_code > 0
        has_error = response.error_message is not None

        assert has_status or has_error, (
            f"Response has neither status code nor error: {response}"
        )

    def test_schema_validator_accepts_valid_data(self):
        """Verify SchemaValidator accepts data matching schema."""
        schema = {
            "type": "object",
            "required": ["name", "price"],
            "properties": {
                "name": {"type": "string"},
                "price": {"type": "number"},
            },
        }

        valid, msg = SchemaValidator.validate(
            {"name": "Lipstick", "price": 299}, schema
        )
        assert valid, f"Valid data rejected: {msg}"

    def test_schema_validator_rejects_invalid_data(self):
        """Verify SchemaValidator rejects data missing required fields."""
        schema = {
            "type": "object",
            "required": ["name", "price"],
            "properties": {
                "name": {"type": "string"},
                "price": {"type": "number"},
            },
        }

        valid, msg = SchemaValidator.validate({"name": "Lipstick"}, schema)
        assert not valid, "Invalid data accepted"
        assert "price" in msg.lower(), f"Error should mention 'price': {msg}"

    def test_schema_validator_field_exists(self):
        """Verify field existence checker handles nested paths."""
        data = {
            "response": {
                "products": [
                    {"id": 1, "title": "Lipstick", "price": 299}
                ]
            }
        }

        valid, _ = SchemaValidator.validate_field_exists(
            data, "response.products.0.price"
        )
        assert valid, "Should find nested price field"

        valid, msg = SchemaValidator.validate_field_exists(
            data, "response.missing.field"
        )
        assert not valid, "Should not find missing field"

    def test_schema_validator_price_field(self):
        """Verify price field validator checks for positive numbers."""
        data = {"product": {"price": 499.0}}

        valid, price = SchemaValidator.validate_price_field(data, "product.price")
        assert valid
        assert price == 499.0

        data_zero = {"product": {"price": 0}}
        valid, _ = SchemaValidator.validate_price_field(data_zero, "product.price")
        assert not valid, "Zero price should be invalid"
