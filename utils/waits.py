"""
Custom expected conditions for Selenium waits.

Extends the standard EC library with domain-specific conditions.
"""

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
        import re
        self.pattern = re.compile(pattern)

    def __call__(self, driver: WebDriver):
        return bool(self.pattern.search(driver.current_url))
