# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Sub-module containing command generators for the velocity-based locomotion task."""

from __future__ import annotations
import torch
import isaaclab.sim as sim_utils
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR

from isaaclab.managers import CommandTerm , CommandTermCfg
from isaaclab.assets import Articulation

from isaaclab.markers import VisualizationMarkersCfg , VisualizationMarkers
from isaaclab.markers.config import CUBOID_MARKER_CFG,  BLUE_ARROW_X_MARKER_CFG

from isaaclab.utils import configclass



from collections.abc import Sequence

from dataclasses import MISSING

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedEnv


class EventCommand(CommandTerm):
    """Command generator that generates a event flag.

    The command comprises of True of False.

    """
    cfg : EventCommandCfg
    
    def __init__(self, cfg : EventCommandCfg, env : ManagerBasedEnv):
        """Initialize the command generator.

        Args:
            cfg: The configuration of the command generator.
            env: The environment.
        """
        super().__init__(cfg,env)
        
        self.env = env
        
        self.robot: Articulation = env.scene[cfg.asset_name]
        
        self.time_elapsed = torch.zeros(self.num_envs, device=self.device)
        
        self.event_command = torch.zeros(self.num_envs,2, dtype=torch.float32, device=self.device)
        
        self.event_during_time = cfg.event_during_time
        
        
    def __str__(self) -> str:
        """Return a string representation of the command generator."""
        msg = "EventCommand:\n"
        msg += f"\tStanding probability: {self.cfg.rel_standing_envs}"
        return msg

    @property
    def command(self) -> torch.Tensor:
        """The event command. Shape is (num_envs)."""
        return self.event_command
    
    def _update_metrics(self):
        # time for which the command was executed
        max_command_time = self.cfg.resampling_time_range[1]
        max_command_step = max_command_time / self._env.step_dt

    def _resample_command(self, env_ids: Sequence[int]):


        #r = torch.zeros(len(env_ids), device=self.device)
        # command of event
        current_time = self.env.episode_length_buf * self.env.physics_dt * 4

        self.event_command[env_ids, 0] = torch.where(
                                                        current_time[env_ids] >= 2.0,
                                                        torch.ones_like(self.event_command[env_ids, 0], dtype=torch.float32, device=self.device),
                                                        torch.zeros_like(self.event_command[env_ids, 0], dtype=torch.float32, device=self.device)
        )

        self.time_elapsed[env_ids] = torch.zeros(len(env_ids), dtype=torch.float32, device=self.device)
        #print('==============Resample===============')
        # print(env_ids)
        # randomly stand command
        #self.event_command[env_ids] = (r.uniform_(0.0, 1.0) <= self.cfg.rel_standing_envs).int()

    def _update_command(self):
        """
        Update the event command.

        - When command is active (event_command[:, 0] == 1.0), increase time_elapsed by dt.
        - If time_elapsed > event_during_time, deactivate the command and reset the timer.
        - If environment is reset, reset both the timer and command values.
        """
        
        self.time_elapsed = torch.where(self.event_command[:,0]==1.0,
                                        self.time_elapsed + self._env.step_dt,
                                        0.0)
        self.event_command[:, 0] = torch.logical_and(self.event_command[:,0]==1.0 , self.time_elapsed <= self.event_during_time).float()
        self.event_command[:,1] = self.time_elapsed

        reset_env_ids = self._env.reset_buf.nonzero(as_tuple=False).flatten()
        if len(reset_env_ids) > 0:
            self.time_elapsed[reset_env_ids] = 0.0
            self.event_command[reset_env_ids] = 0.0

    def _set_debug_vis_impl(self, debug_vis: bool):
            if debug_vis:
            # create markers if necessary for the first tomes
                if not hasattr(self, "command_active_visualizer") or not hasattr(self, "command_inactive_visualizer"):
                    self.command_active_visualizer = VisualizationMarkers(self.cfg.command_active_visualizer_cfg)
                    self.command_inactive_visualizer = VisualizationMarkers(self.cfg.command_inactive_visualizer_cfg)
                self.command_active_visualizer.set_visibility(True)
                self.command_inactive_visualizer.set_visibility(True)
            else:
                if hasattr(self, "command_active_visualizer"):
                    self.command_active_visualizer.set_visibility(False)
                if hasattr(self, "command_inactive_visualizer"):
                    self.command_inactive_visualizer.set_visibility(False)
                
    def _debug_vis_callback(self, event):
        # Check if robot is initialized
        if not self.robot.is_initialized:
            return

        # Clone base positions and raise them slightly for visualization
        base_pos_w = self.robot.data.root_pos_w.clone()
        base_pos_w[:, 2] += 0.65

        # Get indices where event_command command is active
        active_indices = (self.event_command[:, 0] == 1.0).nonzero(as_tuple=True)[0]
        inactive_indices = (self.event_command[:, 0] == 0.0).nonzero(as_tuple=True)[0]

        # Visualize only for active indices
        if active_indices.numel() > 0:
            self.command_active_visualizer.visualize(base_pos_w[active_indices])
        if inactive_indices.numel() > 0:
            self.command_inactive_visualizer.visualize(base_pos_w[inactive_indices])


GREEN_CUBOID_MARKER_CFG = VisualizationMarkersCfg(
    prim_path="/Visuals/Command/event_command",
    markers={
        "cuboid": sim_utils.SphereCfg(
            radius=0.075,
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.0, 1.0, 0.0)),
        ),
    }
)

RED_CUBOID_MARKER_CFG = VisualizationMarkersCfg(
    prim_path="/Visuals/Command/event_command",
    markers={
        "cuboid": sim_utils.SphereCfg(
            radius=0.075,
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(1.0, 0.0, 0.0)),
        ),
    }
)


@configclass
class EventCommandCfg(CommandTermCfg):
    
    class_type : type = EventCommand
    
    asset_name : str = MISSING

    event_during_time: float = 1.0
    
    command_active_visualizer_cfg : VisualizationMarkersCfg = GREEN_CUBOID_MARKER_CFG
    command_inactive_visualizer_cfg : VisualizationMarkersCfg = RED_CUBOID_MARKER_CFG

    """The sampled probability of environments that should be standing still. Defaults to 0.0."""

    """The sampled probability of environments where the robots should do event
    (the others follow the sampled angular velocity command). Defaults to 1.0."""