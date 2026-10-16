"""Shared HTTP helpers: GET with timeout and retry."""

import logging
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)

RETRYABLE_STATUS = {500, 502, 503, 504}
MAX_RETRY_AFTER = 5.0


class ExternalServiceError(Exception):
    """Base class for external service errors."""


class NotFoundError(ExternalServiceError):
    """Requested resource (city/currency) was not found."""


class ExternalServiceUnavailable(ExternalServiceError):
    """External service unavailable after retries."""


def get_json(
    url: str,
    params: dict[str, Any] | None = None,
    timeout: int = 10,
    retries: int = 2,
    headers: dict[str, str] | None = None,
) -> Any:
    """Perform a GET request and return parsed JSON.

    Retries at least ``retries`` times (default 2) on Timeout,
    ConnectionError, temporary 5xx (500/502/503/504) and 429 (respecting
    a numeric Retry-After header).
    """
    if timeout is None or timeout <= 0 or timeout > 10:
        timeout = 10

    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=timeout, headers=headers)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
            last_exc = exc
            if attempt < retries:
                sleep = 0.5 * (2 ** attempt)
                logger.warning(
                    "request to %s failed (%s); retry %d/%d in %.1fs",
                    url, type(exc).__name__, attempt + 1, retries, sleep,
                )
                time.sleep(sleep)
                continue
            raise ExternalServiceUnavailable(
                f"Service unavailable: {exc}"
            ) from exc

        # 429 Too Many Requests
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            delay: float | None = None
            if retry_after is not None:
                try:
                    delay = float(retry_after)
                except (TypeError, ValueError):
                    delay = None
            if delay is not None:
                delay = min(delay, MAX_RETRY_AFTER)
            if attempt < retries:
                sleep = delay if delay is not None else 0.5 * (2 ** attempt)
                logger.warning("429 from %s; retry in %.1fs", url, sleep)
                time.sleep(sleep)
                continue
            raise ExternalServiceUnavailable("Rate limited (429)")

        # temporary 5xx
        if resp.status_code in RETRYABLE_STATUS:
            if attempt < retries:
                sleep = 0.5 * (2 ** attempt)
                logger.warning(
                    "HTTP %s from %s; retry %d/%d in %.1fs",
                    resp.status_code, url, attempt + 1, retries, sleep,
                )
                time.sleep(sleep)
                continue
            raise ExternalServiceUnavailable(f"HTTP {resp.status_code}")

        # not found / invalid currency
        if resp.status_code in (404, 422):
            raise NotFoundError(
                f"HTTP {resp.status_code}: {resp.text[:200]}"
            )

        if resp.status_code >= 400:
            raise ExternalServiceError(
                f"HTTP {resp.status_code}: {resp.text[:200]}"
            )

        # parse JSON
        try:
            data = resp.json()
        except ValueError as exc:
            raise ExternalServiceError(f"Invalid JSON: {exc}") from exc
        if not isinstance(data, (dict, list)):
            raise ExternalServiceError("Unexpected response format")
        return data

    if last_exc is not None:
        raise ExternalServiceUnavailable(str(last_exc)) from last_exc
    raise ExternalServiceUnavailable("Unknown error")