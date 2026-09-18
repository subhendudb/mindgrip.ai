#!/usr/bin/env python3
"""Extract page-specific HTML fragments from docs/source into public/fragments."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "docs" / "source"
OUT = ROOT / "public" / "fragments"

PAGES = (
    "mindgrip",
    "project_page",
    "lelab",
    "cli_menu",
    "roadmap",
    "optional_tooling",
    "so101_kinematics",
    "policy_cheatsheet",
)

STYLE_RE = re.compile(r"<style\b[^>]*>.*?</style>", re.IGNORECASE | re.DOTALL)
MAIN_RE = re.compile(
    r"<main\b([^>]*)>(.*?)</main>",
    re.IGNORECASE | re.DOTALL,
)
# Scripts that appear after </main> (body scripts for interactivity)
AFTER_MAIN_SCRIPTS_RE = re.compile(
    r"</main>(.*)</body>",
    re.IGNORECASE | re.DOTALL,
)
SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
CLASS_RE = re.compile(r'class\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)


def main_extra_classes(main_attrs: str) -> str:
    """Keep page-specific classes from <main>, drop shared 'content'."""
    m = CLASS_RE.search(main_attrs)
    if not m:
        return ""
    classes = [c for c in m.group(1).split() if c != "content"]
    return " ".join(classes)


def extract(stem: str) -> str:
    src = SOURCE / f"{stem}.html"
    if not src.exists():
        raise FileNotFoundError(src)
    html = src.read_text(encoding="utf-8")

    styles = STYLE_RE.findall(html)
    main_m = MAIN_RE.search(html)
    if not main_m:
        raise ValueError(f"{src.name}: no <main> found")
    extra = main_extra_classes(main_m.group(1))
    main_inner = main_m.group(2).strip()
    if extra:
        main_inner = f'<div class="{extra}">\n{main_inner}\n</div>'

    scripts: list[str] = []
    after = AFTER_MAIN_SCRIPTS_RE.search(html)
    if after:
        tail = after.group(1)
        scripts = SCRIPT_RE.findall(tail)

    parts = [*styles, main_inner, *scripts]
    return "\n\n".join(parts).strip() + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for stem in PAGES:
        out = OUT / f"{stem}.html"
        content = extract(stem)
        out.write_text(content, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({len(content):,} bytes)")


if __name__ == "__main__":
    main()
