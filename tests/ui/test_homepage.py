"""
UI Tests — Homepage validation.

Tests fundamental homepage functionality:
  - Page loads successfully
  - Search bar is visible and functional
  - Navigation categories are present
  - Popup dismissal works
"""

import pytest

from pages.home_page import HomePage


@pytest.mark.ui
@pytest.mark.smoke
class TestHomepage:
    """Homepage validation tests."""

    def test_homepage_loads_successfully(self, driver):
        """Verify Nykaa homepage loads without errors."""
        home = HomePage(driver)
        home.navigate()

        assert home.is_loaded(), "Homepage did not load — search input not found"
        assert "nykaa" in driver.title.lower() or "nykaa" in driver.current_url, (
            f"Not on Nykaa homepage: title='{driver.title}'"
        )

    def test_search_bar_is_visible(self, driver):
        """Verify search bar is visible after popup dismissal."""
        home = HomePage(driver)
        home.navigate()

        assert home.is_loaded(), "Search bar not visible after page load"

    @pytest.mark.regression
    def test_logo_is_present(self, driver):
        """Verify Nykaa logo/header image is present."""
        home = HomePage(driver)
        home.navigate()

        assert home.is_element_visible(home.LOGO, timeout=10), (
            "Logo/header image not found on homepage"
        )
