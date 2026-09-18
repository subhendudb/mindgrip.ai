#!/usr/bin/env python3
"""Build an HTML grid of every episode video so they can be viewed together."""

from __future__ import annotations

import json
import subprocess
import webbrowser
from pathlib import Path

import pyarrow.parquet as pq

DS = Path.home() / "Documents/lerobot/SUBHENDU/pick_place_sorting_20260909_011504"
GALLERY = DS / "_gallery"
CAM = "observation.images.front"
VIDEO_KEY = f"videos/{CAM}"


def ffmpeg_ok() -> None:
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        raise SystemExit("ffmpeg is required (brew install ffmpeg)") from e


def extract_clip(src: Path, start: float, end: float, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dur = max(end - start, 0.1)
    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{start:.3f}",
        "-i",
        str(src),
        "-t",
        f"{dur:.3f}",
        "-c",
        "copy",
        "-avoid_negative_ts",
        "make_zero",
        str(dest),
        "-hide_banner",
        "-loglevel",
        "error",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or dest.stat().st_size < 1000:
        cmd_re = [
            "ffmpeg",
            "-y",
            "-ss",
            f"{start:.3f}",
            "-i",
            str(src),
            "-t",
            f"{dur:.3f}",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "28",
            str(dest),
            "-hide_banner",
            "-loglevel",
            "error",
        ]
        subprocess.run(cmd_re, check=True)


def write_html(rows: list[dict], out: Path) -> None:
    cards = []
    for r in rows:
        ep = r["episode_index"]
        sec = r["length"] / 30.0
        cards.append(
            f"""
      <figure class="card">
        <video src="ep_{ep:03d}.mp4" muted playsinline loop preload="metadata" controls></video>
        <figcaption>Episode {ep} · {r["length"]} frames · {sec:.1f}s</figcaption>
      </figure>"""
        )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>All 50 episodes — pick_place_sorting</title>
  <style>
    :root {{ --navy:#0E1C2B; --cyan:#00A9CE; --bg:#101820; --card:#1a2430; --text:#e8eef3; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--text); }}
    header {{ position:sticky; top:0; z-index:2; background:var(--navy); padding:14px 20px; display:flex; gap:12px; align-items:center; flex-wrap:wrap; }}
    h1 {{ margin:0; font-size:18px; font-weight:600; }}
    .sub {{ color:#8fa6b8; font-size:13px; }}
    button {{ background:var(--cyan); color:var(--navy); border:0; border-radius:6px; padding:8px 14px; font-weight:700; cursor:pointer; }}
    button.ghost {{ background:transparent; color:var(--cyan); border:1px solid var(--cyan); }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:12px; padding:16px; }}
    .card {{ margin:0; background:var(--card); border-radius:8px; overflow:hidden; }}
    video {{ width:100%; aspect-ratio:4/3; background:#000; display:block; }}
    figcaption {{ padding:8px 10px; font-size:12px; color:#c5d0d8; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>SUBHENDU / pick_place_sorting_20260909_011504</h1>
      <div class="sub">{len(rows)} episodes together · front camera · 640×480 @ 30 fps</div>
    </div>
    <button type="button" onclick="playAll()">Play all</button>
    <button type="button" class="ghost" onclick="pauseAll()">Pause all</button>
  </header>
  <div class="grid">
    {"".join(cards)}
  </div>
  <script>
    function playAll() {{ document.querySelectorAll("video").forEach(v => v.play()); }}
    function pauseAll() {{ document.querySelectorAll("video").forEach(v => v.pause()); }}
  </script>
</body>
</html>
"""
    out.write_text(html, encoding="utf-8")


def main() -> None:
    ffmpeg_ok()
    GALLERY.mkdir(parents=True, exist_ok=True)
    table = pq.read_table(DS / "meta/episodes/chunk-000/file-000.parquet")
    data = table.to_pydict()
    n = len(data["episode_index"])
    rows = []
    for i in range(n):
        ep = int(data["episode_index"][i])
        chunk = int(data[f"{VIDEO_KEY}/chunk_index"][i])
        file_i = int(data[f"{VIDEO_KEY}/file_index"][i])
        start = float(data[f"{VIDEO_KEY}/from_timestamp"][i])
        end = float(data[f"{VIDEO_KEY}/to_timestamp"][i])
        length = int(data["length"][i])
        src = DS / "videos" / CAM / f"chunk-{chunk:03d}" / f"file-{file_i:03d}.mp4"
        dest = GALLERY / f"ep_{ep:03d}.mp4"
        print(f"Episode {ep:02d}/{n-1}  {start:.2f}s–{end:.2f}s  ← {src.name}")
        extract_clip(src, start, end, dest)
        rows.append({"episode_index": ep, "length": length})
    html_path = GALLERY / "index.html"
    write_html(rows, html_path)
    print(f"\nGallery: {html_path}")
    webbrowser.open(html_path.as_uri())


if __name__ == "__main__":
    main()
