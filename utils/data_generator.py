"""
Test data generation and loading.

Provides static test data from fixtures and dynamic generators
for search terms, product categories, etc.
"""

import json
import logging
import os
import random
from typing import List

logger = logging.getLogger(__name__)

_FIXTURES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fixtures")

# Fallback search terms if fixtures file is missing.
# Multi-word terms to avoid single-word redirects to category pages.
_DEFAULT_SEARCH_TERMS = [
    "maybelline foundation",
    "vitamin c serum for oily skin",
    "l'oreal hair color",
    "neutrogena sunscreen spf 50",
    "lakme eyeshadow palette",
    "nykaa matte lipstick",
    "cetaphil gentle cleanser",
    "garnier micellar water",
    "dove body wash moisturizing",
    "himalaya face wash neem",
]

_CATEGORIES = [
    "Makeup",
    "Skin",
    "Hair",
    "Bath & Body",
    "Fragrance",
]

_BRANDS = [
    "Maybelline",
    "Lakme",
    "L'Oreal",
    "Nykaa Cosmetics",
    "Neutrogena",
]


def load_search_terms() -> List[str]:
    """Load search terms from fixtures or use defaults."""
    filepath = os.path.join(_FIXTURES_DIR, "search_terms.json")
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            return data.get("terms", _DEFAULT_SEARCH_TERMS)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.debug("Using default search terms (fixtures file not found)")
        return _DEFAULT_SEARCH_TERMS


def get_random_search_term() -> str:
    """Return a random search term for test variety."""
    terms = load_search_terms()
    return random.choice(terms)


def get_random_category() -> str:
    """Return a random product category."""
    return random.choice(_CATEGORIES)


def get_random_brand() -> str:
    """Return a random brand name."""
    return random.choice(_BRANDS)


def load_schema(schema_name: str) -> dict:
    """
    Load a JSON schema from fixtures/expected_schemas/.

    Args:
        schema_name: Filename without extension (e.g., "search_response")

    Returns:
        Parsed JSON schema dict
    """
    filepath = os.path.join(
        _FIXTURES_DIR, "expected_schemas", f"{schema_name}.json"
    )
    with open(filepath, "r") as f:
        return json.load(f)
