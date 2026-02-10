import uuid
from typing import MutableMapping

import websockets

from tt.sdk.simulation_service.common.simulation_service import (
    ISimulationManagementService,
    IEnvironment,
)


# https://gymnasium.farama.org/api/env/
class Environment(IEnvironment):

    def __init__(self, name: str, compatibility_date: str):
        self._uuid: str | None = None
        self._name = name
        self._compatibility_date = compatibility_date
        self._observation: object = None
        self._step_num: int = 0
        self._timestamp_ns: int = 0
        self._frame_idx: int = 0

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
        self.simulations: MutableMapping[str, ISimulation] = {}

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

    def step(self, simulation_or_id):
        simulation = simulation_or_id

        if isinstance(simulation, str):
            simulation = self._simulations.get(simulation)
            if simulation is None:
                raise Exception("No simulation matched with id")
        else:
            if self._simulations.get(simulation.uuid) is None:
                raise Exception("Warn: Not registered simulation")

        simulation
