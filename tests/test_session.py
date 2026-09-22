import json
import tempfile
import unittest
from pathlib import Path
from publisher.session import parse_cookies, heartbeat_status
from publisher.content import Blocked
from publisher.health import healthy


class SessionTests(unittest.TestCase):
    def test_markdown_escaped_names_and_encoded_values(self):
        result = parse_cookies(r'sessionid=test; sid\_tt=value%2B%3D; s\_v\_web\_id=verify\_test')
        self.assertEqual(result[1]['name'], 'sid_tt')
        self.assertEqual(result[1]['value'], 'value%2B%3D')
        self.assertEqual(result[2]['value'], 'verify_test')
        self.assertTrue(all(c['url'] == 'https://fanqienovel.com/' for c in result))

    def test_bad_cookie_headers_rejected(self):
        for raw in ('uid=x', 'sessionid=x; sessionid=y', 'sessionid=x\r\nInjected: y'):
            with self.assertRaises(Blocked):
                parse_cookies(raw)

    def test_heartbeat_retains_last_success_on_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            heartbeat_status(path, True)
            initial = json.loads((path / 'heartbeat.json').read_text())
            heartbeat_status(path, False)
            failed = json.loads((path / 'heartbeat.json').read_text())
            self.assertFalse(failed['ok'])
            self.assertEqual(failed['last_success_at'], initial['last_success_at'])
            self.assertEqual(failed['consecutive_failures'], 1)

    def test_health_requires_recent_success(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            self.assertFalse(healthy(path, 1000, 300))
            (path / 'heartbeat.json').write_text(json.dumps({'ok': True, 'checked_at': 1000}))
            self.assertTrue(healthy(path, 1001, 300))
            self.assertFalse(healthy(path, 1800, 300))
            (path / 'heartbeat.json').write_text(json.dumps({'ok': False, 'checked_at': 1000}))
            self.assertFalse(healthy(path, 1001, 300))
