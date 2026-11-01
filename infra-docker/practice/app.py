"""Single-process learning server, not a production HTTP server."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import os


def read_count(directory: Path) -> int:
    path = directory / "count.txt"
    return int(path.read_text(encoding="utf-8")) if path.exists() else 0


def increment(directory: Path) -> int:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "count.txt"
    count = read_count(directory) + 1
    path.write_text(str(count), encoding="utf-8")
    return count


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.respond(change=False)

    def do_POST(self):
        self.respond(change=True)

    def respond(self, change: bool):
        if self.path != "/":
            self.send_error(404)
            return
        directory = Path(os.environ.get("DATA_DIR", "data"))
        count = increment(directory) if change else read_count(directory)
        body = f"count={count}\n".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
