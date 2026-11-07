"""Exercise hosted verification over HTTP, including failures a 200-only probe misses."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Thread
import unittest


class HostedCheckTests(unittest.TestCase):
    def check_server(self, mode):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if mode == 'redirect' and self.path == '/preview/':
                    self.send_response(302)
                    self.send_header('Location', '/preview/redirected')
                    self.end_headers()
                    return
                bodies = {
                    '/preview/': b'<h1>Home</h1>',
                    '/preview/redirected': b'<h1>Home</h1>',
                    '/preview/404.html': b'<h1>Not found</h1>',
                    '/preview/book.epub': b'book bytes',
                }
                status = 200 if self.path in bodies or mode == 'soft404' else 404
                body = bodies.get(self.path, b'<h1>Not found</h1>')
                if mode == 'corrupt' and self.path.endswith('.epub'):
                    body = b'truncated'
                self.send_response(status)
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for name, body in [('index.html', b'<h1>Home</h1>'), ('404.html', b'<h1>Not found</h1>'), ('book.epub', b'book bytes')]:
                (output / name).write_bytes(body)
            server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                report = output / 'report.json'
                result = subprocess.run([
                    sys.executable, 'scripts/check_hosted.py', '--output-dir', directory,
                    '--base-url', f'http://127.0.0.1:{server.server_port}/preview/',
                    '--report', str(report),
                ], capture_output=True, text=True)
                data = json.loads(report.read_text())
            finally:
                server.shutdown()
                server.server_close()
                thread.join()
        return result.returncode, data

    def test_matching_artifact_and_custom_404_pass(self):
        code, report = self.check_server('correct')
        self.assertEqual(code, 0)
        self.assertEqual(report['failures'], 0)
        self.assertTrue(any(row['expected_status'] == 404 for row in report['results']))

    def test_soft_404_fails(self):
        code, report = self.check_server('soft404')
        self.assertEqual(code, 1)
        self.assertGreater(report['failures'], 0)

    def test_corrupt_download_fails(self):
        code, report = self.check_server('corrupt')
        self.assertEqual(code, 1)
        self.assertEqual(report['failures'], 1)

    def test_redirect_even_to_matching_content_fails(self):
        code, report = self.check_server('redirect')
        self.assertEqual(code, 1)
        self.assertEqual(report['failures'], 1)


if __name__ == '__main__':
    unittest.main()
