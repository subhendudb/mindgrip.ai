#!/usr/bin/env bash
# Apply optional SO-101 Lab UX patches onto a vanilla LeRobot source tree.
# Usage: ./scripts/apply_lerobot_patches.sh /path/to/lerobot
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEROBOT_ROOT="${1:-}"

if [[ -z "$LEROBOT_ROOT" || ! -d "$LEROBOT_ROOT/src/lerobot" ]]; then
  echo "Usage: $0 /path/to/lerobot"
  echo "Expected a checkout containing src/lerobot/."
  exit 1
fi

echo "Applying patches from $ROOT/patches → $LEROBOT_ROOT"
cd "$LEROBOT_ROOT"

shopt -s nullglob
for patch in "$ROOT"/patches/*.patch; do
  echo "→ $(basename "$patch")"
  # Prefer git apply (clean); fall back to patch -p1
  if git apply --check "$patch" 2>/dev/null; then
    git apply "$patch"
  else
    patch -p1 <"$patch"
  fi
done

echo "Done. Rebuild / reinstall lerobot if needed."
