"""CLI entry point: city summary."""

import argparse
import json
import logging
import os
import sys
from typing import NoReturn

from clients.http import (
    ExternalServiceError,
    ExternalServiceUnavailable,
    NotFoundError,
)
from processing.service import build_city_summary


def _fail(message: str, code: int) -> NoReturn:
    print(message, file=sys.stderr)
    sys.exit(code)


def main() -> None:
    parser = argparse.ArgumentParser(description="Сводка по городу")
    parser.add_argument("--city", required=True, help="Название города")
    parser.add_argument(
        "--currency", default="USD", help="ISO-код валюты (по умолчанию USD)"
    )
    parser.add_argument("--json", action="store_true", help="Вывод в JSON")
    parser.add_argument(
        "--timeout", type=int, default=10, help="Таймаут запросов, сек (<=10)"
    )
    parser.add_argument(
        "--weather-api-key",
        default=None,
        help="Ключ Yandex Weather API (по умолчанию из YANDEX_WEATHER_API_KEY)",
    )
    args = parser.parse_args()

    city = (args.city or "").strip()
    if not city:
        _fail("Ошибка аргументов: город не указан", 2)

    currency = (args.currency or "").strip().upper()
    if len(currency) != 3 or not currency.isalpha():
        _fail("Ошибка аргументов: код валюты должен быть ISO-кодом из 3 букв", 2)

    timeout = args.timeout
    if timeout is None or timeout <= 0 or timeout > 10:
        timeout = 10

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )

    try:
        weather_key = "8c3db24e-f5d2-4f3f-a3d1-4bffe7917bd0"
        summary = build_city_summary(
            city, currency, timeout=timeout, weather_api_key=weather_key
        )
    except ValueError as exc:
        _fail(f"Ошибка аргументов: {exc}", 2)
    except NotFoundError as exc:
        _fail(f"Не найдено: {exc}", 3)
    except (ExternalServiceUnavailable, ExternalServiceError) as exc:
        _fail(f"Внешний сервис недоступен: {exc}", 4)
    except Exception as exc:  # noqa: BLE001  # pragma: no cover
        _fail(f"Неожиданная ошибка: {exc}", 4)

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        w = summary["weather"]
        r = summary["rates"]
        print(f"Город: {summary['city']}")
        print(f"Погода: {w['temp_c']}°C, {w['description']}")
        print(f"Тёплая одежда: {'да' if w.get('warm_clothes') else 'нет'}")
        print(f"{r['currency']}→RUB: {r['rate_to_rub']}")
        print(f"Дорогой курс: {'да' if r.get('expensive') else 'нет'}")
    sys.exit(0)


if __name__ == "__main__":
    main()