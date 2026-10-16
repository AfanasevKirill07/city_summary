import unittest

from processing.preprocessing import (
    is_expensive_rate,
    normalize_description,
    preprocess_rate,
    preprocess_weather,
    warm_clothes_needed,
)


class TestPreprocessing(unittest.TestCase):
    def test_warm_clothes_below_zero(self):
        self.assertTrue(warm_clothes_needed(-3.2))
        self.assertFalse(warm_clothes_needed(5.0))

    def test_expensive_rate(self):
        self.assertTrue(is_expensive_rate(101.0))
        self.assertFalse(is_expensive_rate(92.15))

    def test_normalize_description_empty(self):
        self.assertEqual(normalize_description(""), "unknown")
        self.assertEqual(normalize_description(None), "unknown")
        self.assertEqual(normalize_description("clear sky"), "clear sky")

    def test_preprocess_weather(self):
        w = preprocess_weather({"temp_c": -3.2, "description": "clear sky"})
        self.assertEqual(w["warm_clothes"], True)
        self.assertEqual(w["description"], "clear sky")

    def test_preprocess_rate(self):
        r = preprocess_rate({"currency": "USD", "rate_to_rub": 92.15})
        self.assertEqual(r["expensive"], False)
        r2 = preprocess_rate({"currency": "USD", "rate_to_rub": 105.0})
        self.assertEqual(r2["expensive"], True)


if __name__ == "__main__":
    unittest.main()