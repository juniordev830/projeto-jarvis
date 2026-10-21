import unittest
from unittest.mock import patch

from backend.source_clients import fetch_celestrak, fetch_opensky


class SourceClientTests(unittest.TestCase):
    @patch("backend.source_clients.fetch_json", return_value=[{"NAME": "ISS"}])
    def test_celestrak_filters_non_objects(self, fetch):
        self.assertEqual(fetch_celestrak("https://example.test"), [{"NAME": "ISS"}])
        fetch.assert_called_once()

    @patch("backend.source_clients.fetch_json", return_value={"states": [["icao"]]})
    def test_opensky_returns_payload(self, fetch):
        self.assertEqual(fetch_opensky("https://example.test")["states"], [["icao"]])
        fetch.assert_called_once()


if __name__ == "__main__":
    unittest.main()
