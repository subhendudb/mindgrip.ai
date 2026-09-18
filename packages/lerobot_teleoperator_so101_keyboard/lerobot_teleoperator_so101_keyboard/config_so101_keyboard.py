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

from dataclasses import dataclass

from lerobot.teleoperators.config import TeleoperatorConfig


@TeleoperatorConfig.register_subclass("so101_keyboard")
@dataclass
class SO101KeyboardTeleopConfig(TeleoperatorConfig):
    """Keyboard joint teleop for SO-101 MuJoCo (sim-only dataset collection)."""

    # Degrees (or gripper units) applied per control tick while a key is held
    step_deg: float = 2.0
    gripper_step: float = 5.0

    # Clamp arm joints (degrees)
    joint_min_deg: float = -100.0
    joint_max_deg: float = 100.0
