"""Build city summary from external clients."""

import logging
import uuid
from typing import Any

try:
    from ..clients.rates import get_rate
    from ..clients.weather import get_weather
except ImportError:
    from clients.rates import get_rate
    from clients.weather import get_weather
from .preprocessing import preprocess_rate, preprocess_weather

logger = logging.getLogger(__name__)


def build_city_summary(
    city: str,
    currency: str = "USD",
    timeout: int = 10,
    weather_api_key: str | None = None,
) -> dict[str, Any]:
    run_id = str(uuid.uuid4())
    logger.info("run_id=%s building summary city=%s currency=%s", run_id, city, currency)

    weather_raw = get_weather(city, timeout=timeout, api_key=weather_api_key)
    weather = preprocess_weather(
        {"temp_c": weather_raw.get("temp_c"), "description": weather_raw.get("description")}
    )

    rate_value = get_rate(currency, timeout=timeout)
    rates = preprocess_rate(
        {"currency": (currency or "").upper().strip(), "rate_to_rub": rate_value}
    )

    summary = {
        "city": city,
        "weather": weather,
        "rates": rates,
    }
    logger.info("run_id=%s summary built", run_id)
    return summary