#!/usr/bin/env python3
"""Simple HTTP server with no-cache headers for Cloudflare Tunnel."""
import http.server
import os

WEBSITE_DIR = os.path.expanduser("~/afk-andy/website")


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEBSITE_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", 8080), NoCacheHandler)
    print("Serving website on :8080 (no-cache mode)")
    server.serve_forever()
