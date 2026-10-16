# Сводка по городу

CLI-утилита, которая получает погоду и курс валюты к рублю из внешних API,
приводит ответы к единому виду, применяет простые правила и печатает результат.

## Установка

```bash
pip install -r requirements.txt
```

## Переменные окружения

- `YANDEX_WEATHER_API_KEY` — обязательный ключ Yandex Weather API. Погода
  запрашивается только у Yandex Weather. Координаты города определяются через
  Open-Meteo Geocoding (отдельный ключ не нужен).

## Запуск

```bash
python main.py --city Moscow
python main.py --city Moscow --currency EUR
python main.py --city Moscow --json
```

С ключом Yandex Weather:

```bash
YANDEX_WEATHER_API_KEY=your_key python main.py --city Moscow
```

Или укажите ключ непосредственно в аргументе `--weather-api-key`.

## Коды выхода

- 0 — успех
- 2 — ошибка аргументов
- 3 — город или код валюты не найден
- 4 — внешний сервис недоступен после повторов

## Структура

```
clients/        # HTTP-клиенты внешних API
processing/     # предобработка и сборка сводки
tests/          # тесты
```