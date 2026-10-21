import unittest
from unittest.mock import patch

from backend.routing import bicycle_route


class RoutingTests(unittest.TestCase):
    @patch("backend.routing.fetch_json", return_value={"code": "Ok", "routes": []})
    def test_bicycle_route_uses_osrm(self, fetch):
        result = bicycle_route(-23.55, -46.63, -23.56, -46.64)
        self.assertEqual(result["code"], "Ok")
        self.assertIn("router.project-osrm.org", fetch.call_args.args[0])
        self.assertIn("bicycle", fetch.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
