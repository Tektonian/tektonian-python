
from typing import (
	Generic,
	TypeVar,
	Union,
	Tuple
)

T = TypeVar("T")
E = TypeVar("E")

# Type alias for convenience
ResultType = Union[Tuple[T, None], Tuple[None, E]]

