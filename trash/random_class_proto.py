from dataclasses import dataclass
from typing import Any, Generic, List, Literal, Tuple, TypeAlias, TypeVar, Union, cast

T = TypeVar("T")


@dataclass
class __Base:
    on: Literal["reset", "spawn", "step"] = "spawn"
    dist: Literal["uniform", "normal", "choice", "triangular", "lognormal"] = "normal"
    mode: Literal["replace", "additive", "multiplicative"] = "replace"


@dataclass
class __BaseMinMax(Generic[T]):
    min: T
    max: T


@dataclass
class __EulerMinMax:
    euler_min: Tuple[float, float, float]
    euler_max: Tuple[float, float, float]


@dataclass
class RandomValue[O](__Base, __BaseMinMax[O]): ...


@dataclass
class __Tri:
    pick: float


@dataclass
class TriangularRandom[V](RandomValue[V], __Tri):
    dist = "triangular"


@dataclass
class EulerRandom[V](__Base, __EulerMinMax[V]): ...


@dataclass
class __Normal:
    loc: float
    scale: float


@dataclass
class NormalRandom[V](RandomValue[V], __Normal):
    dist = "normal"


@dataclass
class __Choice(Generic[T]):
    values: List[T]
    weights: List[float]


@dataclass
class ChoiceRandom[V](
    __Base,
    __Choice[V],
):
    dist = "choice"


@dataclass
class VarRandom:
    var: str


@dataclass
class CustomPrividerRandom:
    """
    entry:
        Python function location 'importlib.metadata.entry_point(group="tektonian.randomizers")
        expected function like
            ```py
            def table_top(ctx: IEnvironment, *kwargs) -> value:
            ```
        Will be imported like tektonian.randomizers:table_top
    """

    entry: str
    kwargs: dict[str, Any]
    on: Literal["reset", "spawn", "step"] = "spawn"
