# Repository directory structure

This page maps **so101-lab** (the MindGrip overlay). Vanilla [LeRobot](https://github.com/huggingface/lerobot) stays a **sibling checkout** — this repo does not replace `src/lerobot/`.

```text
temp/   (or your workspace)
├── lerobot/      ← upstream core (clone / Docker base)
└── so101-lab/    ← this project (plugins, CLI, docs, patches)
```

> Browse the sidebar for all chapters. Edit HTML sources under `docs/source/`; the React site lives in `docs-web/`.

---

## Top-level tree (so101-lab)

```text
so101-lab/
├── packages/                 # Installable LeRobot plugins
│   ├── lerobot_robot_so101_mujoco/
│   └── lerobot_teleoperator_so101_keyboard/
├── so101_cli_menu.sh         # Interactive calibrate / teleop / record / train / rollout
├── scripts/                  # HF home, patches, docs helpers, episode viewer
├── patches/                  # Optional diffs applied onto a lerobot checkout
├── docs/                     # HTML/MDX sources (+ optional static html build)
├── docs-web/                 # MindGrip docs SPA (Vite + React) — preferred local site
├── docker/                   # Overlay image ON TOP of lerobot-user
├── docker-compose.yml        # lab shell (+ optional docs profile)
├── images/                   # Shared photos / diagrams
├── pyproject.toml            # Overlay Python project metadata
└── README.md                 # Setup: sibling lerobot + plugins + menu
```

---

## Top-level folders

| Path | Purpose |
|------|---------|
| **`packages/`** | Third-party plugins auto-discovered by LeRobot (`lerobot_robot_*`, `lerobot_teleoperator_*`). |
| **`so101_cli_menu.sh`** | Day-to-day terminal workflow; config in `.so101_cli.env` (menu **C**). |
| **`scripts/`** | `setup_lerobot_home.sh`, `apply_lerobot_patches.sh`, `build_docs.sh`, `view_all_episodes.py`. |
| **`patches/`** | Optional UX patches for recording keys, OBS cam, dataset viz — see `patches/README.md`. |
| **`docs/source/`** | Authoritative page sources (`.html` fragments + `.mdx`). |
| **`docs/html/`** | Optional static HTML build (legacy / offline). Prefer **`docs-web`**. |
| **`docs-web/`** | Local docs site: `npm run dev` → http://localhost:8000/. |
| **`docker/`** | `Dockerfile` extending `lerobot-user` with this overlay’s plugins. |
| **`images/`** | Camera placement, assembly photos, home hero assets. |

---

## `packages/` — plugins

| Package | Registers as | Role |
|---------|--------------|------|
| **`lerobot_robot_so101_mujoco`** | `--robot.type=so101_mujoco` | MuJoCo sim follower for practice without hardware. |
| **`lerobot_teleoperator_so101_keyboard`** | `--teleop.type=so101_keyboard` | Keyboard teleop (sim / bring-up). |

Install into the same venv as LeRobot:

```bash
uv pip install -e packages/lerobot_robot_so101_mujoco
uv pip install -e packages/lerobot_teleoperator_so101_keyboard
```

No copy of upstream `src/lerobot/robots/…` is required for these plugins.

---

## `scripts/`

| Script | Purpose |
|--------|---------|
| **`setup_lerobot_home.sh`** | Points `HF_LEROBOT_HOME` at a stable folder (e.g. `~/Documents/lerobot`) for calibration / datasets. |
| **`apply_lerobot_patches.sh`** | Applies `patches/*.patch` onto a sibling `lerobot` tree. |
| **`build_docs.sh`** | Rebuilds static docs helpers when needed. |
| **`view_all_episodes.py`** | Helper for browsing recorded episodes. |

---

## `patches/` (optional)

Touch core LeRobot files only when applied. Prefer upstream PRs long-term.

| Patch | Effect |
|-------|--------|
| `0001-recording-keyboard-stdin-fallback.patch` | `n` / Enter / `q` via TTY (macOS Accessibility workaround) |
| `0002-skip-reset-on-early-episode-end.patch` | Skip reset wait after early episode end |
| `0003-opencv-obs-virtual-camera-resize.patch` | OBS Virtual Camera FPS / resize tolerance |
| `0004-dataset-viz-all-episodes.patch` | `--all-episodes` for dataset viz |

```bash
./scripts/apply_lerobot_patches.sh ../lerobot
```

---

## `docs/` & `docs-web/`

| Path | Purpose |
|------|---------|
| **`docs/source/*.html`** | Rich pages (home, project, roadmap, LeLab, CLI, kinematics, policy cheatsheet, optional tooling). |
| **`docs/source/*.mdx`** | Shorter markdown chapters (acronyms, policy cheatsheet, directory structure, …). |
| **`docs-web/scripts/extract_fragments.py`** | Extracts `<main>` (+ styles/scripts) → `docs-web/public/fragments/`. |
| **`docs-web/src/content/*.md`** | Markdown chapters loaded by the SPA. |
| **`docs-web/public/images/`**, **`videos/`** | Assets served by the site. |
| **`docs-web/public/brand/`** | MindGrip mark / logo. |

After editing HTML sources:

```bash
python3 docs-web/scripts/extract_fragments.py
cd docs-web && npm run dev
```

---

## `docker/` (overlay)

| Item | Purpose |
|------|---------|
| **`docker/Dockerfile`** | `FROM lerobot-user` + install so101-lab plugins (optional patches via build arg). |
| **`docker-compose.yml`** | `compose run --rm lab` for a shell; docs profile optional — local npm is preferred. |

Build the upstream base once from the lerobot repo (`Dockerfile.user` → `lerobot-user`), then build this overlay.

---

## Sibling `lerobot/` (not in this repo)

You still need a normal LeRobot checkout for `uv run lerobot-train`, Feetech extras, etc. Mentally:

| Area (inside lerobot) | Role for this lab |
|-----------------------|-------------------|
| **`src/lerobot/robots/`**, **`teleoperators/`**, **`motors/`**, **`cameras/`** | Real SO-101 drivers + USB cam |
| **`src/lerobot/policies/`** | ACT, Diffusion, SmolVLA, … |
| **`src/lerobot/datasets/`** | LeRobotDataset + Hub |
| **`src/lerobot/scripts/`** | CLIs: calibrate, teleoperate, record, train, rollout, … |
| **`docker/Dockerfile.user`** | Base image this overlay extends |

Official layout details: upstream LeRobot repo + [huggingface.co/docs/lerobot](https://huggingface.co/docs/lerobot).

---

## Day-to-day files you’ll touch

| File / path | Why |
|-------------|-----|
| **`.so101_cli.env`** | Ports, `LeoArm` ids, camera index, `TASK`, dataset name (created/edited via menu **C**). |
| **`$HF_LEROBOT_HOME/calibration/…/LeoArm.json`** | Leader & follower calibration. |
| **`$HF_LEROBOT_HOME/<user>/pick_place_sorting*`** | Local datasets (often timestamp-stamped). |
| **`outputs/train/…`** | Local checkpoints if you train on a CUDA host instead of HF Jobs. |

---

## Quick mental model

1. **Hardware & teleop** → LeRobot drivers + LeLab or `so101_cli_menu.sh` (0–9)
2. **Data** → menu **10 / 11** (record / viz) · Hub dataset
3. **Train** → LeLab HF Jobs or menu **12 / 13** on CUDA
4. **Deploy** → menu **14 / 15** or LeLab **Run on robot**
5. **Sim / extras** → `packages/*` · [Optional Tooling](./optional_tooling)

Related: [MindGrip home](./mindgrip) · [Acronyms](./acronyms) · [README](https://github.com/huggingface/lerobot) (upstream).
