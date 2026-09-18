# SO-101 MuJoCo (LeRobot)

Simulate an SO-101 **follower** in MuJoCo for:

1. **Leader connected** — physical `so101_leader` drives the sim arm (`so101_mujoco`)
2. **No robot** — keyboard teleop (`so101_keyboard`) to practice and **record ML datasets** in sim

Full MindGrip guide: [Optional Tooling](./source/optional_tooling.html) (purpose · install · CLI 16–18 · future use cases).

## Install

From **so101-lab** root (after sibling `lerobot` is in the venv):

```bash
uv pip install -e packages/lerobot_robot_so101_mujoco
uv pip install -e packages/lerobot_teleoperator_so101_keyboard

# Or:
./so101_cli_menu.sh 18
```

LeRobot UX patches under `patches/` are **not** required for these plugins.

## Mode A — real leader → MuJoCo follower

```bash
./so101_cli_menu.sh 17
# or:
uv run lerobot-teleoperate \
  --robot.type=so101_mujoco \
  --robot.id=sim_follower \
  --robot.show_viewer=true \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodemXXXX \
  --teleop.id=LeoArm \
  --display_data=true
```

Record demos the same way with `lerobot-record` (same `--robot` / `--teleop` flags).

## Mode B — keyboard → MuJoCo (no hardware)

```bash
uv run lerobot-teleoperate \
  --robot.type=so101_mujoco \
  --robot.id=sim_follower \
  --teleop.type=so101_keyboard \
  --display_data=true
```

### Interactive viewer (recommended)

Use MuJoCo’s native **Control** sliders (no keyboard teleop — avoids conflicting with viewer shortcuts):

```bash
./so101_cli_menu.sh 16
# or: mjpython -m lerobot_robot_so101_mujoco.run_viewer
```

### Keyboard map (optional, headless only)

| Keys | Joint |
|------|--------|
| `q` / `w` | shoulder_pan |
| `a` / `s` | shoulder_lift |
| `z` / `x` | elbow_flex |
| `e` / `r` | wrist_flex |
| `d` / `f` | wrist_roll |
| `c` / `v` | gripper close / open |
| `ESC` | disconnect |

Prefer the viewer Control panel when the 3D window is open.

## Record a sim dataset for training

```bash
uv run lerobot-record \
  --robot.type=so101_mujoco \
  --robot.id=sim_follower \
  --teleop.type=so101_keyboard \
  --dataset.repo_id=${HF_USER}/so101_mujoco_sorting \
  --dataset.num_episodes=20 \
  --dataset.single_task="Pick coloured block and place in matching bin" \
  --dataset.episode_time_s=30 \
  --display_data=true
```

Then train as usual, e.g. ACT:

```bash
uv run lerobot-train \
  --policy.type=act \
  --dataset.repo_id=${HF_USER}/so101_mujoco_sorting \
  --output_dir=outputs/train/sorting_act_sim
```

> **Sim-to-real:** even with accurate CAD meshes, policies trained only in sim will **not** transfer cleanly to the physical SO-101 + USB cam without domain randomization / fine-tuning on real demos. Use sim for pipeline practice and algorithm tests; use real arms for the sorting project.

## Model assets

Default scene is under `packages/lerobot_robot_so101_mujoco/.../assets/so101_scene.xml` — the **official MuJoCo SO-101** from [TheRobotStudio/SO-ARM100 `Simulation/SO101`](https://github.com/TheRobotStudio/SO-ARM100/tree/main/Simulation/SO101) (`so101_new_calib` — joint zero at mid-range, STS3215 motor params).

`IITD_EPR_KIT4-main` uses the **same CAD** as URDF only (no MJCF). A copy of the IITD base xacro is kept under `assets/reference_iitd_urdf/` for comparison — this overlay does **not** install or run a ROS stack.

Joint names already match Feetech / LeRobot. Gripper is a revolute jaw mapped from LeRobot 0–100.

Override with:

```bash
--robot.mjcf_path=/path/to/other/scene.xml
```

## Notes

- On macOS, interactive MuJoCo viewers often need `mjpython` instead of `python` for `show_viewer=true` (CLI 16/17 handle this).
- Headless recording works without a viewer (`show_viewer=false`, default).
- Simulated camera key is `front` (640×480) to mirror the project USB overview cam.
