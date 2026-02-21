"""
Root conftest — shared fixtures for the entire test suite.

Provides:
  - driver: Function-scoped WebDriver (fresh browser per test)
  - api_client: Session-scoped API client (shared HTTP session)
  - Automatic screenshot capture on test failure
"""

import logging

import pytest

from core.config import settings
from core.driver_factory import DriverFactory
from core.logger import setup_logging
from services.api_client import ApiClient
from utils.screenshot import capture_screenshot

logger = logging.getLogger(__name__)


# ── Logging setup (once per session) ──────────────────────────────────


def pytest_configure(config):
    """Called after command-line options are parsed."""
    setup_logging()
    logger.info(
        "Test session starting | env=%s | browser=%s | headless=%s",
        settings.ENVIRONMENT,
        settings.BROWSER,
        settings.HEADLESS,
    )


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def api_client():
    """Session-scoped API client with connection pooling."""
    client = ApiClient()
    yield client
    client.close()


@pytest.fixture(scope="function")
def driver():
    """
    Function-scoped WebDriver.

    Each test gets a clean browser session for full isolation.
    Driver is quit after each test regardless of outcome.
    """
    _driver = DriverFactory.create_driver()
    logger.info("WebDriver created: %s", settings.BROWSER)
    yield _driver
    _driver.quit()
    logger.info("WebDriver quit")


# ── Screenshot on failure ─────────────────────────────────────────────


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store test result on the item node for the screenshot fixture."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="function", autouse=True)
def _capture_screenshot_on_failure(request):
    """
    Autouse fixture — captures screenshot when a UI test fails.

    Only activates for tests that use the 'driver' fixture.
    """
    yield

    # Only capture if test failed during call phase
    rep = getattr(request.node, "rep_call", None)
    if rep and rep.failed and settings.SCREENSHOT_ON_FAILURE:
        # Check if this test uses a driver
        driver = request.node.funcargs.get("driver")
        if driver:
            test_name = request.node.name.replace("[", "_").replace("]", "")
            capture_screenshot(driver, f"FAIL_{test_name}")
