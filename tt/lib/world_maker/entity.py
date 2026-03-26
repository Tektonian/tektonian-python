from tt.sdk.environment_service.common.model.component import (
    MJCFPhysicsComponent,
    RenderingComponent,
)
from tt.sdk.environment_service.common.model.entity import EnvironmentObjectEntity


class Stuff:
    def __init__(self, obj_uri_or_prebuilt_name: str, name: str | None = None) -> None:
        rendering = RenderingComponent("", "")
        physic = MJCFPhysicsComponent(obj_uri_or_prebuilt_name)
        self.entity = EnvironmentObjectEntity(
            rendering=rendering, physics=physic, name=name
        )


class Robot:
    def __init__(self, obj_uri_or_prebuilt_name: str, name: str) -> None:
        rendering = RenderingComponent("", "")
        physic = MJCFPhysicsComponent(obj_uri_or_prebuilt_name)
        self.entity = EnvironmentObjectEntity(
            rendering=rendering, physics=physic, name=name
        )
