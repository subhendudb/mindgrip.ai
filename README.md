# SO-101 Lab

Overlay project for **SO-101 pick & place sorting**. Vanilla [LeRobot](https://github.com/huggingface/lerobot) stays the core; this repo only owns your plugins, scripts, and optional UX patches.

```
lerobot/          ← core (Docker base / untouched upstream)
so101-lab/        ← this project (your additions only)
```

## What’s in here

| Path | Role |
|------|------|
| `packages/lerobot_robot_so101_mujoco/` | Official-style robot plugin (`--robot.type=so101_mujoco`) |
| `packages/lerobot_teleoperator_so101_keyboard/` | Teleop plugin (`--teleop.type=so101_keyboard`) |
| `so101_cli_menu.sh` | Interactive CLI for calibrate / teleop / record / train |
| `scripts/` | Home setup, episode viewer, patch applier |
| `patches/` | Optional diffs for recording keyboard UX, OpenCV OBS fix, dataset viz |
| `docs/` | Authoring sources (`docs/source/*.html` + `.mdx`) for MindGrip docs |
| `docs-web/` | MindGrip AI docs — React + Vite SPA (`npm run dev` → :8000) |
| `docker/Dockerfile` | `FROM lerobot-user` + install plugins |
| `docker-compose.yml` | Optional lab shell (+ opt-in docs profile) |

No forks of `src/lerobot/` are required for MuJoCo or keyboard teleop — LeRobot auto-discovers packages named `lerobot_robot_*` / `lerobot_teleoperator_*`.

## Local setup (macOS / Linux)

```bash
# 1) Vanilla LeRobot (sibling checkout)
cd /path/to/temp
git clone https://github.com/huggingface/lerobot.git   # or your fork
cd lerobot && uv sync --extra feetech --extra hardware --extra viz

# 2) This overlay
cd ../so101-lab
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ../lerobot
uv pip install -e packages/lerobot_robot_so101_mujoco
uv pip install -e packages/lerobot_teleoperator_so101_keyboard

# 3) Optional: recording / camera / viz UX patches onto the lerobot tree
./scripts/apply_lerobot_patches.sh ../lerobot

# 4) Permanent HF_LEROBOT_HOME (calibration outside ~/.cache)
./scripts/setup_lerobot_home.sh

# 5) Menu
./so101_cli_menu.sh
```

Quick smoke test (plugins registered):

```bash
uv run python -c "from lerobot.utils.import_utils import register_third_party_plugins as r; r(); from lerobot.robots.config import RobotConfig; print('so101_mujoco' in RobotConfig.get_known_choices())"
```

## Docker

```bash
# Interactive lab shell (needs so101-lab image)
docker compose build lab
docker compose run --rm lab
docker compose run --rm lab ./so101_cli_menu.sh

# Build core image from the lerobot repo (once, if missing)
docker build -f ../lerobot/docker/Dockerfile.user -t lerobot-user ../lerobot

# Overlay with UX patches
APPLY_PATCHES=1 docker compose build --no-cache lab

# Optional: docs via nginx (prefer local npm below)
docker compose --profile docs up --build docs
# → http://localhost:8000/
```

The `lab` service is behind profile `lab` — use `compose run` for a shell. Docs Docker is behind profile `docs` (local `npm run dev` is the default). Datasets persist in the `so101-data` volume.

## Optional patches

These improve day-to-day SO-101 workflows but touch core LeRobot files. Prefer upstream PRs long-term; until then:

```bash
./scripts/apply_lerobot_patches.sh /path/to/lerobot
```

| Patch | Effect |
|-------|--------|
| `0001-recording-keyboard-stdin-fallback.patch` | `n`/`Enter`/`q` via TTY (no macOS Accessibility) |
| `0002-skip-reset-on-early-episode-end.patch` | Skip reset wait after early episode end |
| `0003-opencv-obs-virtual-camera-resize.patch` | OBS Virtual Camera FPS / resize tolerance |
| `0004-dataset-viz-all-episodes.patch` | `--all-episodes` in dataset viz |

## Custom docs (React + Vite)

MindGrip project docs (home, roadmap, LeLab, CLI, kinematics, policy cheatsheet, MuJoCo optional tooling, …):

```bash
cd docs-web && npm install && npm run dev
# → http://localhost:8000/  (hot reload)

# After editing docs/source/*.html:
python3 docs-web/scripts/extract_fragments.py
```

Optional production-style nginx image: `docker compose --profile docs up --build docs`.

Official LeRobot library docs (not mirrored here): https://huggingface.co/docs/lerobot

See [`docs-web/README.md`](docs-web/README.md) for the full site map and authoring notes.

## Clean up the LeRobot tree

After extracting this overlay, you can restore vanilla LeRobot:

```bash
cd ../lerobot
git checkout -- .
git clean -fd -- src/lerobot/robots/so101_mujoco src/lerobot/teleoperators/so101_keyboard \
  so101_cli_menu.sh start.sh examples/so101_mujoco scripts/setup_lerobot_home.sh scripts/view_all_episodes.py
# also remove lab docs tooling if present:
# rm -rf docs/html docs/build_html.py docs/serve_html.py
# rm -f docs/source/{acronyms,directory_structure,policy_cheatsheet,so101_mujoco}.mdx
# rm -f docs/source/{mindgrip,project_page,roadmap,lelab,cli_menu,so101_kinematics,optional_tooling,policy_cheatsheet}.html
# rm -rf docs-web
```

Do **not** run destructive `git clean` until you confirm everything you care about lives under `so101-lab/`.

© 2026 Subhendu Datta Bhowmik. All rights reserved.