from __future__ import annotations

from typing import Callable, Protocol, runtime_checkable


@runtime_checkable
class IStuffRuntimeOps(Protocol):
    def set_pos(self, pos: tuple[float, float, float]) -> None: ...
    def set_mass(self, mass: float) -> None: ...
    def set_size(self, size: tuple[float, float, float]) -> None: ...
    def set_fixed(self, is_fixed: bool) -> None: ...
    def set_friction(self, friction: float) -> None: ...
    def set_density(self, density: float) -> None: ...


class StuffRuntime:
    def __init__(self, entity_id: str, ops: IStuffRuntimeOps) -> None:
        self.id = entity_id
        self._ops = ops

    def change_pos(self, pos: tuple[float, float, float]) -> None:
        self._ops.set_pos(pos)

    def change_mass(self, mass: float) -> None:
        self._ops.set_mass(mass)

    def change_size(self, size: tuple[float, float, float]) -> None:
        self._ops.set_size(size)

    def change_fixed(self, is_fixed: bool) -> None:
        self._ops.set_fixed(is_fixed)

    def change_friction(self, friction: float) -> None:
        self._ops.set_friction(friction)

    def change_density(self, density: float) -> None:
        self._ops.set_density(density)
