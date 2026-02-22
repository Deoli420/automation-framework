"""
Browser abstraction using the Factory pattern.

Supports:
  - Local Chrome / Firefox with headless toggle
  - Remote Selenium Grid via SELENIUM_REMOTE_URL
  - Ethical user-agent identification

Usage:
    driver = DriverFactory.create_driver()
    # ... run tests ...
    driver.quit()

Scaling to Grid:
    Set AUTO_SELENIUM_REMOTE_URL=http://selenium-hub:4444/wd/hub
    Zero code changes needed.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver

from core.config import settings

# Realistic Chrome user-agent to bypass Akamai WAF.
# Nykaa's CDN returns 403 for bot-like user-agents.
# Matches the UA used in api_client.py for consistency.
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


class DriverFactory:
    """Creates WebDriver instances based on configuration."""

    @staticmethod
    def create_driver() -> WebDriver:
        """
        Create a WebDriver based on current settings.

        Returns local or remote driver depending on SELENIUM_REMOTE_URL.
        """
        if settings.SELENIUM_REMOTE_URL:
            return DriverFactory._create_remote_driver()

        browser = settings.BROWSER.lower()
        if browser == "chrome":
            return DriverFactory._create_chrome_driver()
        elif browser == "firefox":
            return DriverFactory._create_firefox_driver()
        else:
            raise ValueError(f"Unsupported browser: {settings.BROWSER}")

    @staticmethod
    def _chrome_options() -> ChromeOptions:
        """Build Chrome options shared between local and remote."""
        options = ChromeOptions()
        if settings.HEADLESS:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(
            f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}"
        )
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument(f"--user-agent={_USER_AGENT}")
        return options

    @staticmethod
    def _apply_timeouts(driver: WebDriver) -> WebDriver:
        """Apply common timeout settings to any driver."""
        driver.implicitly_wait(settings.IMPLICIT_WAIT)
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
        return driver

    @staticmethod
    def _create_chrome_driver() -> WebDriver:
        options = DriverFactory._chrome_options()
        driver = webdriver.Chrome(options=options)
        return DriverFactory._apply_timeouts(driver)

    @staticmethod
    def _create_firefox_driver() -> WebDriver:
        options = FirefoxOptions()
        if settings.HEADLESS:
            options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        return DriverFactory._apply_timeouts(driver)

    @staticmethod
    def _create_remote_driver() -> WebDriver:
        """Connect to Selenium Grid or standalone Chrome container."""
        options = DriverFactory._chrome_options()
        driver = webdriver.Remote(
            command_executor=settings.SELENIUM_REMOTE_URL,
            options=options,
        )
        return DriverFactory._apply_timeouts(driver)
