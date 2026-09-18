#!/usr/bin/env bash
# Point LeRobot + LeLab at a permanent folder (not ~/.cache, which gets wiped).
#
# Usage:
#   ./scripts/setup_lerobot_home.sh
#
# Creates:  ~/Documents/lerobot
# Symlink:  ~/.cache/huggingface/lerobot  →  that folder
#   (LeLab hardcodes the cache path; the symlink is what keeps LeLab in sync.)
#
# Also adds HF_LEROBOT_HOME to ~/.zshrc if it is not already there.

set -euo pipefail

PERMANENT="${HF_LEROBOT_HOME:-$HOME/Documents/lerobot}"
CACHE_PARENT="$HOME/.cache/huggingface"
CACHE_LINK="$CACHE_PARENT/lerobot"
ZSHRC="${ZDOTDIR:-$HOME}/.zshrc"

mkdir -p \
  "$PERMANENT/calibration/teleoperators/so_leader" \
  "$PERMANENT/calibration/robots/so_follower" \
  "$PERMANENT/robots" \
  "$PERMANENT/ports" \
  "$PERMANENT/saved_configs" \
  "$PERMANENT/outputs"

# Move any leftover cache contents into the permanent folder, then replace
# the cache path with a symlink so LeLab (hardcoded) and CLI (env) share one tree.
mkdir -p "$CACHE_PARENT"

if [[ -L "$CACHE_LINK" ]]; then
  current="$(readlink "$CACHE_LINK")"
  if [[ "$current" == "$PERMANENT" ]]; then
    echo "Symlink already correct: $CACHE_LINK → $PERMANENT"
  else
    echo "Updating symlink $CACHE_LINK (was → $current)"
    rm "$CACHE_LINK"
    ln -s "$PERMANENT" "$CACHE_LINK"
  fi
elif [[ -d "$CACHE_LINK" ]]; then
  echo "Moving existing cache files into $PERMANENT …"
  rsync -a "$CACHE_LINK/" "$PERMANENT/"
  rm -rf "$CACHE_LINK"
  ln -s "$PERMANENT" "$CACHE_LINK"
  echo "Replaced $CACHE_LINK with symlink → $PERMANENT"
elif [[ -e "$CACHE_LINK" ]]; then
  echo "Error: $CACHE_LINK exists and is not a directory or symlink."
  exit 1
else
  ln -s "$PERMANENT" "$CACHE_LINK"
  echo "Created $CACHE_LINK → $PERMANENT"
fi

MARKER_START="# >>> lerobot home (permanent, not cache)"
MARKER_END="# <<< lerobot home"
BLOCK=$(cat <<EOF
$MARKER_START
export HF_LEROBOT_HOME="$PERMANENT"
export HF_LEROBOT_CALIBRATION="\$HF_LEROBOT_HOME/calibration"
$MARKER_END
EOF
)

if [[ -f "$ZSHRC" ]] && grep -q "HF_LEROBOT_HOME" "$ZSHRC"; then
  echo "HF_LEROBOT_HOME already mentioned in $ZSHRC — left as-is."
else
  printf '\n%s\n' "$BLOCK" >> "$ZSHRC"
  echo "Added HF_LEROBOT_HOME to $ZSHRC"
fi

echo
echo "Permanent home: $PERMANENT"
echo "  calibration/teleoperators/so_leader/   ← leader JSON (LeoArm.json)"
echo "  calibration/robots/so_follower/        ← follower JSON"
echo "  robots/                                ← LeLab robot records"
echo "  datasets land under \$HF_LEROBOT_HOME/<hf_user>/"
echo
echo "Open a new terminal (or: source $ZSHRC) before running lelab or lerobot-calibrate."
