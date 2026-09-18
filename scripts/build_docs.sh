#!/usr/bin/env bash
# Build MindGrip AI custom docs only (no upstream LeRobot MDX mirror).
# Usage: ./scripts/build_docs.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "error: '$1' is required" >&2
    exit 1
  }
}

need_cmd pandoc
need_cmd python3
python3 -c "import yaml" 2>/dev/null || {
  echo "error: Python package 'yaml' (PyYAML) is required — try: pip3 install --user pyyaml" >&2
  exit 1
}

echo "==> Building MindGrip AI docs (custom pages only)"
echo "    Official LeRobot docs: https://huggingface.co/docs/lerobot"
cd "$ROOT"
python3 docs/build_html.py
echo "==> Done. Prefer: cd docs-web && npm run dev → http://localhost:8000/"
echo "    Legacy static: docs/html/mindgrip.html"
