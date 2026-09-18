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

"""Interactive SO-101 MuJoCo viewer driven by native UI controls (no keyboard teleop).

Run under mjpython on macOS:

    mjpython -m lerobot_robot_so101_mujoco.run_viewer
"""

from __future__ import annotations

from lerobot_robot_so101_mujoco.config_so101_mujoco import SO101MujocoConfig
from lerobot_robot_so101_mujoco.so101_mujoco import SO101Mujoco


def main() -> None:
    robot = SO101Mujoco(SO101MujocoConfig(show_viewer=True, id="sim_follower"))
    robot.connect()
    try:
        robot.run_viewer_control_loop()
    finally:
        robot.disconnect()


if __name__ == "__main__":
    main()
