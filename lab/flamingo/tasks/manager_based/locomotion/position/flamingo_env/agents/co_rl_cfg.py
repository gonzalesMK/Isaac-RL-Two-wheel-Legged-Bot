# Copyright (c) 2022-2024, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from isaaclab.utils import configclass

from scripts.co_rl.core.wrapper import (
    CoRlPolicyRunnerCfg,
    CoRlPpoActorCriticCfg,
    CoRlPpoAlgorithmCfg,
    CoRlSrmPpoAlgorithmCfg,
)

######################################## [ PPO CONFIG] ########################################


@configclass
class FlamingoPPORunnerCfg(CoRlPolicyRunnerCfg):
    num_steps_per_env = 24
    max_iterations = 1500
    save_interval = 100
    experiment_name = "FlamingoStand-v0"
    experiment_description = "test"
    empirical_normalization = False
    policy = CoRlPpoActorCriticCfg(
        init_noise_std=1.0,
        actor_hidden_dims=[512, 256, 128],
        critic_hidden_dims=[512, 256, 128],
        activation="elu",
    )
    algorithm = CoRlPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.01,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=1.0e-3,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
    )

@configclass
class FlamingoFlatPPORunnerCfg_Position(FlamingoPPORunnerCfg):
    def __post_init__(self):
        super().__post_init__()

        self.max_iterations = 10000
        self.experiment_name = "Flat_Position"
        self.policy.actor_hidden_dims = [512, 256, 128]
        self.policy.critic_hidden_dims = [512, 256, 128]


@configclass
class FlamingoRoughPPORunnerCfg_Position(FlamingoPPORunnerCfg):
    def __post_init__(self):
        super().__post_init__()

        self.max_iterations = 10000
        self.experiment_name = "Flamingo_Rough_Position"
        self.policy.actor_hidden_dims = [512, 256, 128]
        self.policy.critic_hidden_dims = [512, 256, 128]

###############################################################################################
######################################## [ SRMPPO CONFIG] ######################################
@configclass
class FlamingoSRMPPORunnerCfg(CoRlPolicyRunnerCfg):
    num_steps_per_env = 24
    max_iterations = 1500
    save_interval = 250
    experiment_name = "FlamingoStand-v0"
    experiment_description = "test"
    empirical_normalization = False
    policy = CoRlPpoActorCriticCfg(
        init_noise_std=1.0,
        actor_hidden_dims=[512, 256, 128],
        critic_hidden_dims=[512, 256, 128],
        activation="elu",
    )
    algorithm = CoRlSrmPpoAlgorithmCfg(
        value_loss_coef=1.0,
        use_clipped_value_loss=True,
        clip_param=0.2,
        entropy_coef=0.01,
        num_learning_epochs=5,
        num_mini_batches=4,
        learning_rate=1.0e-3,
        schedule="adaptive",
        gamma=0.99,
        lam=0.95,
        desired_kl=0.01,
        max_grad_norm=1.0,
        srm_net="gru",
        srm_input_dim=34,
        cmd_dim = 6,
        srm_hidden_dim=256,
        srm_output_dim=5,
        srm_num_layers=1,
        srm_r_loss_coef=1.0,
        srm_rc_loss_coef=1.0e-1,
        use_acaps=True,
        acaps_lambda_t_coef=1.0e-1,
        acaps_lambda_s_coef=1.0e-2,
    )