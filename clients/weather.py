"""Weather client using Yandex Weather, with Open-Meteo city geocoding."""

import os
from typing import Any

from .http import ExternalServiceError, NotFoundError, get_json

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
YANDEX_WEATHER_URL = "https://api.weather.yandex.ru/v2/forecast"

YANDEX_CONDITIONS = {
    "clear": "clear sky",
    "partly-cloudy": "partly cloudy",
    "cloudy": "cloudy",
    "overcast": "overcast",
    "drizzle": "drizzle",
    "light-rain": "light rain",
    "rain": "rain",
    "moderate-rain": "moderate rain",
    "heavy-rain": "heavy rain",
    "continuous-heavy-rain": "continuous heavy rain",
    "showers": "showers",
    "wet-snow": "wet snow",
    "light-snow": "light snow",
    "snow": "snow",
    "snow-showers": "snow showers",
    "hail": "hail",
    "thunderstorm": "thunderstorm",
    "thunderstorm-with-rain": "thunderstorm with rain",
    "thunderstorm-with-hail": "thunderstorm with hail",
}


def _geocode_city(city: str, timeout: int) -> tuple[float, float]:
    if not city or not city.strip():
        raise ValueError("city is required")
    data = get_json(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=timeout,
    )
    if not isinstance(data, dict):
        raise ExternalServiceError("Unexpected geocoding response")
    results = data.get("results")
    if not results:
        raise NotFoundError(f"City not found: {city}")
    result = results[0]
    if not isinstance(result, dict):
        raise ExternalServiceError("Invalid geocoding entry")
    lat, lon = result.get("latitude"), result.get("longitude")
    if lat is None or lon is None:
        raise ExternalServiceError("Geocoding response missing coordinates")
    return float(lat), float(lon)


def get_weather_yandex(
    city: str, api_key: str, timeout: int = 10
) -> dict[str, Any]:
    """Get current conditions from Yandex Weather API."""
    if not api_key:
        raise ValueError("Yandex Weather API key is required")
    lat, lon = _geocode_city(city, timeout)
    data = get_json(
        YANDEX_WEATHER_URL,
        params={"lat": lat, "lon": lon, "lang": "en_US"},
        headers={"X-Yandex-Weather-Key": api_key},
        timeout=timeout,
    )
    if not isinstance(data, dict):
        raise ExternalServiceError("Unexpected Yandex Weather response")
    fact = data.get("fact")
    if not isinstance(fact, dict):
        raise ExternalServiceError("Yandex Weather missing fact data")
    temp = fact.get("temp")
    if temp is None:
        raise ExternalServiceError("Yandex Weather missing temperature")
    condition = fact.get("condition", "")
    description = YANDEX_CONDITIONS.get(condition, condition or "unknown")
    return {"temp_c": float(temp), "description": str(description).strip() or "unknown"}


def get_weather(
    city: str,
    timeout: int = 10,
    api_key: str | None = None,
    allow_fallback: bool = True,
) -> dict[str, Any]:
    """Get weather from Yandex; key may be supplied through the environment."""
    del allow_fallback  # No forecast fallback provider is configured.
    key = api_key or os.getenv("YANDEX_WEATHER_API_KEY")
    return get_weather_yandex(city, key or "", timeout=timeout)
