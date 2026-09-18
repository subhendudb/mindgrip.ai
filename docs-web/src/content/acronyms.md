# Acronyms & short names

Glossary for **MindGrip AI** / **so101-lab** and the SO-101 pick-and-place sorting path. Use this when you see short forms like **HF**, **ACT**, **FK**, or **VLA** without expansion.

> Tip: keep this open beside the [project page](./project_page) or [roadmap](./roadmap).

## How to use this page

| Column | Meaning |
| --- | --- |
| **Acronym** | Short form as written in the docs |
| **Stands for / full name** | Expanded meaning |
| **In this lab** | Why it matters for MindGrip / so101-lab |

---

## Platforms, products & this repo

| Acronym | Stands for / full name | In this lab |
| --- | --- | --- |
| **MindGrip AI** | MindGrip AI (project brand) | Cognitive targeting / handling narrative for the binary sorter lab. |
| **so101-lab** | This overlay repository | Plugins, CLI menu, patches, and docs — sits beside vanilla `lerobot/`, not a fork of it. |
| **HF** | Hugging Face | Hosts models, datasets, Spaces, and **HF Jobs** (cloud GPUs). |
| **Hub** | Hugging Face Hub | Where you push datasets and publish / pull policies (e.g. `SUBHENDU/…`). |
| **HF Jobs** | Hugging Face Jobs | Managed cloud GPU training — preferred for Step 8 from LeLab (`a10g-small` / `a10g-large`). |
| **LeRobot** | LeRobot (Hugging Face robotics library) | Core framework: teleop, datasets, train, rollout. Upstream docs: [huggingface.co/docs/lerobot](https://huggingface.co/docs/lerobot). |
| **LeLab** | LeRobot Lab (GUI) | Recommended GUI for calibrate → teleop → record → train → deploy on a laptop/desktop. |
| **CLI** | Command-Line Interface | Terminal path: `./so101_cli_menu.sh` and `uv run lerobot-*`. |
| **GUI** | Graphical User Interface | LeLab (and Rerun) instead of long flags. |
| **uv** | uv (Astral package / project manager) | Installs deps and runs tools (`uv run …`, `uv sync`). |
| **TTY** | Teletype / terminal device | Interactive stdin used by recording key patches on macOS. |
| **JSON** | JavaScript Object Notation | Calibration files — this lab: `LeoArm.json` under `so_leader/` and `so_follower/`. |
| **ENV** | Environment / config file | `.so101_cli.env` — ports, ids, camera, `TASK`, dataset (menu **C**). |
| **MJPG** | Motion JPEG | Preferred USB camera `fourcc` for stable capture. |

---

## Hardware & robotics

| Acronym | Stands for / full name | In this lab |
| --- | --- | --- |
| **SO-101** / **SO-ARM101** | Standard Open Arm 101 | Leader + follower dual-arm kit for teleop and sorting. |
| **SO-100** | Standard Open Arm 100 | Earlier related arm; mentioned next to SO-101 in some upstream docs. |
| **DOF** | Degrees Of Freedom | SO-101 is **6-DOF** (six actuated joints including gripper). |
| **STS3215** | Feetech STS3215 servo | Smart servo on the arms (bus IDs 1–6 per arm). |
| **TTL** | Transistor–Transistor Logic (serial bus) | Feetech motor bus (~1 Mbps). |
| **USB** | Universal Serial Bus | Arm adapters (`/dev/tty.usbmodem…` on macOS) and the policy webcam. |
| **PSU** | Power Supply Unit | External **5 V** (leader) and **12 V** (follower) — USB alone is not enough. |
| **ID** | Identifier | Motor bus ID (1–6) and robot/teleop id — this lab uses **`LeoArm`** for both arms. |
| **J1–J6** | Joint 1 through Joint 6 | Pan, lift, elbow, wrist flex, wrist roll, gripper. |
| **EE** | End-Effector | Gripper / tip frame that picks objects. |
| **FK** | Forward Kinematics | Gripper pose from joint angles. See [FK & IK](./so101_kinematics). |
| **IK** | Inverse Kinematics | Joint angles from a desired pose (Jacobian / DLS demos on the kinematics page). |
| **DH** | Denavit–Hartenberg | Classic link parameters used when writing each joint’s 4×4 transform. |
| **L<sub>max</sub>** | Maximum reach length | ≈ **38 cm** for SO-101 — size the sorting mat inside this arc. |
| **URDF** | Unified Robot Description Format | Robot model for sim / kinematics helpers. |
| **MJCF** | MuJoCo XML model format | Used by the optional `so101_mujoco` plugin. |
| **ROS2** | Robot Operating System 2 | Classical robotics middleware — **not** part of this overlay’s install or CLI. |
| **RViz** | ROS Visualization | ROS 3D viewer — **not** shipped or documented as a MindGrip path. |

---

## Vision, sensing & control

| Acronym | Stands for / full name | In this lab |
| --- | --- | --- |
| **OpenCV** | Open Source Computer Vision Library | Backend for the USB cam (`type: opencv`). |
| **FPS** | Frames Per Second | Policy cam: **640×480 @ 30 FPS**, name **`front`**. |
| **Hz** | Hertz | Control / teleop loop rate (often ~30–60 Hz). |
| **Mbps** | Megabits per second | Motor bus baud (~1 Mbps). |
| **Rerun** | Rerun (visualization SDK) | Live camera + joint plots when `--display_data=true` / CLI viz. |
| **OBS** | Open Broadcaster Software | Virtual camera path covered by an optional patch. |

---

## Learning, policies & ML

| Acronym | Stands for / full name | In this lab |
| --- | --- | --- |
| **IL** | Imitation Learning | Learn from teleop demos (not hand-coded pick scripts). |
| **BC** | Behaviour Cloning | Map observations → actions from demos. |
| **ML** | Machine Learning | Training the neural policy (Step 8). |
| **Policy** | Control policy (neural net) | Maps camera + joints → motor commands. |
| **ACT** | Action Chunking Transformer | **Recommended** first policy for this sorter. |
| **Diffusion** | Diffusion Policy | Smoother multi-modal actions; heavier than ACT. |
| **VLA** | Vision–Language–Action | Policies that take images + language (SmolVLA, Pi-0, …). |
| **SmolVLA** | Small VLA (LeRobot) | Advanced option; train on cloud GPUs only. |
| **Pi-0** / **π₀** | Physical Intelligence π₀ | Large flow-matching VLA — cloud / big GPU. |
| **DiT** | Diffusion Transformer | Backbone used in some multitask policies. |
| **RL** | Reinforcement Learning | Reward/trial-and-error — separate from this IL path. |
| **OOM** | Out Of Memory | Risk when training large policies on 8–16 GB hosts. |
| **VRAM** | GPU memory | On NVIDIA cloud cards; Apple Silicon uses **unified** memory. |

---

## Compute & hosts

| Acronym | Stands for / full name | In this lab |
| --- | --- | --- |
| **CPU** | Central Processing Unit | Teleop, record, light inference on laptop/desktop or Pi. |
| **GPU** | Graphics Processing Unit | Prefer **cloud NVIDIA** for ACT training (HF Jobs / AWS). |
| **MPS** | Metal Performance Shaders | Apple Silicon PyTorch backend — tiny local experiments only. |
| **CUDA** | NVIDIA GPU compute API | Required for serious `lerobot-train` (CLI · 12 / 13). |
| **Pi** | Raspberry Pi | Valid control host for teleop/record/rollout — not for comfortable local training. |
| **SSD** | Solid-State Drive | Keep free space for demos and checkpoints. |
| **GB** | Gigabyte | Host RAM guidance: **8–16 GB** laptop/desktop class. |

---

## Quick “say it out loud” cheat sheet

| You see… | Read it as… |
| --- | --- |
| HF Jobs | Hugging Face Jobs |
| ACT | Action Chunking Transformer |
| FK / IK | Forward / Inverse Kinematics |
| L<sub>max</sub> | Max reach (~38 cm) |
| VLA | Vision–Language–Action |
| DOF | Degrees of Freedom |
| CLI / GUI | Command-line / graphical interface |
| PSU | Power supply unit |
| IL | Imitation learning |
| LeoArm | Calibration / robot id for both arms in this lab |

---

## Related pages

- [MindGrip AI Home](./mindgrip) — what this overlay is for
- [Pick & Place Sorting](./project_page) — project overview
- [Roadmap](./roadmap) — 9-step build path
- [LeLab](./lelab) · [CLI menu](./cli_menu) — GUI vs terminal
- [Forward & Inverse Kinematics](./so101_kinematics) — FK / IK / L<sub>max</sub>
- [Policy Cheatsheet](./policy_cheatsheet) — ACT vs Diffusion / VLA
- [Directory Structure](./directory_structure) — so101-lab layout
