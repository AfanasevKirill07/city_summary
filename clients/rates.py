"""Currency rate client (Frankfurter)."""

import logging
import time

from .http import ExternalServiceError, get_json

logger = logging.getLogger(__name__)

RATE_URL = "https://api.frankfurter.dev/v2/rate/{currency}/RUB"
CACHE_TTL = 300  # 5 minutes
_cache: dict[str, tuple] = {}


def clear_cache() -> None:
    _cache.clear()


def get_rate(currency: str, timeout: int = 10, use_cache: bool = True) -> float:
    """Return exchange rate of ``currency`` to RUB."""
    currency = (currency or "").upper().strip()
    if not currency:
        raise ValueError("currency is required")

    if use_cache:
        cached = _cache.get(currency)
        if cached is not None:
            ts, value = cached
            if time.time() - ts < CACHE_TTL:
                return value

    url = RATE_URL.format(currency=currency)
    data = get_json(url, timeout=timeout)
    if not isinstance(data, dict):
        raise ExternalServiceError("Unexpected rate response")
    rate = data.get("rate")
    if rate is None:
        raise ExternalServiceError("Rate missing in response")
    try:
        value = float(rate)
    except (TypeError, ValueError) as exc:
        raise ExternalServiceError("Invalid rate value") from exc

    if use_cache:
        _cache[currency] = (time.time(), value)
    return value