import uuid
import asyncio
import json
from typing import MutableMapping, List

from websockets.sync.client import connect, ClientConnection
import json_numpy
import numpy
import torch

from tt.sdk.simulation_service.common.simulation_service import (
    ISimulationManagementService,
    IEnvironment,
)


# https://gymnasium.farama.org/api/env/
# https://docs.wandb.ai/models/ref/python/experiments/run#property-run-entity
class Environment(IEnvironment):

    def __init__(self, name: str, task_id: str, 
                 compatibility_date: str, control_mode: str = "ee_pose",
                 camera_spec: dict = {"heights": 128, "widths": 128},
                 max_steps: int = 100
                 ):
        self._uuid: str | None = None
        self._name = name
        self._task_id = task_id
        self._compatibility_date = compatibility_date
        self._observation: object = None
        self._step_num: int = 0
        self._timestamp_ns: int = 0
        self._frame_idx: int = 0
        self._socket: ClientConnection
        self._max_steps = max_steps
        assert max_steps < 1000, "max_steps should be less than default(1000)"
        assert control_mode in ["ee_pose", "joint_position"], "control_mode should be either 'ee_pose' or 'joint_position'"
        
        self._socket = connect("ws://0.0.0.0:7777/ws")
        self._socket.send(
            json.dumps(
                {
                    "command": "build_env",
                    "args": {
                        "name": self._name, 
                        "task_id": self._task_id,
                        "control_mode": control_mode,
                        "camera_spec": camera_spec
                        },
                }
            )
        )

        res = json.loads(self._socket.recv())
        self.env_id = res["env_id"]
        
        return

    def snapshot(self):
        """
        Not implemented
        """
        return

    def reset(self, seed: int = 0):
        self._socket.send(json.dumps({
            "command": "reset", 
            "args": {
                "env_id": self.env_id,
                "seed": seed,
                    }
                }))
        
        res = json.loads(self._socket.recv())
        obs = json_numpy.loads(res['observation'])
        lang_instruction = res['language_instruction']
        self._observation = obs
        self.step_num = 0
        return obs, lang_instruction

    def step(self, action: torch.Tensor | numpy.ndarray | List[float]):
        if isinstance(action, torch.Tensor):
            action = action.cpu().numpy().tolist()
        elif isinstance(action, numpy.ndarray):
            action = action.tolist()
        
        assert isinstance(action, list), f"Action must be a list of floats, got {type(action)}"
        
        if len(action) == 1:
            action = action[0]
        
        self._socket.send(json.dumps({"command": "step", 
                                      "args": {
                                          "action": action}}))
        self.step_num += 1
        res = json.loads(self._socket.recv())
        obs = json_numpy.loads(res["observation"])
        reward = res["reward"]
        done = res["done"]
        info = res["info"]

        if self.step_num >= (self._max_steps - 1):
            done = True
            info['TimeLimit.truncated'] = True
            info['TimeLimit.max_episode_steps'] = self._max_steps

        return obs, reward, done, info


    def close(self):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        result = None
        try:
            result = new_loop.run_until_complete(self.__do_close())
        finally:
            new_loop.close()
            print(result)
            return result

    async def __do_close(self):
        await self._socket.send(json.dumps({"command": "close", "args": {}}))
        res = await self._socket.recv()
        return res

    @property
    def uuid(self) -> str | None:
        return self._uuid

    @uuid.setter
    def uuid(self, value: str):
        self._uuid = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def task(self) -> str:
        return self._task

    @task.setter
    def task(self, value: str):
        self._task = value

    @property
    def compatibility_date(self) -> str:
        return self._compatibility_date

    @compatibility_date.setter
    def compatibility_date(self, value: str):
        self._compatibility_date = value

    @property
    def observation(self) -> object:
        return self._observation

    @observation.setter
    def observation(self, value: object):
        self._observation = value

    @property
    def step_num(self) -> int:
        return self._step_num

    @step_num.setter
    def step_num(self, value: int):
        self._step_num = value

    @property
    def timestamp_ns(self) -> int:
        return self._timestamp_ns

    @timestamp_ns.setter
    def timestamp_ns(self, value: int):
        self._timestamp_ns = value

    @property
    def frame_idx(self) -> int:
        return self._frame_idx

    @frame_idx.setter
    def frame_idx(self, value: int):
        self._frame_idx = value


class SimulationManagementService(ISimulationManagementService):

    def __init__(self):
        self.simulations: MutableMapping[str, IEnvironment] = {}

    @property
    def _simulations(self):
        return self.simulations

    @_simulations.setter
    def _simulations(self, v):
        self.simulations = v

    def register_simulation(self, simulation):
        _uuid = str(uuid.uuid4())

        self._simulations[id] = simulation
        simulation.uuid = _uuid

        return (_uuid, None)

    def get_simulation(self, simulation_id):
        ret = self._simulations.get(simulation_id)
        if ret is None:
            return (None, Exception("No registered simulation"))

        return (ret, None)

    def step(self, simulation_or_id, action):
        simulation = simulation_or_id

        if isinstance(simulation, str):
            simulation = self._simulations.get(simulation)
            if simulation is None:
                raise Exception("No simulation matched with id")
        else:
            if self._simulations.get(simulation.uuid) is None:
                raise Exception("Warn: Not registered simulation")

        simulation
