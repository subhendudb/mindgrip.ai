#!/usr/bin/env python

# Copyright 2026 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass, field
from pathlib import Path

from lerobot.cameras import CameraConfig
from lerobot.robots.config import RobotConfig

DEFAULT_MJCF = Path(__file__).resolve().parent / "assets" / "so101_scene.xml"


@RobotConfig.register_subclass("so101_mujoco")
@dataclass
class SO101MujocoConfig(RobotConfig):
    """MuJoCo SO-101 simulated follower for teleop and dataset recording."""

    # Path to MJCF. Default: bundled TheRobotStudio SO101 MuJoCo scene.
    mjcf_path: str = str(DEFAULT_MJCF)

    # Physics substeps per send_action call
    n_substeps: int = 25

    # Render resolution for the simulated "front" camera (and any named cameras)
    image_width: int = 640
    image_height: int = 480

    # Always publish a rendered overview camera under this key (LeRobot image feature)
    sim_camera_name: str = "front"

    # Optional extra real cameras (USB) — usually empty for pure sim datasets
    cameras: dict[str, CameraConfig] = field(default_factory=dict)

    # Match SO-101 follower convention (degrees for arm joints)
    use_degrees: bool = True

    # Show an interactive MuJoCo viewer window (requires display; use mjpython on macOS)
    show_viewer: bool = False

    # Home pose (degrees / gripper 0–100) applied on connect
    home_positions: dict[str, float] = field(
        default_factory=lambda: {
            "shoulder_pan": 0.0,
            "shoulder_lift": 0.0,
            "elbow_flex": 0.0,
            "wrist_flex": 0.0,
            "wrist_roll": 0.0,
            "gripper": 50.0,
        }
    )
