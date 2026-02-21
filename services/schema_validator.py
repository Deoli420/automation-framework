"""
JSON Schema validation for API responses.

Validates API response bodies against expected schemas stored
in fixtures/expected_schemas/. Designed as an entry point for
future contract testing.
"""

import logging
from typing import Any, Tuple

from jsonschema import ValidationError, validate

logger = logging.getLogger(__name__)


class SchemaValidator:
    """Validates API responses against JSON schemas."""

    @staticmethod
    def validate(response_body: Any, schema: dict) -> Tuple[bool, str]:
        """
        Validate a response body against a JSON schema.

        Args:
            response_body: Parsed JSON response (dict or list)
            schema: JSON Schema dict

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            validate(instance=response_body, schema=schema)
            logger.debug("Schema validation passed")
            return True, ""
        except ValidationError as e:
            logger.warning("Schema validation failed: %s", e.message)
            return False, e.message

    @staticmethod
    def validate_field_exists(
        response_body: dict, field_path: str
    ) -> Tuple[bool, str]:
        """
        Check if a nested field exists in the response.

        Args:
            response_body: Parsed JSON response
            field_path: Dot-separated path (e.g., "data.products.0.price")

        Returns:
            Tuple of (exists, error_message)
        """
        keys = field_path.split(".")
        current = response_body

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list):
                try:
                    index = int(key)
                    current = current[index]
                except (ValueError, IndexError):
                    return False, f"Field not found at: {field_path} (index: {key})"
            else:
                return False, f"Field not found at: {field_path} (key: {key})"

        return True, ""

    @staticmethod
    def validate_price_field(
        response_body: dict, price_path: str
    ) -> Tuple[bool, float]:
        """
        Validate that a price field exists and is a positive number.

        Args:
            response_body: Parsed JSON response
            price_path: Dot-separated path to price field

        Returns:
            Tuple of (is_valid, price_value)
        """
        exists, error = SchemaValidator.validate_field_exists(
            response_body, price_path
        )
        if not exists:
            return False, 0.0

        keys = price_path.split(".")
        current = response_body
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list):
                current = current[int(key)]

        try:
            price = float(current)
            if price > 0:
                return True, price
            return False, price
        except (ValueError, TypeError):
            return False, 0.0
