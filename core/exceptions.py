"""
Categorized custom exceptions for the automation framework.

Each exception carries a `category` attribute for failure tagging
in reports and structured logs.
"""


class AutomationBaseError(Exception):
    """Base exception for all automation framework errors."""

    category: str = "UNKNOWN"


class ElementNotFoundError(AutomationBaseError):
    """Raised when a page element cannot be located within timeout."""

    category = "UI_ELEMENT"


class PageLoadError(AutomationBaseError):
    """Raised when a page fails to load within the configured timeout."""

    category = "PAGE_LOAD"


class ApiValidationError(AutomationBaseError):
    """Raised when an API response fails JSON schema validation."""

    category = "API_SCHEMA"


class PriceInconsistencyError(AutomationBaseError):
    """Raised when the UI-displayed price does not match the API price."""

    category = "PRICE_MISMATCH"


class CartOperationError(AutomationBaseError):
    """Raised when a cart add/remove/validate operation fails."""

    category = "CART"


class ApiTimeoutError(AutomationBaseError):
    """Raised when an API response exceeds the configured timeout."""

    category = "API_TIMEOUT"
