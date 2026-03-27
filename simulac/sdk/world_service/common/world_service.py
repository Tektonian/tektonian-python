from __future__ import annotations  # 3.7+ 에서 필요

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Mapping, Optional

from simulac.base.error.error import SimulacBaseError
from simulac.base.instantiate.instantiate import ServiceIdentifier, service_identifier
from simulac.base.result.result import ResultType

if TYPE_CHECKING:
    from simulac.sdk.environment_service.common.environment import IEnvironment


@dataclass
class IWorld:
    id: str
    environments: list[IEnvironment] = field(default_factory=list["IEnvironment"])


@service_identifier("IWorldManagementService")
class IWorldManagementService(ServiceIdentifier["IWorldManagementService"]):
    _ID_PREFIX = "world_"

    @property
    @abstractmethod
    def _worlds(self) -> List[IWorld]:
        pass

    @abstractmethod
    def get_world(self, world_id: str) -> ResultType[IWorld, BaseException]:
        pass

    @abstractmethod
    def create_world(
        self, environments: Optional[List[IEnvironment]]
    ) -> ResultType[IWorld, BaseException]:
        pass


class WorldManagementService(IWorldManagementService):
    def __init__(self) -> None:
        self.worlds: List[IWorld] = []

    @property
    def _worlds(self) -> List[IWorld]:
        return self.worlds

    def get_world(self, world_id: str):
        for world in self.worlds:
            if world.id == world_id:
                return (world, None)
        return (None, SimulacBaseError("no world found"))

    def create_world(self, environments: Optional[List[IEnvironment]]):
        world_id = f"{self._ID_PREFIX}{len(self._worlds)}"
        if environments is None:
            world = IWorld(world_id, [])
            return (world, None)

        else:
            world = IWorld(world_id, environments)
            return (world, None)
