#!/usr/bin/env python3
"""
Roadmap DA — Backend Server
Serves the HTML widget + provides file-based progress persistence.
Run: python server.py
Open: http://localhost:7777
"""
import json
import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

PORT = 7777
DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(DIR, 'roadmap-da-widget.html')
PROGRESS_FILE = os.path.join(DIR, 'progress.json')


class DAHandler(SimpleHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        if path == '/api/progress':
            self._handle_get_progress()
        elif path == '/' or path == '/index.html':
            self._serve_html()
        else:
            # Serve static files from the directory
            super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path

        if path == '/api/progress':
            self._handle_save_progress()
        else:
            self.send_error(404)

    def _serve_html(self):
        try:
            with open(HTML_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self._cors()
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, 'HTML file not found')

    def _handle_get_progress(self):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        except FileNotFoundError:
            # No progress file yet — return empty state
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({"phases": {}}).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))

    def _handle_save_progress(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "saved"}).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))


if __name__ == '__main__':
    os.chdir(DIR)  # Serve files from this directory
    server = ThreadingHTTPServer(('localhost', PORT), DAHandler)
    server.daemon_threads = True
    print(f'Roadmap DA server running at http://localhost:{PORT}')
    print(f'Directory: {DIR}')
    print(f'Progress file: {PROGRESS_FILE}')
    print('Press Ctrl+C to stop')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped.')
        server.server_close()
