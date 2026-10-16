import unittest
from unittest.mock import MagicMock, patch

from clients.http import ExternalServiceUnavailable, NotFoundError, get_json
from clients.rates import clear_cache, get_rate
from clients.weather import get_weather


class TestHttpGetJson(unittest.TestCase):
    @patch("clients.http.requests.get")
    def test_success(self, mock_get):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {"ok": True}
        mock_get.return_value = resp
        self.assertEqual(get_json("http://example.com"), {"ok": True})

    @patch("clients.http.requests.get")
    @patch("clients.http.time.sleep", return_value=None)
    def test_retry_on_500(self, _sleep, mock_get):
        r1 = MagicMock(status_code=500, text="err")
        r2 = MagicMock(status_code=200)
        r2.json.return_value = {"ok": True}
        mock_get.side_effect = [r1, r1, r2]
        self.assertEqual(get_json("http://example.com", retries=2), {"ok": True})
        self.assertEqual(mock_get.call_count, 3)

    @patch("clients.http.requests.get")
    @patch("clients.http.time.sleep", return_value=None)
    def test_timeout_retries_then_fails(self, _sleep, mock_get):
        import requests as r

        mock_get.side_effect = r.exceptions.Timeout("t")
        with self.assertRaises(ExternalServiceUnavailable):
            get_json("http://example.com", retries=2)
        self.assertEqual(mock_get.call_count, 3)

    @patch("clients.http.requests.get")
    def test_404_raises_not_found(self, mock_get):
        resp = MagicMock(status_code=404, text="nf")
        mock_get.return_value = resp
        with self.assertRaises(NotFoundError):
            get_json("http://example.com")

    @patch("clients.http.requests.get")
    @patch("clients.http.time.sleep", return_value=None)
    def test_429_retry_after(self, _sleep, mock_get):
        r1 = MagicMock(status_code=429, headers={"Retry-After": "1"}, text="")
        r2 = MagicMock(status_code=200)
        r2.json.return_value = {"ok": True}
        mock_get.side_effect = [r1, r2]
        self.assertEqual(get_json("http://example.com", retries=2), {"ok": True})


class TestWeatherClient(unittest.TestCase):
    @patch("clients.weather.get_json")
    def test_get_weather_yandex(self, mock_get_json):
        mock_get_json.side_effect = [
            {"results": [{"latitude": 1.0, "longitude": 2.0}]},
            {"fact": {"temp": -3, "condition": "clear"}},
        ]
        res = get_weather("Moscow", api_key="test-key")
        self.assertEqual(res["temp_c"], -3.0)
        self.assertEqual(res["description"], "clear sky")
        self.assertEqual(mock_get_json.call_args.kwargs["headers"], {
            "X-Yandex-Weather-Key": "test-key"
        })

    @patch("clients.weather.get_json")
    def test_city_not_found(self, mock_get_json):
        mock_get_json.return_value = {}
        with self.assertRaises(NotFoundError):
            get_weather("NopeCityXYZ", api_key="test-key")


class TestRatesClient(unittest.TestCase):
    def setUp(self):
        clear_cache()

    @patch("clients.rates.get_json")
    def test_get_rate(self, mock_get_json):
        mock_get_json.return_value = {"rate": 92.15}
        self.assertEqual(get_rate("USD"), 92.15)

    @patch("clients.rates.get_json")
    def test_cache(self, mock_get_json):
        mock_get_json.return_value = {"rate": 92.15}
        self.assertEqual(get_rate("USD"), 92.15)
        self.assertEqual(get_rate("USD"), 92.15)
        self.assertEqual(mock_get_json.call_count, 1)

    @patch("clients.rates.get_json")
    def test_invalid_currency(self, mock_get_json):
        mock_get_json.side_effect = NotFoundError("422")
        with self.assertRaises(NotFoundError):
            get_rate("XYZ")


if __name__ == "__main__":
    unittest.main()
