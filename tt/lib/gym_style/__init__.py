from __future__ import annotations
from typing import TYPE_CHECKING, Any
from tt.sdk import instantiate_service

if TYPE_CHECKING:
    from tt.sdk import (
        IWorldManagementService,
        ISimulationManagementService,
        IEnvironmentManagementService,
        IRunnerManagementService,
    )


def init_env(
    env_uri: str, sim_id: str, seed: int | None = 0, /, **env_specific: dict[str, Any]
):
    """Initialize environment

    Args:
        env_uri (str): Environment URI could be .json file location, remote prebuilt environment uri
        sim_id (str): _description_
    """
    world_service: IWorldManagementService = instantiate_service.service_accessor.get(
        IWorldManagementService
    )
    print("world_service", world_service)

    simulation_service: ISimulationManagementService = (
        instantiate_service.service_accessor.get(ISimulationManagementService)
    )
    env_service: IEnvironmentManagementService = (
        instantiate_service.service_accessor.get(IEnvironmentManagementService)
    )
    print(instantiate_service._services._entries)
    print(env_service)
    print(simulation_service)

    runner_service: IRunnerManagementService = instantiate_service.service_accessor.get(
        IRunnerManagementService
    )

    env_ret = env_service.create_environment(
        "http://0.0.0.0", "http://0.0.0.0", "http://0.0.0.0", 0
    )

    if env_ret[0] is not None:
        runner_ret = runner_service.create_runner(env_ret[0].id)
        print(env_ret, runner_ret)

    print(env_ret)

    return env_ret[0]
