import unittest
from unittest.mock import patch

from backend.alerts import send_webhook


class AlertTests(unittest.TestCase):
    def test_empty_url_does_not_send(self):
        self.assertFalse(send_webhook(None, {"event": "entered"}))

    @patch("backend.alerts.urlopen")
    def test_webhook_posts_json(self, urlopen):
        self.assertTrue(send_webhook("https://example.test/hook", {"event": "exited"}))
        urlopen.assert_called_once()


if __name__ == "__main__":
    unittest.main()
