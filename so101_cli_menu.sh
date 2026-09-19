#!/usr/bin/env bash
# Interactive CLI menu for the SO-101 pick & place sorting project (so101-lab overlay).
# Usage:  ./so101_cli_menu.sh
# Config: .so101_cli.env  (created on first run; ports / ids / HF user)
#
# This Mac / LeLab robot record uses the SAME id for both arms:
#   LEADER_ID=LeoArm   → $HF_LEROBOT_HOME/calibration/teleoperators/so_leader/LeoArm.json
#   FOLLOWER_ID=LeoArm → $HF_LEROBOT_HOME/calibration/robots/so_follower/LeoArm.json
# Permanent home (not ~/.cache): run ./scripts/setup_lerobot_home.sh once.
# Do not use legacy my_leader / my_follower unless you recalibrate under those ids.
# MuJoCo sim robot id stays sim_follower (not a calibration file on disk).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

# Keep calibration / LeLab robots out of ~/.cache (that folder was wiped).
export HF_LEROBOT_HOME="${HF_LEROBOT_HOME:-$HOME/Documents/lerobot}"
export HF_LEROBOT_CALIBRATION="${HF_LEROBOT_CALIBRATION:-$HF_LEROBOT_HOME/calibration}"

CONFIG_FILE="${SO101_CLI_ENV:-$ROOT/.so101_cli.env}"

# ── defaults (this MacBook Air project) ──────────────────────────────────────
LEADER_PORT="${LEADER_PORT:-/dev/tty.usbmodem5AE60832361}"
FOLLOWER_PORT="${FOLLOWER_PORT:-/dev/tty.usbmodem5B141118901}"
LEADER_ID="${LEADER_ID:-LeoArm}"
FOLLOWER_ID="${FOLLOWER_ID:-LeoArm}"
HF_USER="${HF_USER:-your_username}"
DATASET_REPO="${DATASET_REPO:-pick_place_sorting}"
EVAL_REPO="${EVAL_REPO:-eval_pick_place_sorting}"
TASK="${TASK:-Pick coloured block and place in matching bin}"
CAM_INDEX="${CAM_INDEX:-0}"
CAM_WIDTH="${CAM_WIDTH:-640}"
CAM_HEIGHT="${CAM_HEIGHT:-480}"
CAM_FPS="${CAM_FPS:-30}"
POLICY_PATH="${POLICY_PATH:-outputs/train/sorting_act/checkpoints/last}"
NUM_EPISODES="${NUM_EPISODES:-100}"
EVAL_EPISODES="${EVAL_EPISODES:-20}"
EPISODE_TIME_S="${EPISODE_TIME_S:-120}"
RESET_TIME_S="${RESET_TIME_S:-60}"
DRY_RUN="${DRY_RUN:-0}"

load_config() {
  if [[ -f "$CONFIG_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$CONFIG_FILE"
  fi
}

save_config() {
  cat >"$CONFIG_FILE" <<EOF
# SO-101 CLI menu settings (edit or use menu option C)
LEADER_PORT="$LEADER_PORT"
FOLLOWER_PORT="$FOLLOWER_PORT"
LEADER_ID="$LEADER_ID"
FOLLOWER_ID="$FOLLOWER_ID"
HF_USER="$HF_USER"
DATASET_REPO="$DATASET_REPO"
EVAL_REPO="$EVAL_REPO"
TASK="$TASK"
CAM_INDEX="$CAM_INDEX"
CAM_WIDTH="$CAM_WIDTH"
CAM_HEIGHT="$CAM_HEIGHT"
CAM_FPS="$CAM_FPS"
POLICY_PATH="$POLICY_PATH"
NUM_EPISODES="$NUM_EPISODES"
EVAL_EPISODES="$EVAL_EPISODES"
EPISODE_TIME_S="$EPISODE_TIME_S"
RESET_TIME_S="$RESET_TIME_S"
EOF
  echo "Saved → $CONFIG_FILE"
}

need_uv() {
  if ! command -v uv >/dev/null 2>&1; then
    echo "Error: 'uv' not found. Install uv, then re-run."
    exit 1
  fi
}

# Sibling LeRobot checkout (editable install into so101-lab/.venv).
LEROBOT_SRC="${LEROBOT_SRC:-$ROOT/../lerobot}"

# so101-lab's pyproject has no feetech/viz/… extras — those live on LeRobot.
# Always install into THIS overlay's active venv via uv pip (not `uv sync` here).
ensure_lerobot_extras() {
  local extras="${1:-feetech,hardware,viz,dataset}"
  need_uv
  if [[ ! -f "$LEROBOT_SRC/pyproject.toml" ]]; then
    echo "Error: LeRobot checkout not found at $LEROBOT_SRC"
    echo "Expected sibling layout: temp/lerobot + temp/so101-lab"
    echo "Clone: git clone https://github.com/huggingface/lerobot.git \"$LEROBOT_SRC\""
    return 1
  fi
  echo "Installing LeRobot extras [$extras] into so101-lab .venv from $LEROBOT_SRC …"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "▶ uv pip install -e \"${LEROBOT_SRC}[${extras}]\""
    echo "(dry-run — not executed)"
    return 0
  fi
  uv pip install -e "${LEROBOT_SRC}[${extras}]"
}

# Replay / viz load LeRobotDataset — needs the dataset extra (huggingface datasets + pandas).
ensure_overlay_plugins() {
  # Editable installs of SO-101 Lab plugins (idempotent).
  if uv run python -c "import lerobot_robot_so101_mujoco, lerobot_teleoperator_so101_keyboard" >/dev/null 2>&1; then
    return 0
  fi
  echo "Installing so101-lab plugins…"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "▶ uv pip install -e packages/lerobot_robot_so101_mujoco -e packages/lerobot_teleoperator_so101_keyboard"
    echo "(dry-run — not executed)"
    return 0
  fi
  uv pip install -e "$ROOT/packages/lerobot_robot_so101_mujoco"
  uv pip install -e "$ROOT/packages/lerobot_teleoperator_so101_keyboard"
}

ensure_replay_deps() {
  ensure_overlay_plugins
  if uv run python -c "from lerobot.datasets import LeRobotDataset" >/dev/null 2>&1; then
    return 0
  fi
  ensure_lerobot_extras "dataset,feetech,hardware,viz"
}

# MuJoCo + keyboard need plugins; --display_data=true needs viz (rerun-sdk).
ensure_mujoco_deps() {
  echo "Ensuring so101-lab plugins + viz + feetech…"
  ensure_overlay_plugins
  ensure_lerobot_extras "viz,feetech"
}

open_teleop_sync_help() {
  # Interactive checklist page removed — tips live on the Roadmap.
  local docs_url="${DOCS_URL:-http://127.0.0.1:8000/roadmap#troubleshooting}"
  local page="$ROOT/docs/source/roadmap.html"
  echo "Teleop sync help → Roadmap · Troubleshooting"
  echo "  Prefer docs site: $docs_url"
  echo "  Source page:      $page  (#troubleshooting)"
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "(dry-run — not opening browser)"
    return 0
  fi
  if command -v open >/dev/null 2>&1; then
    open "$docs_url" 2>/dev/null || open "$page"
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$docs_url" 2>/dev/null || xdg-open "$page"
  else
    echo "Open in a browser: $docs_url"
  fi
}

# Teleop/record with Rerun: install viz if missing, else disable display.
display_flag() {
  if uv run python -c "import rerun" 2>/dev/null; then
    echo "true"
  else
    echo "Installing viz (rerun-sdk) for --display_data…" >&2
    if [[ "$DRY_RUN" != "1" ]]; then
      ensure_lerobot_extras "viz" >/dev/null || true
    fi
    if uv run python -c "import rerun" 2>/dev/null; then
      echo "true"
    else
      echo "Warning: rerun-sdk still missing — continuing with --display_data=false" >&2
      echo "false"
    fi
  fi
}

# Interactive MuJoCo viewer: native Control sliders drive the arm (no keyboard teleop).
run_mujoco_viewer() {
  echo
  echo "Opening MuJoCo 3D viewer — use native Control sliders (no keyboard teleop)."
  echo

  export PATH="$ROOT/.venv/bin:${PATH}"

  if [[ "$(uname -s)" == "Darwin" && -x "$ROOT/.venv/bin/mjpython" ]]; then
    local py_lib
    py_lib="$(uv run python -c 'import sysconfig; print(sysconfig.get_config_var("LIBDIR") or "")')"
    if [[ -n "$py_lib" ]]; then
      export DYLD_LIBRARY_PATH="${py_lib}${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
    fi
    echo "▶ mjpython -m lerobot_robot_so101_mujoco.run_viewer"
    echo
    if [[ "$DRY_RUN" == "1" ]]; then
      echo "(dry-run — not executed)"
      return 0
    fi
    "$ROOT/.venv/bin/mjpython" -m lerobot_robot_so101_mujoco.run_viewer
    return
  fi

  run uv run python -m lerobot_robot_so101_mujoco.run_viewer
}

# macOS MuJoCo passive viewer needs mjpython + libpython on DYLD_LIBRARY_PATH.
# Also put .venv/bin on PATH so rerun-cli is found when --display_data=true.
run_mujoco_teleoperate() {
  local -a args=("$@")
  echo
  echo "Opening MuJoCo 3D viewer (--robot.show_viewer=true)."
  echo "  Mouse: scroll=zoom · left-drag=orbit · right-drag=pan"
  echo

  export PATH="$ROOT/.venv/bin:${PATH}"

  if [[ "$(uname -s)" == "Darwin" && -x "$ROOT/.venv/bin/mjpython" ]]; then
    local py_lib
    py_lib="$(uv run python -c 'import sysconfig; print(sysconfig.get_config_var("LIBDIR") or "")')"
    if [[ -n "$py_lib" ]]; then
      export DYLD_LIBRARY_PATH="${py_lib}${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
    fi
    echo "▶ mjpython -m lerobot.scripts.lerobot_teleoperate ${args[*]}"
    echo
    if [[ "$DRY_RUN" == "1" ]]; then
      echo "(dry-run — not executed)"
      return 0
    fi
    "$ROOT/.venv/bin/mjpython" -m lerobot.scripts.lerobot_teleoperate "${args[@]}"
    return
  fi

  run uv run lerobot-teleoperate "${args[@]}"
}

run() {
  echo
  echo "▶ $*"
  echo
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "(dry-run — not executed)"
    return 0
  fi
  # shellcheck disable=SC2068
  "$@"
}

pause() {
  if [[ "${SO101_CLI_NONINTERACTIVE:-0}" == "1" ]]; then
    return 0
  fi
  echo
  read -r -p "Press Enter to return to menu… " _
}

prompt_default() {
  # $1=varname $2=prompt $3=current
  local _var="$1" _prompt="$2" _cur="$3" _ans
  read -r -p "${_prompt} [${_cur}]: " _ans
  if [[ -n "${_ans}" ]]; then
    printf -v "$_var" '%s' "$_ans"
  fi
}

print_viewer_help() {
  cat <<'EOF'

  SO-101 MuJoCo — native viewer controls
  ────────────────────────────────────────
  • Right panel → Control: drag actuator sliders to move the arm
  • Mouse: scroll=zoom · left-drag=orbit · right-drag=pan
  • Close the MuJoCo window to exit
  • Keyboard teleop disabled (avoids conflicts with MuJoCo shortcuts)

EOF
}

cameras_json() {
  printf '{front: {type: opencv, index_or_path: %s, width: %s, height: %s, fps: %s, fourcc: MJPG}}' \
    "$CAM_INDEX" "$CAM_WIDTH" "$CAM_HEIGHT" "$CAM_FPS"
}

# lerobot-record stamps repo_id with _YYYYMMDD_HHMMSS. Resolve that for replay/viz.
# Sets globals (call directly — do NOT use $(...) or RESOLVED_* is lost in a subshell):
#   RESOLVED_DATASET_REPO_ID  e.g. your_username/pick_place_sorting_YYYYMMDD_HHMMSS
#   RESOLVED_DATASET_ROOT     local folder, or empty if missing
resolve_dataset_repo_id() {
  local cache_home="${HF_LEROBOT_HOME:-$HOME/.cache/huggingface/lerobot}"
  local user_dir="$cache_home/$HF_USER"
  local exact="$user_dir/$DATASET_REPO"
  local latest=""

  RESOLVED_DATASET_REPO_ID="${HF_USER}/${DATASET_REPO}"
  RESOLVED_DATASET_ROOT=""

  if [[ -f "$exact/meta/info.json" ]]; then
    RESOLVED_DATASET_REPO_ID="${HF_USER}/${DATASET_REPO}"
    RESOLVED_DATASET_ROOT="$exact"
    return 0
  fi

  if [[ -d "$user_dir" ]]; then
    latest="$(
      find "$user_dir" -mindepth 1 -maxdepth 1 -type d -name "${DATASET_REPO}_*" \
        -exec test -f '{}/meta/info.json' \; -print 2>/dev/null \
        | sort -r | head -n 1
    )"
    if [[ -n "$latest" ]]; then
      RESOLVED_DATASET_REPO_ID="${HF_USER}/$(basename "$latest")"
      RESOLVED_DATASET_ROOT="$latest"
      return 0
    fi
  fi

  # Fall back: any user folder under LeRobot home (stamped names like pick_place_sorting_YYYYMMDD_HHMMSS).
  if [[ -d "$cache_home" ]]; then
    latest="$(
      find "$cache_home" -mindepth 2 -maxdepth 2 -type d \( -name "${DATASET_REPO}" -o -name "${DATASET_REPO}_*" \) \
        -exec test -f '{}/meta/info.json' \; -print 2>/dev/null \
        | sort -r | head -n 1
    )"
    if [[ -n "$latest" ]]; then
      RESOLVED_DATASET_REPO_ID="$(basename "$(dirname "$latest")")/$(basename "$latest")"
      RESOLVED_DATASET_ROOT="$latest"
      return 0
    fi
  fi

  return 0
}

show_header() {
  clear 2>/dev/null || true
  cat <<EOF
╔══════════════════════════════════════════════════════════════╗
║     SO-101 Pick & Place — CLI Menu (no LeLab)                ║
╚══════════════════════════════════════════════════════════════╝
  Repo:     $ROOT
  Leader:   $LEADER_PORT  ($LEADER_ID)
  Follower: $FOLLOWER_PORT  ($FOLLOWER_ID)
  HF user:  $HF_USER
  Dataset:  ${HF_USER}/${DATASET_REPO}
  Camera:   index=$CAM_INDEX  ${CAM_WIDTH}x${CAM_HEIGHT}@${CAM_FPS}
  Dry-run:  $DRY_RUN   Config: $CONFIG_FILE

EOF
}

show_menu() {
  cat <<'EOF'
  0) Find USB ports
  1) Find cameras (OpenCV)
  2) Install / sync deps (feetech + viz + dataset + hardware)
  3) Program motor ID (set_middle_positions) …
  4) Setup motors (lerobot-setup-motors) …
  5) Calibrate leader
  6) Calibrate follower
  7) Teleop (no camera)
  8) Teleop (USB camera + Rerun)
  9) Teleop sync help (Roadmap · Troubleshooting)
 10) Record demos (USB camera)
 11) Visualize dataset (all episodes — Rerun)
 12) Train ACT (cloud GPU — run where CUDA is available)
 13) Train Diffusion (cloud GPU)
 14) Rollout / evaluate policy
 15) Replay episode on follower
 16) MuJoCo — interactive viewer (Control sliders)
 17) MuJoCo — real leader → sim (3D viewer)
 18) Install MuJoCo extra
 19) HF auth login
 ──
  C) Configure ports / ids / HF user / camera
  D) Toggle dry-run (print commands only)
  S) Save config now
  Q) Quit

EOF
}

program_motor_id() {
  local arm port id
  echo "  Arm:  1) leader   2) follower"
  read -r -p "Choose arm [1]: " arm
  arm="${arm:-1}"
  if [[ "$arm" == "2" ]]; then
    port="$FOLLOWER_PORT"
  else
    port="$LEADER_PORT"
  fi
  read -r -p "Motor ID to program (1–6): " id
  if [[ -z "${id:-}" || ! "$id" =~ ^[1-6]$ ]]; then
    echo "Invalid ID."
    return 1
  fi
  echo "Connect ONLY motor that should become ID $id on $port"
  run uv run python set_middle_positions.py --port "$port" --id "$id"
}

setup_motors_menu() {
  local choice
  echo "  1) Leader (so101_leader)"
  echo "  2) Follower (so101_follower)"
  read -r -p "Choose [1]: " choice
  choice="${choice:-1}"
  if [[ "$choice" == "2" ]]; then
    run uv run lerobot-setup-motors \
      --robot.type=so101_follower \
      --robot.port="$FOLLOWER_PORT"
  else
    run uv run lerobot-setup-motors \
      --teleop.type=so101_leader \
      --teleop.port="$LEADER_PORT"
  fi
}

configure() {
  echo "── Configure (Enter keeps current) ──"
  prompt_default LEADER_PORT "Leader port" "$LEADER_PORT"
  prompt_default FOLLOWER_PORT "Follower port" "$FOLLOWER_PORT"
  prompt_default LEADER_ID "Leader id" "$LEADER_ID"
  prompt_default FOLLOWER_ID "Follower id" "$FOLLOWER_ID"
  prompt_default HF_USER "Hugging Face username" "$HF_USER"
  prompt_default DATASET_REPO "Dataset repo name (without user/)" "$DATASET_REPO"
  prompt_default EVAL_REPO "Eval repo name" "$EVAL_REPO"
  prompt_default TASK "Task string" "$TASK"
  prompt_default CAM_INDEX "Camera index" "$CAM_INDEX"
  prompt_default POLICY_PATH "Policy path" "$POLICY_PATH"
  prompt_default NUM_EPISODES "Record num episodes" "$NUM_EPISODES"
  prompt_default EVAL_EPISODES "Eval num episodes" "$EVAL_EPISODES"
  prompt_default EPISODE_TIME_S "Episode time (seconds)" "$EPISODE_TIME_S"
  prompt_default RESET_TIME_S "Reset time between episodes (seconds)" "$RESET_TIME_S"
  save_config
}

dispatch() {
  local choice="$1"
  local cams
  cams="$(cameras_json)"

  case "$choice" in
    0)
      run uv run lerobot-find-port
      ;;
    1)
      run uv run lerobot-find-cameras opencv
      ;;
    2)
      ensure_lerobot_extras "feetech,hardware,viz,dataset"
      ensure_overlay_plugins
      run uv run python --version
      ;;
    3)
      program_motor_id
      ;;
    4)
      setup_motors_menu
      ;;
    5)
      run uv run lerobot-calibrate \
        --teleop.type=so101_leader \
        --teleop.port="$LEADER_PORT" \
        --teleop.id="$LEADER_ID"
      ;;
    6)
      run uv run lerobot-calibrate \
        --robot.type=so101_follower \
        --robot.port="$FOLLOWER_PORT" \
        --robot.id="$FOLLOWER_ID"
      ;;
    7)
      run uv run lerobot-teleoperate \
        --robot.type=so101_follower \
        --robot.port="$FOLLOWER_PORT" \
        --robot.id="$FOLLOWER_ID" \
        --teleop.type=so101_leader \
        --teleop.port="$LEADER_PORT" \
        --teleop.id="$LEADER_ID"
      ;;
    8)
      local disp cams
      cams="$(cameras_json)"
      disp="$(display_flag)"
      run uv run lerobot-teleoperate \
        --robot.type=so101_follower \
        --robot.port="$FOLLOWER_PORT" \
        --robot.id="$FOLLOWER_ID" \
        --teleop.type=so101_leader \
        --teleop.port="$LEADER_PORT" \
        --teleop.id="$LEADER_ID" \
        --robot.cameras="$cams" \
        --display_data="$disp"
      ;;
    9)
      open_teleop_sync_help
      ;;
    10)
      local disp cams
      cams="$(cameras_json)"
      disp="$(display_flag)"
      run uv run lerobot-record \
        --robot.type=so101_follower \
        --robot.port="$FOLLOWER_PORT" \
        --robot.id="$FOLLOWER_ID" \
        --teleop.type=so101_leader \
        --teleop.port="$LEADER_PORT" \
        --teleop.id="$LEADER_ID" \
        --robot.cameras="$cams" \
        --dataset.repo_id="${HF_USER}/${DATASET_REPO}" \
        --dataset.num_episodes="$NUM_EPISODES" \
        --dataset.episode_time_s="$EPISODE_TIME_S" \
        --dataset.reset_time_s="$RESET_TIME_S" \
        --dataset.single_task="$TASK" \
        --display_data="$disp"
      ;;
    11)
      local ep
      local -a viz_args
      local viz_help=""
      local has_all_episodes=0
      resolve_dataset_repo_id
      echo "Using dataset: $RESOLVED_DATASET_REPO_ID"
      if [[ -n "${RESOLVED_DATASET_ROOT:-}" ]]; then
        echo "Local root:   $RESOLVED_DATASET_ROOT"
      else
        echo "Warning: no local dataset found for ${HF_USER}/${DATASET_REPO}*"
      fi
      # Stock LeRobot requires --episode-index. Optional patch 0004 adds --all-episodes.
      viz_help="$(uv run lerobot-dataset-viz --help 2>&1 || true)"
      if grep -q -- '--all-episodes' <<<"$viz_help"; then
        has_all_episodes=1
      fi
      if [[ "$has_all_episodes" == "1" ]]; then
        echo "Rerun: pick one episode, or 'all' for every episode on one timeline (patched LeRobot)."
        if [[ "${SO101_CLI_NONINTERACTIVE:-0}" == "1" ]]; then
          ep="${SO101_VIZ_EPISODE:-all}"
        else
          read -r -p "Episode index [all]: " ep
          ep="${ep:-all}"
        fi
      else
        echo "Rerun: one episode at a time (stock LeRobot — no --all-episodes)."
        if [[ "${SO101_CLI_NONINTERACTIVE:-0}" == "1" ]]; then
          ep="${SO101_VIZ_EPISODE:-0}"
        else
          read -r -p "Episode index [0]: " ep
          ep="${ep:-0}"
        fi
        if [[ "$ep" == "all" || "$ep" == "*" || "$ep" == "-1" ]]; then
          echo "Error: this LeRobot build has no --all-episodes."
          echo "Enter a numeric episode (e.g. 0), or apply patches/0004-dataset-viz-all-episodes.patch to ../lerobot."
          return 1
        fi
      fi
      viz_args=(uv run lerobot-dataset-viz --repo-id "$RESOLVED_DATASET_REPO_ID" --num-workers 0)
      if grep -q -- '--video-backend' <<<"$viz_help"; then
        viz_args+=(--video-backend pyav)
      fi
      if [[ -n "${RESOLVED_DATASET_ROOT:-}" ]]; then
        viz_args+=(--root "$RESOLVED_DATASET_ROOT")
      fi
      if [[ "$ep" == "all" || "$ep" == "*" || "$ep" == "-1" ]]; then
        viz_args+=(--all-episodes)
      else
        viz_args+=(--episode-index "$ep")
      fi
      run "${viz_args[@]}"
      ;;
    12)
      echo "Run this on a CUDA GPU host (not MacBook Air)."
      run uv run lerobot-train \
        --policy.type=act \
        --dataset.repo_id="${HF_USER}/${DATASET_REPO}" \
        --output_dir=outputs/train/sorting_act \
        --job_name=sorting_act \
        --policy.device=cuda
      ;;
    13)
      echo "Run this on a CUDA GPU host (not MacBook Air)."
      run uv run lerobot-train \
        --policy.type=diffusion \
        --dataset.repo_id="${HF_USER}/${DATASET_REPO}" \
        --output_dir=outputs/train/sorting_diffusion \
        --policy.device=cuda
      ;;
    14)
      local disp
      disp="$(display_flag)"
      run uv run lerobot-rollout \
        --robot.type=so101_follower \
        --robot.port="$FOLLOWER_PORT" \
        --robot.id="$FOLLOWER_ID" \
        --robot.cameras="$cams" \
        --policy.path="$POLICY_PATH" \
        --dataset.repo_id="${HF_USER}/${EVAL_REPO}" \
        --dataset.num_episodes="$EVAL_EPISODES" \
        --dataset.single_task="$TASK" \
        --strategy.num_episodes="$EVAL_EPISODES" \
        --display_data="$disp"
      ;;
    15)
      local ep
      local -a replay_args
      ensure_replay_deps
      resolve_dataset_repo_id
      echo "Using dataset: $RESOLVED_DATASET_REPO_ID"
      if [[ -n "${RESOLVED_DATASET_ROOT:-}" ]]; then
        echo "Local root:   $RESOLVED_DATASET_ROOT"
      else
        echo "Error: no local dataset found under $HF_LEROBOT_HOME for ${DATASET_REPO}*"
        echo "Set HF user with option C (this project: SUBHENDU), or record with option 10."
        return 1
      fi
      echo "Camera not required. Stop LeLab teleop/record first so the follower USB is free."
      echo "Replay is open-loop — clear the table or reset objects to this episode's start."
      if [[ "${SO101_CLI_NONINTERACTIVE:-0}" == "1" ]]; then
        ep="${2:-0}"
      else
        read -r -p "Episode index [0]: " ep
        ep="${ep:-0}"
      fi
      replay_args=(
        uv run lerobot-replay
        --robot.type=so101_follower
        --robot.port="$FOLLOWER_PORT"
        --robot.id="$FOLLOWER_ID"
        --dataset.repo_id="$RESOLVED_DATASET_REPO_ID"
        --dataset.root="$RESOLVED_DATASET_ROOT"
        --dataset.episode="$ep"
      )
      run "${replay_args[@]}"
      ;;
    16)
      ensure_mujoco_deps
      print_viewer_help
      run_mujoco_viewer
      ;;
    17)
      ensure_mujoco_deps
      echo "Physical leader drives the sim arm. Use MuJoCo mouse to view; close window when done."
      run_mujoco_teleoperate \
        --robot.type=so101_mujoco \
        --robot.id=sim_follower \
        --robot.show_viewer=true \
        --teleop.type=so101_leader \
        --teleop.port="$LEADER_PORT" \
        --teleop.id="$LEADER_ID" \
        --display_data=false
      ;;
    18)
      ensure_mujoco_deps
      ;;
    19)
      if command -v hf >/dev/null 2>&1; then
        run hf auth login
      else
        run uv run hf auth login
      fi
      ;;
    [cC])
      configure
      ;;
    [dD])
      if [[ "$DRY_RUN" == "1" ]]; then DRY_RUN=0; else DRY_RUN=1; fi
      echo "DRY_RUN=$DRY_RUN"
      sleep 1
      return 0
      ;;
    [sS])
      save_config
      ;;
    [qQ])
      echo "Bye."
      exit 0
      ;;
    *)
      echo "Unknown option: $choice"
      ;;
  esac
  pause
}

main() {
  need_uv
  load_config
  if [[ ! -f "$CONFIG_FILE" ]]; then
    save_config
  fi

  # Non-interactive: ./so101_cli_menu.sh <number>
  if [[ "${1:-}" != "" ]]; then
    SO101_CLI_NONINTERACTIVE=1
    dispatch "$1"
    exit 0
  fi

  while true; do
    show_header
    show_menu
    read -r -p "Select: " choice
    dispatch "$choice" || true
  done
}

main "$@"
