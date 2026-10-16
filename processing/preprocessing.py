"""Data preprocessing rules for city summary."""

from typing import Any

TEMP_THRESHOLD = 0.0
RATE_THRESHOLD = 100.0


def warm_clothes_needed(temp_c: Any) -> bool:
    try:
        t = float(temp_c)
    except (TypeError, ValueError):
        return False
    return t < TEMP_THRESHOLD


def is_expensive_rate(rate: Any) -> bool:
    try:
        r = float(rate)
    except (TypeError, ValueError):
        return False
    return r > RATE_THRESHOLD


def normalize_description(description: Any) -> str:
    if description is None:
        return "unknown"
    text = str(description).strip()
    if not text:
        return "unknown"
    return text


def preprocess_weather(weather: dict[str, Any]) -> dict[str, Any]:
    """Apply weather rules and return a new dict."""
    result = dict(weather or {})
    result["temp_c"] = result.get("temp_c")
    try:
        result["temp_c"] = float(result["temp_c"])
    except (TypeError, ValueError):
        pass
    result["description"] = normalize_description(result.get("description"))
    result["warm_clothes"] = warm_clothes_needed(result.get("temp_c"))
    return result


def preprocess_rate(rates: dict[str, Any]) -> dict[str, Any]:
    """Apply rate rules and return a new dict."""
    result = dict(rates or {})
    if "rate_to_rub" in result:
        try:
            result["rate_to_rub"] = float(result["rate_to_rub"])
        except (TypeError, ValueError):
            pass
    result["expensive"] = is_expensive_rate(result.get("rate_to_rub"))
    return result


def preprocess_summary(summary: dict[str, Any]) -> dict[str, Any]:
    result = dict(summary or {})
    if isinstance(result.get("weather"), dict):
        result["weather"] = preprocess_weather(result["weather"])
    if isinstance(result.get("rates"), dict):
        result["rates"] = preprocess_rate(result["rates"])
    return result


# aliases
apply_weather_rules = preprocess_weather
apply_rate_rules = preprocess_rate
add_weather_flags = preprocess_weather
add_rate_flags = preprocess_rate
preprocess = preprocess_summary
apply_rules = preprocess_summary
transform = preprocess_summary
process = preprocess_summary