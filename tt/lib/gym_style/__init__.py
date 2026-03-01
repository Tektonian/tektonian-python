from __future__ import annotations
from typing import Any, Optional

from tt.lib.gym_style.gym_style_environment import GymStyleEnvironment
from tt.sdk import instantiate_service
from tt.sdk.environment_service.common.environment_service import (
    IEnvironmentManagementService,
)
from tt.sdk.runner_service.common.runner_service import IRunnerManagementService
from tt.sdk.simulation_service.common.simulation_service import (
    ISimulationManagementService,
)
from tt.sdk.world_service.common.world_service import IWorldManagementService


def init_bench(
    benchmark_id: str,
    env_id: str,
    seed: Optional[int] = 0,
    /,
    benchmark_specific: dict[str, Any] = {},
):
    """Initialize environment

    Args:
        env_uri (str): Environment URI could be .json file location, remote prebuilt environment uri
        sim_id (str): _description_
    """

    env = GymStyleEnvironment(
        instantiate_service,
        benchmark_id,
        env_id,
        seed,
        benchmark_specific=benchmark_specific,
    )

    return env
