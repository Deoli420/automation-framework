"""
Retry decorator for flaky Selenium interactions.

Handles transient failures like StaleElementReferenceException that occur
when the DOM updates between finding an element and interacting with it.
Applied to BasePage.click() and BasePage.find_element() for resilience.

Usage:
    @retry(max_attempts=3, delay=0.5, exceptions=(StaleElementReferenceException,))
    def click(self, locator):
        ...
"""

import functools
import logging
import time
from typing import Tuple, Type

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 0.5,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Decorator that retries a function on specified exceptions.

    Args:
        max_attempts: Maximum number of attempts (including first try).
        delay: Seconds to wait between retries.
        exceptions: Tuple of exception classes to catch and retry on.

    Raises:
        The last exception if all attempts are exhausted.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exception = exc
                    if attempt < max_attempts:
                        logger.warning(
                            "Retry %d/%d for %s: %s",
                            attempt,
                            max_attempts,
                            func.__name__,
                            exc,
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            "All %d attempts exhausted for %s: %s",
                            max_attempts,
                            func.__name__,
                            exc,
                        )
            raise last_exception  # type: ignore[misc]

        return wrapper

    return decorator
