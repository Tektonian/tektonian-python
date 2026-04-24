from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Literal, overload

from simulac.base.error.error import SimulacBaseError
from simulac.sdk import obtain_runtime

from .entity import ActionT
from .object import _CREATE_SENTINAL, Environment
from .randomize import Vec3

if TYPE_CHECKING:
    from .object import CameraObject, LightObject, RobotObject, StuffObject


class Runner:
    def __init__(
        self,
        env: Environment,
        seed: int | None = 0,
        tick: int | None = 5,  # 5ms
        record_location: str
        | None = None,  # save location of runtime recording data (a.k.a. Lerobot dataset format)
        /,
        *,
        runtime_engine: Literal["mujoco", "newton", "genesis"] = "mujoco",
    ):
        self.seed = seed
        self.tick_time = tick

        self._world_maker = obtain_runtime().world_maker

        self._runner = self._world_maker.create_runner(env._env.id)

        env._freeze()

    def step(self, action: list[float]):
        self._runner.step(action)

    def tick(self): ...

    type State = Any

    def reset(self) -> State: ...

    def get_state(self): ...

    @overload
    def get_runtime_object(self, obj: StuffObject) -> StuffRuntime: ...
    @overload
    def get_runtime_object(
        self, obj: RobotObject[ActionT]
    ) -> RobotRuntime[ActionT]: ...
    @overload
    def get_runtime_object(self, obj: LightObject) -> LightRuntime: ...
    @overload
    def get_runtime_object(self, obj: CameraObject) -> CameraRuntime: ...
    def get_runtime_object(
        self, obj: StuffObject | RobotObject[Any] | LightObject | CameraObject
    ) -> StuffRuntime | RobotRuntime[Any] | LightRuntime | CameraRuntime: ...

    def close(self) -> None: ...

    # For context manage
    # e.g., `with Runner(env) as runner:`
    def __enter__(self): ...
    def __exit__(self, exc_type, exc, tb): ...

    def _debug_render(self):
        return self._runner._debug_render()


class StuffRuntime:
    def __init__(
        self,
        /,
        *,
        _create_sentinal: object,
    ) -> None:
        if _create_sentinal is not _CREATE_SENTINAL:
            raise SimulacBaseError("Please do not create stuff object directly")

    def change_mass(self, mass: float) -> None: ...
    def change_pos(self, pos: Vec3) -> None: ...
    def change_size(self, size: Vec3) -> None: ...
    def change_fixed(self, is_fixed: bool) -> None: ...
    def change_friction(self, friction: float) -> None: ...
    def change_density(self, density: float) -> None: ...


class RobotRuntime(Generic[ActionT]):
    def __init__(
        self,
        /,
        *,
        _create_sentinal: object,
    ) -> None:
        if _create_sentinal is not _CREATE_SENTINAL:
            raise SimulacBaseError("Please do not create stuff object directly")

    def step(self, action: ActionT) -> None: ...
    def tick(self) -> None: ...

    def get_pos(self) -> Vec3: ...
    def get_vel(self) -> list[float]: ...


class CameraRuntime:
    def __init__(
        self,
        /,
        *,
        _create_sentinal: object,
    ) -> None:
        if _create_sentinal is not _CREATE_SENTINAL:
            raise SimulacBaseError("Please do not create stuff object directly")

    def change_pos(self, pos: Vec3) -> None: ...
    def change_rot(self, rot: Vec3) -> None: ...


class LightRuntime:
    def __init__(
        self,
        /,
        *,
        _create_sentinal: object,
    ) -> None:
        if _create_sentinal is not _CREATE_SENTINAL:
            raise SimulacBaseError("Please do not create stuff object directly")

    def change_pos(self, pos: Vec3) -> None: ...
    def change_rot(self, rot: Vec3) -> None: ...
    def change_intensity(self, intensity: float) -> None: ...
    def change_color(self, color: tuple[int, int, int]) -> None: ...

    # Needed?
    def __change_type(self): ...


# region Will be implemented


class ParallelRunner:
    def __init__(
        self,
        envs: list[Environment],
        seeds: list[int] | None = None,
        tick: list[int] | None = None,
        record_locations: list[str] | None = None,
        strict: bool = True,
    ) -> None: ...

    def step(self, actions: list[list[float]]) -> None: ...
    def tick(self) -> None: ...

    type State = Any

    def reset(self, seeds: list[int]) -> list[State]: ...

    def close(self) -> None: ...

    # For context manage
    # e.g., `with Runner(env) as runner:`
    def __enter__(self): ...
    def __exit__(self, exc_type, exc, tb): ...

    def at(self, idx: int) -> Runner: ...

    def get_state(self) -> object: ...

    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> Runner: ...
