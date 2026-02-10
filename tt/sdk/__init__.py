from tt.base.instantiate.extensions import (
    register_singleton,
    get_singleton_service_descriptors,
)
from tt.base.instantiate.service_collection import ServiceCollection
from tt.base.instantiate.instantiate_service import InstantiateService

from tt.sdk.simulation_service.common.simulation_service import (
    ISimulationManagementService,
)
from tt.sdk.simulation_service.remote.simulation_service import (
    SimulationManagementService,
)

from tt.sdk.simulation_service.remote.simulation_service import Environment

register_singleton(ISimulationManagementService, SimulationManagementService)


services = get_singleton_service_descriptors()
services = ServiceCollection(services)

instantiate_service = InstantiateService(services)

simulation_service: ISimulationManagementService = (
    instantiate_service.service_accessor.get(SimulationManagementService)
)

_simulation = simulation_service
