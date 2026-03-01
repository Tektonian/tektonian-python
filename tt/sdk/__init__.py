from typing import Any

from tt.base.instantiate.extensions import (
    register_singleton,
    get_singleton_service_descriptors,
)
from tt.base.instantiate.service_collection import ServiceCollection
from tt.base.instantiate.instantiate_service import InstantiateService
from tt.sdk.environment_service.common.environment_service import (
    EnvironmentManagementService,
    IEnvironmentManagementService,
)
from tt.sdk.log_service.common.log_service import ILogService, LogService
from tt.sdk.runner_service.common.runner_service import (
    IRunnerManagementService,
    RunnerManagementService,
)
from tt.sdk.simulation_service.common.simulation_service import (
    ISimulationManagementService,
    SimulationManagementService,
)
from tt.sdk.world_service.common.world_service import (
    IWorldManagementService,
    WorldManagementService,
)

register_singleton(ILogService, LogService)
register_singleton(ISimulationManagementService, SimulationManagementService)
register_singleton(IRunnerManagementService, RunnerManagementService)
register_singleton(IWorldManagementService, WorldManagementService)
register_singleton(IEnvironmentManagementService, EnvironmentManagementService)


services = get_singleton_service_descriptors()
services = ServiceCollection(services)

instantiate_service = InstantiateService(services)

simulation_service: ISimulationManagementService = (
    instantiate_service.service_accessor.get(SimulationManagementService)
)
