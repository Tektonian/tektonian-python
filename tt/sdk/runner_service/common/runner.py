from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class IRunner(ABC):

    id: str
    env_id: str
    state: object

    @abstractmethod
    def step(self, action: object) -> object:
        pass

    @abstractmethod
    def set_state(self) -> None:
        pass

    @abstractmethod
    def get_state(self) -> None:
        pass

    @abstractmethod
    def render(self) -> None:
        pass
