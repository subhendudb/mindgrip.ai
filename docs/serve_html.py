#!/usr/bin/env python3
"""Serve docs/html as a local website with live reload.

Watches docs/source/ for changes, rebuilds HTML, and refreshes the browser.

Usage:
  uv run python docs/serve_html.py
  uv run python docs/serve_html.py --port 8080
  uv run python docs/serve_html.py --no-watch   # static serve only

Then open: http://127.0.0.1:8000/
"""

from __future__ import annotations

import argparse
import hashlib
import http.server
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS_HTML = ROOT / "html"
DOCS_SOURCE = ROOT / "source"
BUILD_SCRIPT = ROOT / "build_html.py"

# Shared rebuild generation — browser polls this to decide when to reload.
_reload_token = "0"
_reload_lock = threading.Lock()


def get_reload_token() -> str:
    with _reload_lock:
        return _reload_token


def bump_reload_token() -> str:
    global _reload_token
    with _reload_lock:
        _reload_token = hashlib.sha1(str(time.time()).encode()).hexdigest()[:12]
        return _reload_token


LIVERELOAD_JS = """
<script>
(function () {
  var token = null;
  var endpoint = "/__livereload";
  function poll() {
    fetch(endpoint, { cache: "no-store" })
      .then(function (r) { return r.text(); })
      .then(function (t) {
        if (token === null) { token = t; }
        else if (t && t !== token) { location.reload(); }
      })
      .catch(function () {})
      .finally(function () { setTimeout(poll, 800); });
  }
  poll();
})();
</script>
"""


def source_fingerprint() -> str:
    """Hash of source file mtimes — cheap change detection."""
    parts: list[str] = []
    if not DOCS_SOURCE.is_dir():
        return ""
    for path in sorted(DOCS_SOURCE.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".mdx", ".md", ".html", ".yml", ".yaml", ".css"}:
            try:
                st = path.stat()
                parts.append(f"{path.relative_to(DOCS_SOURCE)}:{st.st_mtime_ns}:{st.st_size}")
            except OSError:
                continue
    # Also watch the build script itself
    if BUILD_SCRIPT.is_file():
        st = BUILD_SCRIPT.stat()
        parts.append(f"build_html.py:{st.st_mtime_ns}")
    return hashlib.sha1("\n".join(parts).encode()).hexdigest()


def rebuild_custom_html(stem: str) -> bool:
    """Fast path: rebuild a single custom HTML page (e.g. project_page)."""
    src = DOCS_SOURCE / f"{stem}.html"
    if not src.is_file():
        return False
    try:
        # Import build helpers from the sibling module
        sys.path.insert(0, str(ROOT))
        import build_html  # noqa: WPS433

        import yaml

        toc = yaml.safe_load((DOCS_SOURCE / "_toctree.yml").read_text(encoding="utf-8"))
        toc_titles = {
            item["local"]: item["title"]
            for section in toc
            for item in section.get("sections", [])
        }
        html = build_html.render_custom_html(src, stem, toc_titles)
        DOCS_HTML.mkdir(parents=True, exist_ok=True)
        (DOCS_HTML / f"{stem}.html").write_text(html, encoding="utf-8")
        # Keep styles.css in sync if missing
        if not (DOCS_HTML / "styles.css").exists():
            (DOCS_HTML / "styles.css").write_text(build_html.CSS, encoding="utf-8")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"  ✗ fast rebuild failed for {stem}.html: {exc}", flush=True)
        return False


def rebuild_all() -> bool:
    print("  → Rebuilding all HTML docs…", flush=True)
    result = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)],
        cwd=str(ROOT.parent),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout, flush=True)
        print("  ✗ build failed", flush=True)
        return False
    # Print last line of success summary
    for line in (result.stdout or "").strip().splitlines()[-3:]:
        print(f"  {line}", flush=True)
    return True


def rebuild_for_changes(changed: set[Path]) -> None:
    """Incremental when only custom HTML changed; full rebuild otherwise."""
    only_custom_html = bool(changed) and all(
        p.suffix.lower() == ".html" and p.name != "_toctree.yml" for p in changed
    )
    ok = False
    if only_custom_html:
        stems = {p.stem for p in changed}
        print(f"  → Fast rebuild: {', '.join(sorted(stems))}", flush=True)
        ok = all(rebuild_custom_html(stem) for stem in stems)
        if not ok:
            ok = rebuild_all()
    else:
        ok = rebuild_all()

    if ok:
        token = bump_reload_token()
        print(f"  ✓ Live reload token → {token}", flush=True)


def watch_loop(poll_seconds: float = 0.6) -> None:
    print(f"Watching {DOCS_SOURCE} for changes (live reload on)…", flush=True)
    last = source_fingerprint()
    last_paths: dict[Path, tuple[int, int]] = {}

    def snapshot() -> dict[Path, tuple[int, int]]:
        out: dict[Path, tuple[int, int]] = {}
        if not DOCS_SOURCE.is_dir():
            return out
        for path in DOCS_SOURCE.rglob("*"):
            if path.is_file() and path.suffix.lower() in {
                ".mdx",
                ".md",
                ".html",
                ".yml",
                ".yaml",
                ".css",
            }:
                try:
                    st = path.stat()
                    out[path] = (st.st_mtime_ns, st.st_size)
                except OSError:
                    continue
        return out

    last_paths = snapshot()
    while True:
        time.sleep(poll_seconds)
        current = source_fingerprint()
        if current == last:
            continue
        now_paths = snapshot()
        changed = {
            p
            for p in set(now_paths) | set(last_paths)
            if now_paths.get(p) != last_paths.get(p)
        }
        # Debounce rapid saves
        time.sleep(0.25)
        current = source_fingerprint()
        now_paths = snapshot()
        changed = {
            p
            for p in set(now_paths) | set(last_paths)
            if now_paths.get(p) != last_paths.get(p)
        }
        rel = sorted(str(p.relative_to(DOCS_SOURCE)) for p in changed if p.is_relative_to(DOCS_SOURCE))
        print(f"\n↻ Change detected: {', '.join(rel) or 'source files'}", flush=True)
        rebuild_for_changes(changed)
        last = current
        last_paths = now_paths


class DocsHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that injects live-reload and tolerates client disconnects."""

    # Browser navigations / live-reload polls often abort mid-response.
    _CLIENT_GONE = (BrokenPipeError, ConnectionResetError, ConnectionAbortedError)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DOCS_HTML), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        # Quieter logs — skip livereload polling noise
        msg = fmt % args
        if "__livereload" in msg:
            return
        super().log_message(fmt, *args)

    def _safe_write(self, data: bytes) -> None:
        try:
            self.wfile.write(data)
        except self._CLIENT_GONE:
            # Client closed tab / navigated away — not a server failure.
            pass

    def do_GET(self) -> None:  # noqa: N802
        try:
            if self.path.split("?", 1)[0] == "/__livereload":
                body = get_reload_token().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self._safe_write(body)
                return
            super().do_GET()
        except self._CLIENT_GONE:
            pass

    def end_headers(self) -> None:
        # Always revalidate HTML/CSS so live reload shows fresh content
        path = self.path.split("?", 1)[0]
        if path.endswith((".html", ".css", "/")) or path == "":
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Pragma", "no-cache")
        try:
            super().end_headers()
        except self._CLIENT_GONE:
            pass

    def send_head(self):  # type: ignore[override]
        """Inject live-reload script into HTML responses."""
        path = self.translate_path(self.path)
        if path.endswith(".html") and Path(path).is_file():
            try:
                data = Path(path).read_bytes()
            except OSError:
                return super().send_head()
            text = data.decode("utf-8", errors="replace")
            if "</body>" in text.lower() and "__livereload" not in text:
                # Case-insensitive replace of closing body tag
                idx = text.lower().rfind("</body>")
                text = text[:idx] + LIVERELOAD_JS + text[idx:]
                data = text.encode("utf-8")
            try:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self._safe_write(data)
            except self._CLIENT_GONE:
                pass
            return None
        return super().send_head()

    def copyfile(self, source, outputfile):  # noqa: ANN001
        try:
            super().copyfile(source, outputfile)
        except self._CLIENT_GONE:
            pass


class ReusableTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, request, client_address) -> None:  # noqa: ANN001, ARG002
        exc = sys.exc_info()[1]
        if isinstance(exc, (BrokenPipeError, ConnectionResetError, ConnectionAbortedError)):
            # Benign: browser cancelled the request (reload / close tab).
            return
        super().handle_error(request, client_address)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve LeRobot HTML docs locally (with live reload).")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port (default: 8000)")
    parser.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open a browser automatically")
    parser.add_argument("--no-watch", action="store_true", help="Disable live reload / file watching")
    args = parser.parse_args()

    if not DOCS_HTML.is_dir() or not (DOCS_HTML / "index.html").exists():
        print("HTML docs not found — building once…", flush=True)
        if not rebuild_all():
            raise SystemExit(1)

    bump_reload_token()

    if not args.no_watch:
        watcher = threading.Thread(target=watch_loop, daemon=True)
        watcher.start()

    url = f"http://{args.host}:{args.port}/"
    print(f"Serving LeRobot HTML docs from: {DOCS_HTML}")
    print(f"Open in browser: {url}")
    if not args.no_watch:
        print("Live reload: ON — edit docs/source/* and the browser will refresh")
    print("Press Ctrl+C to stop.\n", flush=True)

    with ReusableTCPServer((args.host, args.port), DocsHandler) as httpd:
        if not args.no_browser:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
