from __future__ import annotations
import json
from typing import TYPE_CHECKING, Any
import urllib.parse

from websockets import connect

from tt.base.error.error import TektonianBaseError
from tt.sdk.runner_service.common.runner import IRunner
from tt.sdk.runner_service.common.runner_service import IRunnerManagementService

if TYPE_CHECKING:
    from tt.sdk.environment_service.common.environment_service import (
        IEnvironmentManagementService,
    )
    from tt.sdk.log_service.common.log_service import ILogService
    from tt.sdk.runner_service.common.physics_engine_adapter import (
        IPhysicsEngineAdapter,
    )


class RemoteRunner(IRunner):
    def __init__(
        self,
        id: str,
        env_id: str,
        state: object,
        owner: str,
        remote_env_id: str,
        env_specific_kwars: dict[str, Any],
    ) -> None:
        self.runner_type = "remote"
        self.id = id
        self.env_id = env_id

        self.state = state
        self.kwargs = env_specific_kwars

        self._socket = connect(
            f"ws://localhost:3000/api/container/{owner}/{remote_env_id}?{env_specific_kwars}"
        )

        msg = json.dumps({"command": "build_env", "args": self.kwargs})
        print(msg)
        self._socket.send(msg)
        recv = self._socket.recv()
        # print(recv)

    def initialize(self) -> None: ...

    def step(self, action: list[float]) -> None:
        self._socket.send(json.dumps({"command": "step", "args": {"action": action}}))

        recv = self._socket.recv()
        return recv

    def tick(self) -> None: ...

    def get_state(self) -> None: ...


class RemoteAdapter(IPhysicsEngineAdapter):
    def __init__(
        self,
        env_id: str,
        LogService: ILogService,
        RunnerManagementService: IRunnerManagementService,
        EnvironmentManagementService: IEnvironmentManagementService,
    ) -> None:
        self.LogService = LogService
        self.RunnerManagementService = RunnerManagementService
        self.EnvironmentManagementService = EnvironmentManagementService

        env_ret = self.EnvironmentManagementService.get_environment(env_id)

        if env_ret[0] is None:
            raise TektonianBaseError(f"No environment {env_id}")

        env = env_ret[0]
        self.env = env

    def initialize(self) -> None: ...

    def create_runner(self) -> IRunner:

        env_uri = self.env.env_json_uri

        if isinstance(env_uri, str):
            env_uri = urllib.parse.urlsplit(env_uri)

        [owner, remote_env_id] = env_uri.path.split("/")[-3:-1]

        runner = RemoteRunner("", self.env_id, {}, owner, remote_env_id, {})

        return runner
