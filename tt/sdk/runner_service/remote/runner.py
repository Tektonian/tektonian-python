from dataclasses import dataclass
from typing import Any, Dict

from websockets.sync.client import connect, ClientConnection

from tt.sdk.runner_service.common.runner import IRunner


@dataclass
class RemoteRunner(IRunner):
    id: str
    env_id: str
    state: object

    def __init__(self, id: str, env_id: str, state: object, **kwargs: dict[str, Any]):
        super().__init__(id, env_id, state)

        self._socket = connect("ws://0.0.0.0:3000/api/container")

    def step(self, action: object) -> object:
        pass

    def set_state(self) -> None:
        pass

    def get_state(self) -> None:
        pass

    def render(self) -> None:
        pass
