#!/usr/bin/env python3
"""Convert docs/source/*.mdx (and .md) into a browsable docs/html/ site."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
SOURCE = ROOT / "source"
OUT = ROOT / "html"
TOCTREE = SOURCE / "_toctree.yml"
IMAGES = REPO_ROOT / "images"

# Application brand for all custom / lab pages
APP_NAME = "MindGrip AI"
APP_TAGLINE = (
    "Emphasizes cognitive decision-making for complex object targeting and handling."
)
# Upstream LeRobot docs (not mirrored locally)
LEROBOT_DOCS_URL = "https://huggingface.co/docs/lerobot"

# Custom project pages (shown under MindGrip AI menu). Order = sidebar order.
CUSTOM_PAGES: dict[str, str] = {
    "mindgrip": "MindGrip AI Home",
    "project_page": "Pick & Place Sorting",
    "so101_kinematics": "Forward & Inverse Kinematics",
    "so101_mujoco": "MuJoCo Simulation",
    "so101_setup": "Setup (see project page)",
    "policy_cheatsheet": "Policy Cheatsheet",
    "directory_structure": "Directory Structure",
    "acronyms": "Acronyms Glossary",
    "code_of_conduct": "Code of Conduct",
    "ai_policy": "AI Usage Policy",
    "security": "Security Policy",
}

CSS = """\
:root, html[data-theme="light"] {
  color-scheme: light;
  --bg: #f7f7f5;
  --panel: #ffffff;
  --text: #1a1a1a;
  --muted: #5c5c5c;
  --border: #e2e2de;
  --accent: #ff9f1c;
  --mindgrip: #0b6bcb;
  --code-bg: #f0efeb;
  --sidebar-w: 300px;
  --nav-root-bg: #fafaf8;
  --tagline-bg: #eef5ff;
  --brand-grad: linear-gradient(135deg, #eef5ff 0%, #fff8ef 100%);
  --blockquote-bg: #fff8ef;
  --link: #0b6bcb;
  --lerobot-summary: #333333;
  --hover-btn: #e8e7e2;
  --surface-elevated: #ffffff;
  --callout-warn-bg: #fff8ef;
  --callout-info-bg: #f3f8ff;
  --callout-ok-bg: #f3faf5;
  --callout-fail-bg: #fff5f4;
  --chip-ok-bg: #f0faf2; --chip-ok-border: #b7dfc2; --chip-ok-text: #1f6b3a;
  --chip-fail-bg: #fff1f0; --chip-fail-border: #f0c2be; --chip-fail-text: #9b2c2c;
  --chip-warn-bg: #fff8ef; --chip-warn-border: #f0d4a8; --chip-warn-text: #8a5a10;
  --chip-info-bg: #f3f8ff; --chip-info-border: #b7d4f0; --chip-info-text: #0b6bcb;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --bg: #0f1115;
    --panel: #171a21;
    --text: #e8eaed;
    --muted: #9aa0a6;
    --border: #2c313a;
    --accent: #ffb347;
    --mindgrip: #6cb6ff;
    --code-bg: #1e232c;
    --nav-root-bg: #141820;
    --tagline-bg: #152033;
    --brand-grad: linear-gradient(135deg, #152033 0%, #2a2118 100%);
    --blockquote-bg: #2a2118;
    --link: #6cb6ff;
    --lerobot-summary: #c5c8ce;
    --hover-btn: #2a303a;
    --surface-elevated: #1c2129;
    --callout-warn-bg: #2a2118;
    --callout-info-bg: #152033;
    --callout-ok-bg: #14241a;
    --callout-fail-bg: #2a1616;
    --chip-ok-bg: #14241a; --chip-ok-border: #2d5a3c; --chip-ok-text: #7dcea0;
    --chip-fail-bg: #2a1616; --chip-fail-border: #6b3030; --chip-fail-text: #f0a0a0;
    --chip-warn-bg: #2a2118; --chip-warn-border: #6b5020; --chip-warn-text: #e0b060;
    --chip-info-bg: #152033; --chip-info-border: #2a5080; --chip-info-text: #6cb6ff;
  }
}
html[data-theme="dark"] {
  color-scheme: dark;
  --bg: #0f1115;
  --panel: #171a21;
  --text: #e8eaed;
  --muted: #9aa0a6;
  --border: #2c313a;
  --accent: #ffb347;
  --mindgrip: #6cb6ff;
  --code-bg: #1e232c;
  --nav-root-bg: #141820;
  --tagline-bg: #152033;
  --brand-grad: linear-gradient(135deg, #152033 0%, #2a2118 100%);
  --blockquote-bg: #2a2118;
  --link: #6cb6ff;
  --lerobot-summary: #c5c8ce;
  --hover-btn: #2a303a;
  --surface-elevated: #1c2129;
  --callout-warn-bg: #2a2118;
  --callout-info-bg: #152033;
  --callout-ok-bg: #14241a;
  --callout-fail-bg: #2a1616;
  --chip-ok-bg: #14241a; --chip-ok-border: #2d5a3c; --chip-ok-text: #7dcea0;
  --chip-fail-bg: #2a1616; --chip-fail-border: #6b3030; --chip-fail-text: #f0a0a0;
  --chip-warn-bg: #2a2118; --chip-warn-border: #6b5020; --chip-warn-text: #e0b060;
  --chip-info-bg: #152033; --chip-info-border: #2a5080; --chip-info-text: #6cb6ff;
}
* { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0;
  font-family: "IBM Plex Sans", "Segoe UI", system-ui, sans-serif;
  background: var(--bg); color: var(--text);
  line-height: 1.6;
}
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }
.layout { display: flex; min-height: 100vh; }
.sidebar {
  width: var(--sidebar-w); flex-shrink: 0;
  background: var(--panel); border-right: 1px solid var(--border);
  padding: 1.25rem 1rem 2rem; overflow-y: auto;
  position: sticky; top: 0; height: 100vh;
}
.sidebar h1 {
  font-size: 1.1rem; margin: 0 0 0.25rem;
  font-family: "IBM Plex Serif", Georgia, serif;
}
.sidebar .sub { color: var(--muted); font-size: 0.8rem; margin-bottom: 1rem; }
.sidebar details { margin-bottom: 0.5rem; }
.sidebar summary {
  cursor: pointer; font-weight: 600; font-size: 0.85rem;
  padding: 0.35rem 0.25rem; list-style: none;
}
.sidebar summary::-webkit-details-marker { display: none; }
.sidebar summary::before { content: "▸ "; color: var(--muted); }
.sidebar details[open] summary::before { content: "▾ "; }
.sidebar ul { list-style: none; margin: 0 0 0.4rem 0.6rem; padding: 0; }
.sidebar li { margin: 0.15rem 0; }
.sidebar a {
  display: block; padding: 0.2rem 0.4rem; border-radius: 4px;
  color: var(--text); font-size: 0.85rem;
}
.sidebar a:hover, .sidebar a.active {
  background: var(--code-bg); text-decoration: none;
}
.sidebar details.nav-root {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.35rem 0.45rem 0.5rem;
  margin-bottom: 0.75rem;
  background: var(--nav-root-bg);
}
.sidebar details.nav-root > summary {
  font-size: 0.9rem;
  font-weight: 700;
  padding: 0.45rem 0.25rem;
}
.sidebar details.nav-root.mindgrip > summary { color: var(--mindgrip); }
.sidebar .brand-tagline {
  color: var(--muted);
  font-size: 0.72rem;
  line-height: 1.35;
  margin: 0 0.35rem 0.55rem;
  padding: 0.35rem 0.45rem;
  background: var(--tagline-bg);
  border-radius: 6px;
  border-left: 3px solid var(--mindgrip);
}
.sidebar .ext-docs {
  margin: 0.75rem 0.15rem 0;
  padding: 0.65rem 0.7rem;
  border: 1px dashed var(--border);
  border-radius: 8px;
  background: var(--nav-root-bg);
  font-size: 0.82rem;
  line-height: 1.4;
}
.sidebar .ext-docs strong { display: block; margin-bottom: 0.25rem; color: var(--text); }
.sidebar .ext-docs a { color: var(--link); font-weight: 600; word-break: break-all; }
.sidebar details.nav-root .nav-section { margin-left: 0.15rem; }
.app-brand {
  margin: 0 0 1.25rem;
  padding: 0.75rem 1rem;
  background: var(--brand-grad);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.92rem;
}
.app-brand strong { color: var(--mindgrip); font-size: 1.05rem; }
.app-brand .tagline { display: block; color: var(--muted); margin-top: 0.25rem; font-size: 0.85rem; }
.content {
  flex: 1; max-width: 900px; padding: 2rem 2.5rem 4rem;
  background: var(--panel); margin: 0 auto; min-width: 0;
}
.content h1, .content h2, .content h3 {
  font-family: "IBM Plex Serif", Georgia, serif;
  line-height: 1.25;
}
.content h1 { margin-top: 0; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; }
.content h2 { margin-top: 2rem; }
.content pre {
  background: var(--code-bg); padding: 0.9rem 1rem; overflow-x: auto;
  border-radius: 6px; border: 1px solid var(--border); font-size: 0.88rem;
}
.content code {
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 0.9em; background: var(--code-bg); padding: 0.1em 0.35em; border-radius: 3px;
}
.content pre code { background: none; padding: 0; }
.content table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.92rem; }
.content th, .content td {
  border: 1px solid var(--border); padding: 0.45rem 0.65rem; text-align: left;
}
.content th { background: var(--code-bg); }
.content img { max-width: 100%; height: auto; }
.content blockquote {
  margin: 1rem 0; padding: 0.5rem 1rem; border-left: 4px solid var(--accent);
  background: var(--blockquote-bg); color: var(--muted);
}
.theme-toggle {
  position: fixed; bottom: 1.25rem; right: 1.25rem; z-index: 50;
  width: 2.5rem; height: 2.5rem; border-radius: 999px;
  border: 1px solid var(--border); background: var(--panel); color: var(--text);
  cursor: pointer; font-size: 1.1rem; line-height: 1;
  box-shadow: 0 4px 14px rgba(0,0,0,.12);
}
.theme-toggle:hover { background: var(--code-bg); }
.topbar {
  display: none; padding: 0.75rem 1rem; background: var(--panel);
  border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 2;
}
@media (max-width: 860px) {
  .layout { flex-direction: column; }
  .sidebar { position: static; height: auto; width: 100%; max-height: 40vh; }
  .content { padding: 1.25rem; }
  .topbar { display: block; }
}
"""

THEME_BOOT = """\
<script>
(function () {
  try {
    var stored = localStorage.getItem("docs-theme");
    var theme = stored || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
  } catch (e) {}
})();
</script>
"""

THEME_UI = """\
<button type="button" class="theme-toggle" id="theme-toggle" title="Toggle light / dark" aria-label="Toggle color theme">◐</button>
<script>
(function () {
  var btn = document.getElementById("theme-toggle");
  if (!btn) return;
  function current() {
    return document.documentElement.getAttribute("data-theme") || "light";
  }
  function apply(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem("docs-theme", theme); } catch (e) {}
    btn.textContent = theme === "dark" ? "☀" : "☾";
    btn.title = theme === "dark" ? "Switch to light theme" : "Switch to dark theme";
  }
  apply(current());
  btn.addEventListener("click", function () {
    apply(current() === "dark" ? "light" : "dark");
  });
})();
</script>
"""

PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} · {title_suffix}</title>
  {theme_boot}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Serif:wght@500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{root}styles.css" />
</head>
<body>
  <div class="layout">
    <nav class="sidebar">
      <h1><a href="{root}mindgrip.html" style="color:inherit;text-decoration:none">{app_name}</a></h1>
      <div class="sub">MindGrip AI project docs</div>
      {nav}
    </nav>
    <main class="content">
{brand_banner}{body}
    </main>
  </div>
{theme_ui}
</body>
</html>
"""


def root_prefix(stem: str) -> str:
    """Relative path from a page back to docs/html/ ('' or '../'…)."""
    depth = Path(stem).parent.parts
    return "../" * len(depth) if depth and depth != (".",) else ""


def brand_banner(stem: str) -> str:
    if stem not in CUSTOM_PAGES:
        return ""
    return (
        f'<div class="app-brand"><strong>{APP_NAME}</strong>'
        f'<span class="tagline">{APP_TAGLINE}</span></div>\n'
    )


def title_suffix(stem: str) -> str:
    return APP_NAME if stem in CUSTOM_PAGES else "LeRobot Docs"


def find_source(stem: str) -> Path | None:
    for ext in (".mdx", ".md", ".html"):
        p = SOURCE / f"{stem}{ext}"
        if p.exists():
            return p
    return None


def render_custom_html(src: Path, stem: str, toc_titles: dict[str, str]) -> str:
    """Inject shared sidebar nav into a custom HTML page (<!--NAV--> placeholder)."""
    html = src.read_text(encoding="utf-8")
    nav = build_nav(stem)
    if "<!--NAV-->" not in html:
        raise ValueError(f"{src.name} is missing <!--NAV--> sidebar placeholder")
    html = html.replace("<!--NAV-->", nav)

    # Early theme boot (avoid flash)
    if "docs-theme" not in html.split("</head>", 1)[0]:
        html = html.replace("<head>", f"<head>\n  {THEME_BOOT}", 1)

    # Brand sidebar header on custom HTML shells
    html = re.sub(
        r'(<nav class="sidebar">\s*)<h1>.*?</h1>\s*<div class="sub">.*?</div>',
        rf'\1<h1><a href="mindgrip.html" style="color:inherit;text-decoration:none">{APP_NAME}</a></h1>\n'
        rf'      <div class="sub">{APP_TAGLINE}</div>',
        html,
        count=1,
        flags=re.DOTALL,
    )

    suffix = title_suffix(stem)
    label = CUSTOM_PAGES.get(stem) or toc_titles.get(stem)
    if label:
        html = re.sub(
            r"<title>.*?</title>",
            f"<title>{label} · {suffix}</title>",
            html,
            count=1,
            flags=re.DOTALL,
        )

    # Insert MindGrip banner after <main ...> opening tag when missing
    if 'class="app-brand"' not in html:
        html = re.sub(
            r"(<main\b[^>]*>)",
            rf"\1\n{brand_banner(stem)}",
            html,
            count=1,
            flags=re.IGNORECASE,
        )

    # Theme toggle UI
    if 'id="theme-toggle"' not in html:
        if "</body>" in html:
            html = html.replace("</body>", f"{THEME_UI}\n</body>", 1)
        else:
            html += THEME_UI
    return html


def preprocess_mdx(text: str) -> str:
    """Light cleanup so pandoc can parse MDX-ish content."""
    # Drop HTML comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    # GitHub-style alerts: > [!CAUTION] / [!WARNING] / ...
    text = re.sub(
        r"> \[!(CAUTION|IMPORTANT|WARNING|TIP|NOTE)\]\s*\n",
        r"> **\1:**\n",
        text,
    )
    # Tip/Warning style callouts used in some HF docs
    text = re.sub(
        r"<Tip(?:\s+warning)?>\s*",
        "\n> ",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"</Tip>", "\n", text, flags=re.IGNORECASE)
    # Convert relative .mdx links to .html
    text = re.sub(r"\]\(\./([^)#]+)\.mdx(#[^)]*)?\)", r"](\1.html\2)", text)
    text = re.sub(r"\]\(([^)/][^)]*)\.mdx(#[^)]*)?\)", r"](\1.html\2)", text)
    # Bare relative links without extension: ./installation -> installation.html
    text = re.sub(r"\]\(\./([a-zA-Z0-9_-]+)\)", r"](\1.html)", text)
    return text


def mdx_to_body_html(src: Path) -> str:
    cleaned = preprocess_mdx(src.read_text(encoding="utf-8"))
    tmp = OUT / "_tmp_input.md"
    tmp.write_text(cleaned, encoding="utf-8")
    result = subprocess.run(
        [
            "pandoc",
            str(tmp),
            "-f",
            "markdown+raw_html",
            "-t",
            "html",
            "--wrap=none",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    tmp.unlink(missing_ok=True)
    return result.stdout


def build_nav(active: str) -> str:
    prefix = root_prefix(active)

    custom_links: list[str] = []
    for stem, label in CUSTOM_PAGES.items():
        if not find_source(stem):
            continue
        cls = ' class="active"' if stem == active else ""
        custom_links.append(
            f'<li><a href="{prefix}{stem}.html"{cls}>{label}</a></li>'
        )

    mindgrip_block = (
        f'<details class="nav-root mindgrip" open>'
        f"<summary>MindGrip AI — Custom Project Pages</summary>"
        f'<p class="brand-tagline">{APP_TAGLINE}</p>'
        f"<ul>{''.join(custom_links)}</ul>"
        f"</details>"
    )

    external = (
        f'<div class="ext-docs">'
        f"<strong>Original LeRobot documentation</strong>"
        f"Not mirrored here — read the official docs on Hugging Face:<br>"
        f'<a href="{LEROBOT_DOCS_URL}" target="_blank" rel="noopener noreferrer">'
        f"{LEROBOT_DOCS_URL}</a>"
        f"</div>"
    )

    return f"{mindgrip_block}\n{external}"


def page_title(stem: str, body_html: str, toc_titles: dict[str, str]) -> str:
    if stem in CUSTOM_PAGES:
        return CUSTOM_PAGES[stem]
    if stem in toc_titles:
        return toc_titles[stem]
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body_html, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip() or stem
    return stem


def main() -> None:
    if OUT.exists():
        # Keep lab images across rebuilds
        existing_images = OUT / "images"
        if existing_images.is_dir():
            staging = ROOT / "_lab_images"
            staging.mkdir(parents=True, exist_ok=True)
            shutil.copytree(existing_images, staging, dirs_exist_ok=True)
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    (OUT / "styles.css").write_text(CSS, encoding="utf-8")

    for img_dir in (IMAGES, ROOT / "_lab_images"):
        if img_dir.is_dir():
            shutil.copytree(img_dir, OUT / "images", dirs_exist_ok=True)
            print(f"  ✓ copied {img_dir.name}/ → {OUT / 'images'}")

    toc_titles = dict(CUSTOM_PAGES)
    all_stems = list(CUSTOM_PAGES.keys())

    built = 0
    missing = []
    for stem in all_stems:
        src = find_source(stem)
        if not src:
            missing.append(stem)
            continue
        if src.suffix == ".html":
            html = render_custom_html(src, stem, toc_titles)
        else:
            body = mdx_to_body_html(src)
            title = page_title(stem, body, toc_titles)
            html = PAGE_TEMPLATE.format(
                title=title,
                title_suffix=title_suffix(stem),
                nav=build_nav(stem),
                body=body,
                root=root_prefix(stem),
                app_name=APP_NAME,
                brand_banner=brand_banner(stem),
                theme_boot=THEME_BOOT,
                theme_ui=THEME_UI,
            )
        out_path = OUT / f"{stem}.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        built += 1
        print(f"  ✓ {stem}.html")

    # Default landing → MindGrip home
    if (OUT / "mindgrip.html").exists():
        (OUT / "index.html").write_text(
            '<!DOCTYPE html><html lang="en"><head>'
            '<meta charset="utf-8"/>'
            '<meta http-equiv="refresh" content="0; url=mindgrip.html"/>'
            '<title>MindGrip AI Docs</title></head>'
            '<body><p>Redirecting to <a href="mindgrip.html">MindGrip AI</a>…</p></body></html>\n',
            encoding="utf-8",
        )

    (OUT / "README.md").write_text(
        f"# {APP_NAME} Docs\n\n"
        f"**{APP_NAME}** — {APP_TAGLINE}\n\n"
        "This site only hosts **MindGrip AI custom project pages**.\n\n"
        f"Official LeRobot documentation: {LEROBOT_DOCS_URL}\n\n"
        "Rebuild: `python3 docs/build_html.py`\n",
        encoding="utf-8",
    )

    print(f"\nBuilt {built} MindGrip HTML pages → {OUT}")
    if missing:
        print("Missing sources:", ", ".join(missing))


if __name__ == "__main__":
    main()
