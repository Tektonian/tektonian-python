from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, MutableMapping

import warp as wp
import newton

from tt.base.error.error import TektonianBaseError
from tt.sdk.runner_service.common.runner import IRunner
from tt.sdk.runner_service.common.physics_engine_adapter import (
    IPhysicsEngineAdapter,
    IPhysicsEngineAdapterState,
)

if TYPE_CHECKING:
    from tt.sdk.runner_service.common.runner_service import IRunnerManagementService
    from tt.sdk.environment_service.common.environment_service import (
        IEnvironmentManagementService,
    )
    from tt.sdk.log_service.common.log_service import ILogService
    import newton
    import warp as wp


class NewtonRunner(IRunner):
    def __init__(self, env_id: str, runner_idx: int, step: Callable[..., None]) -> None:
        self.runner_type = "newton"
        self.id = ""
        self.env_id = env_id

        self._runner_idx = runner_idx
        self._step = step

    def initialize(self) -> None:
        """Do nothing.
        Initialization will be hanlded on NewtonAdapter
        """

    def step(self, action: list[float]) -> None:
        self._step(self._runner_idx, action)

    def tick(self) -> None: ...

    def clone_state(self) -> None: ...
    def get_state(self) -> None: ...
    def render(self) -> None: ...
    def reset(self) -> None: ...
    def set_state(self) -> None: ...

class NewtonAdapter(IPhysicsEngineAdapter):

class NewtonAdapter(IPhysicsEngineAdapter):
    def __init__(
        self,
        env_id: str,
        LogService: ILogService,
        RunnerManagementService: IRunnerManagementService,
        EnvironmentManagementService: IEnvironmentManagementService,
    ) -> None:

        self.env_id = env_id
        self.LogService = LogService
        self.RunnerManagementService = RunnerManagementService
        self.EnvironmentManagementService = EnvironmentManagementService

        self._runner_count = 0
        self._step_count = 0
        self._step_count_map: MutableMapping[str, int] = dict()

        self.builder = newton.ModelBuilder()
        self.model: newton.Model | None = None

        self._solver: newton.solvers.SolverBase | None = None
        self._state_0: newton.State | None = None
        self._state_1: newton.State | None = None
        self._control: newton.Control | None = None
        self._contacts: newton.Contacts | None = None

        self._runner_count = 0

        env_ret = self.EnvironmentManagementService.get_environment(self.env_id)

        if env_ret[0] is None:
            raise env_ret[1]

        env = env_ret[0]

        self.env = env

    def initialize(self):

        objects = self.env.objects

        for obj in objects:
            print(obj.physics.mjcf_uri)

            # if "franka" in obj.physics.mjcf_uri:
            #     self.builder.add_urdf(obj.physics.mjcf_uri)
            # else:
            # TODO: URDF file is not handled here. Need handling code
            self.__scene.add_mjcf(obj.physics.mjcf_uri, xform=(obj.pos + obj.quat))

    def initialize(self) -> None: ...

    def create_runner(self) -> IRunner:

        def runner_step(world_idx: int, action: list[float]):
            if self.model is None:
                self.builder.replicate(self._runner_count)
                self.model = self.builder.finalize()
                self._solver = self.newton.solvers.SolverMuJoCo(self.model)
                self._state_0 = self.model.state()
                self._state_1 = self.model.state()
                self._control = self.model.control()
                self._contacts = self.model.contacts()

            if self.model.max_dofs_per_articulation != len(action):
                self.LogService.warn(
                    f"Action dimension is not fit. expected: [{self.model.max_dofs_per_articulation}] input: [{len(action)}]"
                )

            if (
                self._control is None
                or self._contacts is None
                or self._state_0 is None
                or self._state_1 is None
                or self._solver is None
            ):
                # Maybe not reachable, just for type safing
                assert False, "unreachable"

            # Compute segment for this world instance
            s1 = self.model.max_dofs_per_articulation * world_idx
            s2 = s1 + self.model.max_dofs_per_articulation

            # Copy action into the segment using wp.copy to avoid slice assignment
            src: wp.array[wp.float32] = wp.array(action, dtype=wp.float32)
            count = s2 - s1  # == self.model.max_dofs_per_articulation
            self.warp.copy(
                self._control.joint_target_pos,
                src,
                dest_offset=s1,
                src_offset=0,
                count=count,
            )

            self._solver.step(
                self._state_0,
                self._state_1,
                self._control,
                self._contacts,
                1.0 / 60.0 / 4.0,  # TODO change with tick
            )

        runner = NewtonRunner(
            env_id=self.env.id, runner_idx=self._runner_count, step=runner_step
        )

        new_runner_id = f"{IRunner.__ID_PREVIX}{self._runner_count}"
        self.LogService.debug(
            f"new newton runner created env_id: {self.env_id} runner_id: {new_runner_id}"
        )
        self._step_count_map[new_runner_id] = 0
        self._runner_count += 1

        return runner

    def get_state(self) -> IPhysicsEngineAdapterState:
        return IPhysicsEngineAdapterState(
            self.env_id, self._runner_count, self._step_count_map
        )
