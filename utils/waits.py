"""
Custom expected conditions for Selenium waits.

Extends the standard EC library with domain-specific conditions
for the Nykaa test suite.

Usage:
    from utils.waits import page_has_loaded, window_count_is
    WebDriverWait(driver, 10).until(page_has_loaded())
    WebDriverWait(driver, 10).until(window_count_is(2))
"""

import re

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC


class element_has_non_empty_text:
    """Wait until element's text is not empty."""

    def __init__(self, locator: tuple[str, str]):
        self.locator = locator

    def __call__(self, driver: WebDriver):
        element = driver.find_element(*self.locator)
        if element.text.strip():
            return element
        return False


class page_has_loaded:
    """Wait until document.readyState is 'complete'."""

    def __call__(self, driver: WebDriver):
        return driver.execute_script("return document.readyState") == "complete"


class element_count_is_at_least:
    """Wait until at least N elements match the locator."""

    def __init__(self, locator: tuple[str, str], count: int):
        self.locator = locator
        self.count = count

    def __call__(self, driver: WebDriver):
        elements = driver.find_elements(*self.locator)
        if len(elements) >= self.count:
            return elements
        return False


class url_matches_pattern:
    """Wait until URL matches a regex pattern."""

    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)

    def __call__(self, driver: WebDriver):
        return bool(self.pattern.search(driver.current_url))


# ── New conditions (wired into tests to replace time.sleep) ───────


class window_count_is:
    """Wait until browser has exactly N windows/tabs open.

    Replaces ``time.sleep(2)`` after clicking product links that
    open in a new tab.
    """

    def __init__(self, count: int):
        self.count = count

    def __call__(self, driver: WebDriver):
        return len(driver.window_handles) == self.count


class window_count_greater_than:
    """Wait until browser has more than N windows/tabs open."""

    def __init__(self, count: int):
        self.count = count

    def __call__(self, driver: WebDriver):
        return len(driver.window_handles) > self.count


class url_changed:
    """Wait until the URL changes from the original value.

    Replaces ``time.sleep(2)`` after navigation actions like
    search submission or page transitions.
    """

    def __init__(self, original_url: str):
        self.original_url = original_url

    def __call__(self, driver: WebDriver):
        return driver.current_url != self.original_url


class element_count_changed:
    """Wait until element count differs from initial value.

    Replaces ``time.sleep(2)`` after filter application where the
    product count should change.
    """

    def __init__(self, locator: tuple[str, str], initial_count: int):
        self.locator = locator
        self.initial_count = initial_count

    def __call__(self, driver: WebDriver):
        current = len(driver.find_elements(*self.locator))
        return current != self.initial_count
