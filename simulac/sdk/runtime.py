import sys

from simulac.base.envvar.envvar import IEnvvarService
from simulac.sdk.environment_service.common.environment_build_service import (
    IEnvironmentBuildService,
)
from simulac.sdk.environment_service.common.environment_service import (
    IEnvironmentManagementService,
)
from simulac.sdk.log_service.common.log_service import ILogService
from simulac.sdk.runner_service.common.runner_service import IRunnerManagementService
from simulac.sdk.telemetry_service.common.telemetry_service import ITelemetryService

from .main import instantiate_service
from .world_maker import WorldMakerFacade


class SimulacRuntime:
    def __init__(self):
        old_exception_hook = sys.excepthook
        old_display_hook = sys.displayhook
        old_unraisable_hook = sys.unraisablehook

        flags = sys.flags

        debug = flags.debug
        dev_mode = flags.dev_mode
        verbose = flags.verbose
        quite = flags.quiet

        self._runner_management_service: IRunnerManagementService = (
            instantiate_service.service_accessor.get(IRunnerManagementService)
        )

        self._log_service: ILogService = instantiate_service.service_accessor.get(
            ILogService
        )
        self._environment_management_service: IEnvironmentManagementService = (
            instantiate_service.service_accessor.get(IEnvironmentManagementService)
        )
        self._environment_build_service: IEnvironmentBuildService = (
            instantiate_service.service_accessor.get(IEnvironmentBuildService)
        )
        self._envvar_service: IEnvvarService = instantiate_service.service_accessor.get(
            IEnvvarService
        )

        self._telemetry_service: ITelemetryService = (
            instantiate_service.service_accessor.get(ITelemetryService)
        )

        self._world_maker: WorldMakerFacade = instantiate_service.create_instance(
            WorldMakerFacade
        )

    @property
    def world_maker(self):
        """Return world maker facade"""
        return self._world_maker

    @property
    def logger(self) -> ILogService:
        """Return logger facade"""
        return self._log_service

    @property
    def environment_variable(self) -> IEnvvarService:
        """Return environment variable facade"""
        return self._envvar_service

    @property
    def telemetry(self) -> ITelemetryService:
        """Return telemetry variable facade"""
        return self._telemetry_service


_SINGLETON_SIMULATION_OBJECT_CACHE: SimulacRuntime | None = None


def obtain_runtime() -> SimulacRuntime:
    global _SINGLETON_SIMULATION_OBJECT_CACHE
    if _SINGLETON_SIMULATION_OBJECT_CACHE:
        return _SINGLETON_SIMULATION_OBJECT_CACHE
    else:
        _SINGLETON_SIMULATION_OBJECT_CACHE = SimulacRuntime()
        return _SINGLETON_SIMULATION_OBJECT_CACHE
