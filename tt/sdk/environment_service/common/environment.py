from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from urllib.parse import urlsplit, SplitResult

from tt.base.error.error import TektonianBaseError


# https://gymnasium.farama.org/api/env/
# https://docs.wandb.ai/models/ref/python/experiments/run#property-run-entity
@dataclass
class IEnvironment(ABC):
    id: str
    world_id: str
    env_json_uri: str | SplitResult
    act_json_uri: str | SplitResult
    obs_json_uri: str | SplitResult

    objects: list[object] = field(default_factory=list[object])
    proprioception: list[object] = field(default_factory=list[object])
    cameras: list[object] = field(default_factory=list[object])

    @abstractmethod
    def snapshop(self):
        pass

    @abstractmethod
    def load_env(self):
        pass

    def __post_init__(self):
        url = (
            urlsplit(self.env_json_uri)
            if isinstance(self.env_json_uri, str)
            else self.env_json_uri
        )

        if url.scheme not in ["http", "https", "file", "memory"]:
            raise TektonianBaseError("not valid schema")
