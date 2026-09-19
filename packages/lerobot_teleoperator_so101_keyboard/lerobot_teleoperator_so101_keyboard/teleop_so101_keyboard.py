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

"""Keyboard teleoperator emitting SO-101 joint `.pos` actions (optional / headless).

Prefer MuJoCo native viewer Control sliders for interactive sim
(``./so101_cli_menu.sh 16`` / ``python -m lerobot_robot_so101_mujoco.run_viewer``).
Keyboard teleop conflicts with MuJoCo's own keybindings when the 3D viewer is open.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from lerobot.lerobot_types import RobotAction
from lerobot.utils.decorators import check_if_already_connected, check_if_not_connected

from lerobot.teleoperators.keyboard.teleop_keyboard import KeyboardTeleop, PYNPUT_AVAILABLE, keyboard
from .config_so101_keyboard import SO101KeyboardTeleopConfig

logger = logging.getLogger(__name__)

JOINT_NAMES = [
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_roll",
    "gripper",
]

KEY_MAP: dict[str, tuple[str, float]] = {
    "q": ("shoulder_pan", -1.0),
    "w": ("shoulder_pan", +1.0),
    "a": ("shoulder_lift", -1.0),
    "s": ("shoulder_lift", +1.0),
    "z": ("elbow_flex", -1.0),
    "x": ("elbow_flex", +1.0),
    "e": ("wrist_flex", -1.0),
    "r": ("wrist_flex", +1.0),
    "d": ("wrist_roll", -1.0),
    "f": ("wrist_roll", +1.0),
    "c": ("gripper", -1.0),
    "v": ("gripper", +1.0),
}


class SO101KeyboardTeleop(KeyboardTeleop):
    """Incremental joint teleop (headless / no MuJoCo viewer)."""

    config_class = SO101KeyboardTeleopConfig
    name = "so101_keyboard"

    def __init__(self, config: SO101KeyboardTeleopConfig):
        super().__init__(config)
        self.config: SO101KeyboardTeleopConfig = config
        self._pose = {
            "shoulder_pan": 0.0,
            "shoulder_lift": 0.0,
            "elbow_flex": 0.0,
            "wrist_flex": 0.0,
            "wrist_roll": 0.0,
            "gripper": 50.0,
        }

    @property
    def action_features(self) -> dict:
        return {f"{name}.pos": float for name in JOINT_NAMES}

    @property
    def feedback_features(self) -> dict:
        return {}

    @property
    def is_calibrated(self) -> bool:
        return True

    def calibrate(self) -> None:
        return

    def _on_press(self, key):
        ch = getattr(key, "char", None)
        if isinstance(ch, str) and ch:
            self.event_queue.put((ch.lower(), True))
            return
        if PYNPUT_AVAILABLE and key == keyboard.Key.esc:
            self.event_queue.put((key, True))

    def _on_release(self, key):
        ch = getattr(key, "char", None)
        if isinstance(ch, str) and ch:
            self.event_queue.put((ch.lower(), False))
        if PYNPUT_AVAILABLE and key == keyboard.Key.esc:
            logger.info("ESC pressed, disconnecting.")
            self.disconnect()

    @check_if_already_connected
    def connect(self) -> None:
        super().connect()
        logger.info(
            "SO101 keyboard teleop (headless). For interactive sim with a 3D view, use "
            "MuJoCo Control sliders via: python -m lerobot_robot_so101_mujoco.run_viewer"
        )

    @check_if_not_connected
    def get_action(self) -> RobotAction:
        before = time.perf_counter()
        self._drain_pressed_keys()

        for key, pressed in list(self.current_pressed.items()):
            if not pressed or key not in KEY_MAP:
                continue
            joint, direction = KEY_MAP[key]
            if joint == "gripper":
                step = self.config.gripper_step * direction
                self._pose[joint] = float(max(0.0, min(100.0, self._pose[joint] + step)))
            else:
                step = self.config.step_deg * direction
                self._pose[joint] = float(
                    max(
                        self.config.joint_min_deg,
                        min(self.config.joint_max_deg, self._pose[joint] + step),
                    )
                )

        self.logs["read_pos_dt_s"] = time.perf_counter() - before
        return {f"{name}.pos": self._pose[name] for name in JOINT_NAMES}

    def send_feedback(self, feedback: dict[str, Any]) -> None:
        return
