"""Confere os exemplos com o cliente de demonstracao atraves de HTTP real."""
import subprocess
import sys
import threading
import unittest
from pathlib import Path

from werkzeug.serving import make_server

from app import create_app


class ExamplesTests(unittest.TestCase):
    def test_documented_examples_over_http(self):
        root = Path(__file__).resolve().parents[1]
        for protocol in ['rest', 'graphql']:
            with self.subTest(protocol=protocol):
                server = make_server('127.0.0.1', 0, create_app())
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    result = subprocess.run(
                        [sys.executable, str(root / 'scripts' / 'demo.py'), protocol,
                         '--url', f'http://127.0.0.1:{server.server_port}'],
                        capture_output=True, text=True, timeout=30,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(result.stdout.count('OK '), 12)
                finally:
                    server.shutdown()
                    thread.join(timeout=5)
                    server.server_close()


if __name__ == '__main__':
    unittest.main()
