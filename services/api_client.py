"""
HTTP client for API validation layer.

Features:
  - Response time measurement (perf_counter precision)
  - Configurable retries with exponential backoff
  - Ethical User-Agent identification
  - Structured ApiResponse dataclass
  - Graceful timeout handling (no crash)

Designed to scale toward contract testing.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ApiResponse:
    """Structured API response with timing and status."""

    status_code: int
    response_time_ms: float
    body: Any = None
    headers: dict = field(default_factory=dict)
    is_success: bool = True
    error_message: Optional[str] = None


class ApiClient:
    """
    Sync HTTP client for validating Nykaa public APIs.

    Usage:
        client = ApiClient()
        response = client.get("/path", params={"q": "lipstick"})
        assert response.is_success
        assert response.response_time_ms < 3000
    """

    def __init__(self, base_url: Optional[str] = None) -> None:
        self.base_url = base_url or settings.API_BASE_URL
        self.session = requests.Session()
        # Browser-like headers required to pass Akamai WAF.
        # Without these, Nykaa's CDN returns 403.
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.nykaa.com/",
                "Origin": "https://www.nykaa.com",
            }
        )

        retry_strategy = Retry(
            total=settings.API_MAX_RETRIES,
            backoff_factor=settings.API_RETRY_BACKOFF,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    # ── Internal request helper ─────────────────────────────────────

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json_body: Optional[dict] = None,
    ) -> ApiResponse:
        """
        Make an HTTP request with timing and structured response.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, HEAD)
            path: URL path (appended to base_url)
            params: Query parameters
            json_body: JSON body for POST/PUT

        Returns:
            ApiResponse with status, timing, and body
        """
        url = f"{self.base_url}{path}"
        logger.info("%s %s params=%s", method, url, params)
        start = time.perf_counter()

        try:
            resp = self.session.request(
                method,
                url,
                params=params,
                json=json_body,
                timeout=settings.API_TIMEOUT,
            )
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

            body = None
            content_type = resp.headers.get("content-type", "")
            if "json" in content_type:
                try:
                    body = resp.json()
                except ValueError:
                    body = None

            logger.info(
                "Response: %d in %.1fms (%d bytes)",
                resp.status_code,
                elapsed_ms,
                len(resp.content),
            )

            return ApiResponse(
                status_code=resp.status_code,
                response_time_ms=elapsed_ms,
                body=body,
                headers=dict(resp.headers),
                is_success=resp.ok,
            )

        except requests.Timeout:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.warning("Request timed out after %.1fms: %s", elapsed_ms, url)
            return ApiResponse(
                status_code=0,
                response_time_ms=elapsed_ms,
                is_success=False,
                error_message=f"Timeout after {settings.API_TIMEOUT}s",
            )

        except requests.RequestException as exc:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.error("Request failed: %s — %s", url, exc)
            return ApiResponse(
                status_code=0,
                response_time_ms=elapsed_ms,
                is_success=False,
                error_message=str(exc),
            )

    # ── Public HTTP methods ──────────────────────────────────────────

    def get(
        self, path: str, params: Optional[dict] = None
    ) -> ApiResponse:
        """Make a GET request with timing."""
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        params: Optional[dict] = None,
        json_body: Optional[dict] = None,
    ) -> ApiResponse:
        """Make a POST request with timing."""
        return self._request("POST", path, params=params, json_body=json_body)

    def put(
        self,
        path: str,
        params: Optional[dict] = None,
        json_body: Optional[dict] = None,
    ) -> ApiResponse:
        """Make a PUT request with timing."""
        return self._request("PUT", path, params=params, json_body=json_body)

    def delete(
        self, path: str, params: Optional[dict] = None
    ) -> ApiResponse:
        """Make a DELETE request with timing."""
        return self._request("DELETE", path, params=params)

    def head(
        self, path: str, params: Optional[dict] = None
    ) -> ApiResponse:
        """Make a HEAD request (lightweight endpoint check)."""
        return self._request("HEAD", path, params=params)

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()
