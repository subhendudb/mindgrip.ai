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

"""MuJoCo SO-101 simulated follower robot for LeRobot teleop / record."""

from __future__ import annotations

import logging
import math
from functools import cached_property
from pathlib import Path

import numpy as np

from lerobot.cameras import make_cameras_from_configs
from lerobot.types import RobotAction, RobotObservation
from lerobot.utils.decorators import check_if_already_connected, check_if_not_connected
from lerobot.robots.robot import Robot
from .config_so101_mujoco import SO101MujocoConfig

logger = logging.getLogger(__name__)

# Match SO-101 Feetech follower motor names / action keys
JOINT_NAMES = [
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_roll",
    "gripper",
]

# Gripper: LeRobot 0–100 → MuJoCo jaw hinge radians
# (TheRobotStudio SO101 so101_new_calib / IITD URDF joint 6)
GRIPPER_CLOSED_RAD = -0.17453297762778586
GRIPPER_OPEN_RAD = 1.7453291995659765


class SO101Mujoco(Robot):
    """Simulated SO-101 follower driven by MuJoCo position actuators."""

    config_class = SO101MujocoConfig
    name = "so101_mujoco"

    def __init__(self, config: SO101MujocoConfig):
        super().__init__(config)
        self.config = config
        self._model = None
        self._data = None
        self._renderer = None
        self._viewer = None
        self._connected = False
        self._joint_qpos_addrs: dict[str, int] = {}
        self._actuator_ids: dict[str, int] = {}
        self.cameras = make_cameras_from_configs(config.cameras)

    @property
    def _motors_ft(self) -> dict[str, type]:
        return {f"{name}.pos": float for name in JOINT_NAMES}

    @property
    def _cameras_ft(self) -> dict[str, tuple]:
        feats: dict[str, tuple] = {
            self.config.sim_camera_name: (self.config.image_height, self.config.image_width, 3)
        }
        for cam_name, cam_cfg in self.config.cameras.items():
            feats[cam_name] = (cam_cfg.height, cam_cfg.width, 3)
        return feats

    @cached_property
    def observation_features(self) -> dict[str, type | tuple]:
        return {**self._motors_ft, **self._cameras_ft}

    @cached_property
    def action_features(self) -> dict[str, type]:
        return dict(self._motors_ft)

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def is_calibrated(self) -> bool:
        return True

    def calibrate(self) -> None:
        # Simulation uses fixed MJCF joint ranges — nothing to calibrate.
        return

    def configure(self) -> None:
        return

    def _deg_to_ctrl(self, name: str, value: float) -> float:
        if name == "gripper":
            # 0 closed → 100 open (revolute jaw in accurate URDF scene)
            t = float(np.clip(value, 0.0, 100.0)) / 100.0
            return GRIPPER_CLOSED_RAD + t * (GRIPPER_OPEN_RAD - GRIPPER_CLOSED_RAD)
        if self.config.use_degrees:
            return math.radians(float(value))
        return float(value)

    def _qpos_to_lerobot(self, name: str, qpos: float) -> float:
        if name == "gripper":
            span = GRIPPER_OPEN_RAD - GRIPPER_CLOSED_RAD
            return float(np.clip((qpos - GRIPPER_CLOSED_RAD) / span * 100.0, 0.0, 100.0))
        if self.config.use_degrees:
            return math.degrees(float(qpos))
        return float(qpos)

    @check_if_already_connected
    def connect(self, calibrate: bool = True) -> None:  # noqa: ARG002
        try:
            import mujoco
        except ImportError as e:
            raise ImportError(
                "mujoco is required. Install with: pip install mujoco\n"
                "or: pip install -e 'packages/lerobot_robot_so101_mujoco'"
            ) from e

        mjcf = Path(self.config.mjcf_path).expanduser()
        if not mjcf.is_file():
            raise FileNotFoundError(
                f"MuJoCo MJCF not found: {mjcf}. Bundled scene should live at "
                f"{Path(__file__).parent / 'assets' / 'so101_scene.xml'}"
            )

        self._model = mujoco.MjModel.from_xml_path(str(mjcf))
        self._data = mujoco.MjData(self._model)

        for name in JOINT_NAMES:
            jid = mujoco.mj_name2id(self._model, mujoco.mjtObj.mjOBJ_JOINT, name)
            if jid < 0:
                raise ValueError(f"Joint '{name}' missing from MJCF {mjcf}")
            self._joint_qpos_addrs[name] = int(self._model.jnt_qposadr[jid])
            # Official SO-ARM100 MJCF names actuators after joints; older scenes used act_*.
            aid = mujoco.mj_name2id(self._model, mujoco.mjtObj.mjOBJ_ACTUATOR, name)
            if aid < 0:
                aid = mujoco.mj_name2id(self._model, mujoco.mjtObj.mjOBJ_ACTUATOR, f"act_{name}")
            if aid < 0:
                raise ValueError(f"Actuator '{name}' (or 'act_{name}') missing from MJCF {mjcf}")
            self._actuator_ids[name] = int(aid)

        self._renderer = mujoco.Renderer(
            self._model, height=self.config.image_height, width=self.config.image_width
        )

        # Apply home pose
        home_action = {f"{k}.pos": v for k, v in self.config.home_positions.items()}
        self._apply_action(home_action, reset_state=True)

        if self.config.show_viewer:
            try:
                import mujoco.viewer

                self._viewer = mujoco.viewer.launch_passive(
                    self._model,
                    self._data,
                    show_left_ui=True,
                    show_right_ui=True,
                )
                # Sensible default framing so the arm is visible (user can still orbit/zoom).
                self._viewer.cam.azimuth = 160.0
                self._viewer.cam.elevation = -20.0
                self._viewer.cam.distance = 1.1
                self._viewer.cam.lookat[:] = (0.12, 0.0, 0.18)
                self._viewer.sync()
            except Exception as e:
                logger.warning("Could not open MuJoCo viewer (%s). Continuing headless.", e)
                self._viewer = None

        for cam in self.cameras.values():
            cam.connect()

        self._connected = True
        logger.info("SO101 MuJoCo connected (%s)", mjcf)

    @check_if_not_connected
    def run_viewer_control_loop(self) -> None:
        """Step physics while the MuJoCo UI owns actuator controls (no keyboard teleop).

        Use the right-hand **Control** panel sliders to move joints. Mouse orbits the camera.
        Native MuJoCo keybindings are left untouched (no custom key overlay).
        """
        import time

        import mujoco

        if self._viewer is None:
            raise RuntimeError(
                "MuJoCo viewer is not open. Connect with show_viewer=True "
                "(e.g. ./so101_cli_menu.sh 15)."
            )

        print(
            "\n"
            "╔══════════════════════════════════════════════════════════════╗\n"
            "║  SO-101 MuJoCo — viewer controls (no keyboard teleop)        ║\n"
            "╠══════════════════════════════════════════════════════════════╣\n"
            "║  • Right panel → Control: drag actuator sliders to move arm  ║\n"
            "║  • Mouse: scroll=zoom · left-drag=orbit · right-drag=pan     ║\n"
            "║  • Close the MuJoCo window to exit                           ║\n"
            "╚══════════════════════════════════════════════════════════════╝\n",
            flush=True,
        )

        # UI writes data.ctrl; we only step + sync (do not overwrite actuators).
        while self._viewer.is_running():
            t0 = time.perf_counter()
            mujoco.mj_step(self._model, self._data)
            self._viewer.sync()
            # Pace roughly to model timestep so the UI stays responsive.
            dt = self._model.opt.timestep - (time.perf_counter() - t0)
            if dt > 0:
                time.sleep(dt)

    def _apply_action(self, action: RobotAction, reset_state: bool = False) -> None:
        import mujoco

        for name in JOINT_NAMES:
            key = f"{name}.pos"
            if key not in action:
                continue
            ctrl = self._deg_to_ctrl(name, float(action[key]))
            self._data.ctrl[self._actuator_ids[name]] = ctrl
            if reset_state:
                self._data.qpos[self._joint_qpos_addrs[name]] = ctrl

        if reset_state:
            mujoco.mj_forward(self._model, self._data)
        else:
            for _ in range(max(1, self.config.n_substeps)):
                mujoco.mj_step(self._model, self._data)

        if self._viewer is not None:
            self._viewer.sync()

    def _render_sim_camera(self) -> np.ndarray:
        import mujoco

        cam_name = self.config.sim_camera_name
        try:
            self._renderer.update_scene(self._data, camera=cam_name)
        except Exception:
            self._renderer.update_scene(self._data)
        rgb = self._renderer.render()
        return np.ascontiguousarray(rgb)

    @check_if_not_connected
    def get_observation(self) -> RobotObservation:
        obs: RobotObservation = {}
        for name in JOINT_NAMES:
            q = float(self._data.qpos[self._joint_qpos_addrs[name]])
            obs[f"{name}.pos"] = self._qpos_to_lerobot(name, q)

        obs[self.config.sim_camera_name] = self._render_sim_camera()

        for cam_key, cam in self.cameras.items():
            obs[cam_key] = cam.async_read()

        return obs

    @check_if_not_connected
    def send_action(self, action: RobotAction) -> RobotAction:
        merged: RobotAction = {}
        for name in JOINT_NAMES:
            key = f"{name}.pos"
            if key in action:
                merged[key] = float(action[key])
            else:
                q = float(self._data.qpos[self._joint_qpos_addrs[name]])
                merged[key] = self._qpos_to_lerobot(name, q)
        self._apply_action(merged, reset_state=False)
        return merged

    @check_if_not_connected
    def disconnect(self) -> None:
        if self._viewer is not None:
            try:
                self._viewer.close()
            except Exception:
                pass
            self._viewer = None
        for cam in self.cameras.values():
            cam.disconnect()
        self._renderer = None
        self._model = None
        self._data = None
        self._connected = False
        logger.info("SO101 MuJoCo disconnected")
