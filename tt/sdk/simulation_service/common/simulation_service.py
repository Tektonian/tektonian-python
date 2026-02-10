from abc import ABC, abstractmethod
from typing import Mapping, Union, Tuple
from dataclasses import dataclass

from tt.base.result.result import ResultType
from tt.base.instantiate.instantiate import service_identifier, ServiceIdentifier


class IEnvironment(ABC):

    @property
    @abstractmethod
    def uuid(self) -> str | None:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def compatibility_date(self) -> str:
        pass

    @property
    @abstractmethod
    def observation(self) -> object:
        pass

    @property
    @abstractmethod
    def step_num(self) -> int:
        pass

    @property
    @abstractmethod
    def timestamp_ns(self) -> int:
        pass

    @property
    @abstractmethod
    def frame_idx(self) -> int:
        pass


@service_identifier("ISimulationManagementService")
class ISimulationManagementService(ServiceIdentifier):

    @property
    @abstractmethod
    def _simulations(self) -> Mapping[str, ISimulation]:
        pass

    @abstractmethod
    def get_simulation(
        self, simulation_id: str
    ) -> ResultType[ISimulation, BaseException]:
        pass

    @abstractmethod
    def register_simulation(
        self, simulation: ISimulation
    ) -> ResultType[ISimulation, BaseException]:
        pass

    @abstractmethod
    def step(self, simulation_or_id: ISimulation | str) -> object:
        pass
