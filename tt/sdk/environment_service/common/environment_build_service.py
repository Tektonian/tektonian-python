from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, List

from tt.base.instantiate.instantiate import ServiceIdentifier, service_identifier
from tt.sdk.environment_service.common.model.entity import (
    EnvironmentCameraEntity,
    EnvironmentLightEntity,
    EnvironmentMachineEntity,
)

if TYPE_CHECKING:
    import urllib.parse

    from tt.sdk.environment_service.common.environment import IEnvironment
    from tt.sdk.environment_service.common.model.component import (
        MJCFPhysicsComponent,
        URDFPhysicsComponent,
        USDPhysicsComponent,
    )


@service_identifier("IEnvironmentBuildService")
class IEnvironmentBuildService(ServiceIdentifier["IEnvironmentBuildService"]):
    @abstractmethod
    def add_entity(
        self,
        entity_or_uri: (
            urllib.parse.SplitResult  # <- mostly for mjcf, urdf, or usc
            | EnvironmentCameraEntity
            | EnvironmentLightEntity
            | EnvironmentMachineEntity
        ),
    ): ...

    @abstractmethod
    def remove_entity(self, entity_id: str): ...

    @abstractmethod
    def replace_entity(self, entity_id: str, render_uri: str, physics_uri: str): ...

    @abstractmethod
    def change_pos(self, entity_id: str): ...

    @abstractmethod
    def change_quat(self, entity_id: str): ...

    @abstractmethod
    def export_env_json(self) -> str: ...

    @abstractmethod
    def export_act_json(self) -> str: ...

    @abstractmethod
    def export_obs_json(self) -> str: ...

    @abstractmethod
    def load_mjcf(self, path: str) -> str: ...

    @abstractmethod
    def load_urdf(self, path: str) -> str: ...

    @abstractmethod
    def load_usd(self, path: str) -> str: ...

    @abstractmethod
    def build_env(self) -> IEnvironment: ...


class EnvironmentBuildService(IEnvironmentBuildService):
    def __init__(self) -> None:
        self.entitys: (
            List[MJCFPhysicsComponent]
            | List[URDFPhysicsComponent]
            | List[USDPhysicsComponent]
        ) = []

    def __compatibility_check(
        self,
        target_physics: Literal["mujoco", "newton", "genesis"],
    ) -> bool:
        """Check compatibility between assets and physics engine

        Compatibility table

        | Type | Mujoco | Newton | Genesis |
        |:-----|:-----:|:-----:|:-----:|
        | MJCF | O | O (with add_mjcf()) | O (with morphs.MJCF) |
        | USDF | △ (need add `<mujoco/>` tag in .usdf file) | O (with add_urdf()) | O (with morphs.URDF) |
        | USD  | X | O (with add_usd()) | X |

        """

        return True
