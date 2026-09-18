# MindGrip AI docs

React + Vite SPA for **MindGrip AI** / so101-lab project documentation.

Official LeRobot docs (not mirrored): https://huggingface.co/docs/lerobot · LeLab: https://huggingface.co/docs/lerobot/lelab

Author: [Subhendu Datta Bhowmik](https://subhdb.co.in)

## Develop

```bash
cd docs-web
npm install
npm run dev
# → http://localhost:8000/
```

After editing `docs/source/*.html`, rebuild fragments:

```bash
python3 scripts/extract_fragments.py
# or from repo root:
python3 docs-web/scripts/extract_fragments.py
```

Prefer this local npm workflow. Docker nginx is optional (`docker compose --profile docs up --build docs`).

## Production build

```bash
cd docs-web
npm run build
npm run preview
```

## Site map

| Route | Page | Source |
|-------|------|--------|
| `/` | MindGrip AI Home | HTML fragment `mindgrip` |
| `/project_page` | Pick & Place Sorting | HTML fragment |
| `/roadmap` | Roadmap · Support · Reference | HTML fragment |
| `/lelab` | LeLab (Recommended Path) | HTML fragment |
| `/cli_menu` | CLI Command Menu | HTML fragment |
| `/so101_kinematics` | Forward & Inverse Kinematics | HTML fragment |
| `/policy_cheatsheet` | Policy Cheatsheet | HTML fragment |
| `/optional_tooling` | Optional Tooling · MuJoCo | HTML fragment |
| `/directory_structure` | Directory Structure | Markdown |
| `/acronyms` | Acronyms Glossary | Markdown |

HTML fragments are authored in `docs/source/*.html` and extracted to `public/fragments/`.  
Markdown pages live in `src/content/` (synced from `docs/source/*.mdx` when used).

## Layout

| Path | Role |
|------|------|
| `src/` | React app (routes, layout, theme, footer) |
| `src/components/` | Sidebar, HtmlFragment, MarkdownView, SiteFooter, … |
| `src/content/` | Markdown sources (`directory_structure`, `acronyms`) |
| `src/data/nav.ts` | Page titles, nav order, fragment set |
| `public/fragments/` | Extracted HTML for rich pages |
| `public/images/` | Screenshots, hero, assembly media |
| `public/videos/` | Demo / outcome clips |
| `scripts/extract_fragments.py` | Rebuild fragments from `docs/source/*.html` |

## Authoring tips

- **Rich pages** (roadmap, project, CLI, kinematics, …): edit `docs/source/<slug>.html`, then run `extract_fragments.py`.
- **Markdown pages**: edit `src/content/<slug>.md` (or the matching `docs/source/*.mdx`).
- Nav order and fragment list: `src/data/nav.ts`.
- Shared chrome (sidebar, theme, **© footer**): `src/components/Layout.tsx`.

## Optional tooling scope

This docs set documents **MuJoCo + keyboard teleop** as optional sim plugins (`packages/`, CLI · 16–18).  
ROS2 / Gazebo / RViz are **not** part of the install or CLI path.

## License / copyright

© 2026 Subhendu Datta Bhowmik. All rights reserved.
