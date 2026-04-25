"""
Executable-looking documentation for the world_maker public interface.

These examples are intentionally skipped. They are not end-to-end runtime tests,
but they should still reflect the current API shape exposed by the library.

Primary mental model:

1. Entity classes such as Stuff, Robot, Camera, and Light describe reusable
   assets.
2. Environment describes the scene definition.
3. Object handles returned by Environment.place_entity mutate build-time scene
   properties.
4. Runner executes one Environment.
5. ParallelRunner executes many Runner instances while preserving Runner-like
   methods.
6. Runtime handles returned by Runner.get_runtime_object mutate live simulation
   state.
"""

from __future__ import annotations

import pytest

from simulac import (
    Camera,
    Constraint,
    Environment,
    Light,
    ParallelRunner,
    Randomize,
    Robot,
    Runner,
    Stuff,
)

pytestmark = pytest.mark.skip(
    reason=(
        "Interface documentation only. The world_maker API is still being "
        "stabilized and several methods are not implemented yet."
    )
)


def test_minimal_tabletop_pick_scene() -> None:
    env = Environment(default_engine="mujoco")

    table = env.place_entity(
        Stuff("assets/tables/workbench.xml"),
        name="table",
        pos=(0.0, 0.0, 0.0),
        description="Fixed tabletop for a pick-and-place task.",
    )
    cube = env.place_entity(
        Stuff("assets/objects/red_cube.xml"),
        name="red_cube",
        pos=(0.35, -0.12, 0.82),
        quat=(0.0, 0.0, 0.0, 1.0),
        description="Target object to pick.",
    )
    robot = env.place_entity(
        Robot("assets/robots/franka_panda.xml"),
        name="panda",
        pos=(0.0, 0.0, 0.0),
        description="7-DoF arm with a parallel gripper.",
    )
    wrist_camera = env.place_entity(
        Camera(type="rgb", mode="track", lookat=(0.35, -0.12, 0.82)),
        name="wrist_rgb",
        pos=(0.28, -0.18, 1.15),
    )
    key_light = env.place_entity(
        Light(type="spot", color=(255, 245, 230), intensity=0.9),
        name="key_light",
        pos=(0.0, -0.6, 2.2),
    )

    table.set_fixed(True)
    cube.set_mass(0.15)
    cube.set_friction(1.2)
    cube.set_size((0.04, 0.04, 0.04))
    robot.set_act_pos([0.0, -0.6, 0.0, -2.2, 0.0, 1.7, 0.78, 0.04, 0.04])
    wrist_camera.set_fov(65.0)
    key_light.set_intensity(0.75)

    runner = Runner(env, 11, 5)
    runner.reset()
    runner.step([0.0, -0.6, 0.0, -2.2, 0.0, 1.7, 0.78, 0.04, 0.04])


def test_scene_can_be_built_from_remote_or_prebuilt_assets() -> None:
    env = Environment(
        default_engine="newton",
        env_uri_or_prebuilt_id="Tektonian/Scenes/tabletop-v0",
    )

    env.place_entity(
        Robot("Tektonian/Robots/franka-panda"),
        name="arm",
        pos=(0.0, 0.0, 0.0),
    )
    env.place_entity(
        Stuff("https://assets.tektonian.com/objects/mug_blue/mug.xml"),
        name="mug",
        pos=(0.42, 0.08, 0.78),
    )
    env.place_entity(
        Camera(type="depth", mode="fixed"),
        name="front_depth",
        pos=(0.7, -0.9, 1.2),
        quat=(0.38, 0.0, 0.0, 0.92),
    )

    runner = Runner(env, 0, runtime_engine="newton")
    state = runner.reset()
    assert state is not None


def test_build_time_randomization_for_reset_sampling() -> None:
    env = Environment(default_engine="mujoco")

    env.place_entity(
        Stuff("assets/tables/table.xml"),
        name="table",
        pos=(0.0, 0.0, 0.0),
    )
    target = env.place_entity(
        Stuff("assets/objects/yellow_bowl.xml"),
        name="bowl",
        pos=(0.25, -0.25, 0.78),
    )
    distractor = env.place_entity(
        Stuff("assets/objects/apple.xml"),
        name="apple",
        pos=(0.20, 0.20, 0.78),
    )
    env.place_entity(
        Robot("assets/robots/franka_panda.xml"),
        name="panda",
        pos=(0.0, 0.0, 0.0),
    )
    env.place_entity(
        Camera(
            type="rgb",
            fov=Randomize.normal(58.0, 4.0, clip_min=50.0, clip_max=70.0),
        ),
        name="front_rgb",
        pos=(0.7, -0.8, 1.3),
    )

    target.set_pos(
        Randomize.uniform(
            (0.25, -0.25, 0.78),
            (0.55, 0.25, 0.78),
            constraints=[
                Constraint.bbox(
                    (0.2, -0.3, 0.75),
                    (0.6, 0.3, 0.9),
                    mode="inside",
                )
            ],
        )
    )
    distractor.set_pos(
        Randomize.choice(
            (0.20, 0.20, 0.78),
            (0.55, -0.18, 0.78),
            constraints=[Constraint.distance("bowl", "apple", min=0.12, max=0.60)],
        )
    )
    target.set_mass(Randomize.uniform(0.08, 0.18))
    distractor.set_fixed(False)

    runner = Runner(env, 7)
    state_a = runner.reset()
    state_b = runner.reset()

    assert state_a != state_b


def test_runtime_handles_are_separate_from_build_time_handles() -> None:
    env = Environment(default_engine="mujoco")
    cube = env.place_entity(
        Stuff("assets/objects/cube.xml"),
        name="cube",
        pos=(0.4, 0.0, 0.8),
    )
    robot = env.place_entity(
        Robot("assets/robots/franka_panda.xml"),
        name="panda",
        pos=(0.0, 0.0, 0.0),
    )

    cube.set_mass(0.12)
    cube.set_friction(1.0)

    runner = Runner(env, 3)
    runner.reset()

    live_cube = runner.get_runtime_object(cube)
    live_robot = runner.get_runtime_object(robot)

    live_cube.change_pos((0.42, 0.05, 0.82))
    live_cube.change_mass(0.20)
    live_robot.step([0.0, -0.5, 0.0, -2.1, 0.0, 1.6, 0.8, 0.02, 0.02])

    assert live_robot.get_pos() is not None


def test_recording_a_lerobot_style_rollout_dataset() -> None:
    env = Environment(default_engine="mujoco")
    env.place_entity(Stuff("assets/tables/table.xml"), name="table")
    env.place_entity(Stuff("assets/objects/can.xml"), name="can", pos=(0.4, 0.1, 0.8))
    env.place_entity(Robot("assets/robots/franka_panda.xml"), name="panda")
    env.place_entity(Camera(type="rgb"), name="front_rgb", pos=(0.7, -0.8, 1.2))
    env.place_entity(
        Camera(type="rgb", mode="track"),
        name="wrist_rgb",
        pos=(0.4, 0.0, 1.0),
    )

    runner = Runner(env, 42, 5, "./datasets/pick_can/episode_0001")
    obs = runner.reset()

    for action in scripted_pick_can_policy(obs):
        obs = runner.step(action)


def test_parallel_runner_from_one_environment_template() -> None:
    env = Environment(default_engine="newton")
    env.place_entity(Stuff("assets/tables/table.xml"), name="table")
    env.place_entity(
        Stuff("assets/objects/block.xml"),
        name="block",
        pos=(0.4, 0.0, 0.78),
    )
    env.place_entity(Robot("assets/robots/franka_panda.xml"), name="panda")

    runner = ParallelRunner(
        [env for _ in range(16)],
        seeds=list(range(16)),
        tick=[5 for _ in range(16)],
        record_locations=[
            f"./datasets/block_lift/episode_{episode_idx:04d}"
            for episode_idx in range(16)
        ],
    )

    states = runner.reset(seeds=list(range(16)))
    actions = [[0.0] * 9 for _ in range(len(runner))]
    runner.step(actions)

    assert len(states) == 16
    assert len(runner) == 16


def test_parallel_runner_repeats_one_environment_template() -> None:
    env = Environment(default_engine="newton")
    env.place_entity(Stuff("assets/tables/table.xml"), name="table")
    env.place_entity(Stuff("assets/objects/red_cube.xml"), name="cube")
    env.place_entity(Robot("assets/robots/franka_panda.xml"), name="panda")

    seeds = list(range(1000, 1032))
    runner = ParallelRunner([env for _ in seeds], seeds=seeds)

    states = runner.reset(seeds=seeds)
    actions = [[0.0] * 9 for _ in range(len(runner))]
    runner.step(actions)

    assert len(states) == len(runner) == 32


def test_parallel_runner_can_mix_different_environment_definitions() -> None:
    lift_env = Environment(default_engine="mujoco")
    lift_env.place_entity(Stuff("assets/tables/table.xml"), name="table")
    lift_env.place_entity(Stuff("assets/objects/cube.xml"), name="cube")
    lift_env.place_entity(Robot("assets/robots/franka_panda.xml"), name="panda")

    door_env = Environment(default_engine="mujoco")
    door_env.place_entity(Stuff("assets/fixtures/door.xml"), name="door")
    door_env.place_entity(Robot("assets/robots/franka_panda.xml"), name="panda")

    drawer_env = Environment(default_engine="mujoco")
    drawer_env.place_entity(Stuff("assets/fixtures/drawer.xml"), name="drawer")
    drawer_env.place_entity(Robot("assets/robots/franka_panda.xml"), name="panda")

    seeds = [10, 20, 30]
    runner = ParallelRunner([lift_env, door_env, drawer_env], seeds=seeds)

    observations = runner.reset(seeds=seeds)
    runner.step(
        [
            [0.0, -0.4, 0.0, -2.0, 0.0, 1.6, 0.8, 0.04, 0.04],
            [0.1, -0.2, 0.0, -1.8, 0.0, 1.5, 0.7, 0.02, 0.02],
            [-0.1, -0.3, 0.0, -2.1, 0.0, 1.7, 0.7, 0.03, 0.03],
        ]
    )

    assert len(observations) == 3


def test_parallel_runner_preserves_single_runner_access() -> None:
    env = Environment(default_engine="newton")
    cube = env.place_entity(Stuff("assets/objects/cube.xml"), name="cube")
    env.place_entity(Robot("assets/robots/franka_panda.xml"), name="panda")

    seeds = [0, 1, 2, 3]
    runners = ParallelRunner([env for _ in seeds], seeds=seeds)
    runners.reset(seeds=seeds)

    first_runner = runners[0]
    first_cube = first_runner.get_runtime_object(cube)
    first_cube.change_pos((0.50, 0.00, 0.90))

    second_runner = runners.at(1)
    second_cube = second_runner.get_runtime_object(cube)
    second_cube.change_pos((0.30, 0.10, 0.85))

    states = runners.get_state()
    assert states[0] != states[1]


def test_parallel_rollout_with_per_environment_done_reset() -> None:
    env = Environment(default_engine="newton")
    env.place_entity(Stuff("assets/tables/table.xml"), name="table")
    env.place_entity(Stuff("assets/objects/cube.xml"), name="cube")
    env.place_entity(Robot("assets/robots/franka_panda.xml"), name="panda")

    seeds = list(range(8))
    runners = ParallelRunner([env for _ in seeds], seeds=seeds)
    observations = runners.reset(seeds=seeds)

    for _ in range(200):
        actions = policy_batch(observations)
        runners.step(actions)
        observations = runners.get_state()
        done_indices = find_done_indices(observations)

        for idx in done_indices:
            observations[idx] = runners[idx].reset()


def test_runner_state_can_be_inspected_after_rollout() -> None:
    env = Environment(default_engine="mujoco")
    env.place_entity(Stuff("assets/tables/table.xml"), name="table")
    env.place_entity(Stuff("assets/objects/cube.xml"), name="cube")
    env.place_entity(Robot("assets/robots/franka_panda.xml"), name="panda")

    runner = Runner(env, 12)
    runner.reset()

    for _ in range(20):
        runner.step([0.0] * 9)

    checkpoint = runner.get_state()
    assert checkpoint is not None


def test_dump_environment_definition_for_review_or_upload() -> None:
    env = Environment(default_engine="mujoco")
    env.place_entity(Stuff("assets/tables/table.xml"), name="table")
    env.place_entity(Stuff("assets/objects/mug.xml"), name="mug", pos=(0.4, 0.0, 0.8))
    env.place_entity(Robot("assets/robots/franka_panda.xml"), name="panda")
    env.place_entity(Camera(type="rgb"), name="front_rgb", pos=(0.8, -0.8, 1.2))
    env.place_entity(Light(type="reactarea"), name="softbox", pos=(0.0, -0.5, 1.8))

    definition = env.dump_env()

    assert definition["physics_engine"] == "mujoco"
    assert definition["objects"][0]["id"] == "ent_stu_0"
    assert definition["machines"][0]["name"] == "panda"


def test_remove_and_replace_scene_objects_before_runner_creation() -> None:
    env = Environment(default_engine="mujoco")
    table = env.place_entity(Stuff("assets/tables/table.xml"), name="table")
    temporary_cube = env.place_entity(
        Stuff("assets/objects/debug_cube.xml"),
        name="debug_cube",
        pos=(0.4, 0.0, 0.8),
    )
    env.place_entity(Robot("assets/robots/franka_panda.xml"), name="panda")

    env.remove_object(temporary_cube)
    env.place_entity(
        Stuff("assets/objects/production_cube.xml"),
        name="cube",
        pos=(0.4, 0.0, 0.8),
    )
    env.remove_object(table._entity.id)

    assert env.get_object("cube")._entity.name == "cube"


def test_multiple_cameras_and_observation_contract() -> None:
    env = Environment(default_engine="mujoco")
    env.place_entity(Stuff("assets/tables/table.xml"), name="table")
    env.place_entity(Stuff("assets/objects/cube.xml"), name="cube")
    env.place_entity(Robot("assets/robots/franka_panda.xml"), name="panda")
    env.place_entity(Camera(type="rgb"), name="front_rgb", pos=(0.8, -0.8, 1.2))
    env.place_entity(Camera(type="depth"), name="front_depth", pos=(0.8, -0.8, 1.2))
    env.place_entity(
        Camera(type="rgb", mode="track"),
        name="wrist_rgb",
        pos=(0.4, 0.0, 1.0),
    )
    env.place_entity(
        Camera(type="segmentation"),
        name="segmentation",
        pos=(0.7, 0.0, 1.4),
    )

    runner = Runner(env, 0)
    obs = runner.reset()

    assert obs["cameras"]["front_rgb"].shape == (480, 640, 3)
    assert obs["cameras"]["front_depth"].shape == (480, 640)
    assert obs["cameras"]["segmentation"].shape == (480, 640)


def test_light_setup_for_rendering_specific_datasets() -> None:
    env = Environment(default_engine="mujoco")
    env.place_entity(Stuff("assets/rooms/kitchen_counter.xml"), name="counter")
    env.place_entity(
        Light(type="reactarea", color=(255, 220, 180), intensity=0.6),
        name="warm_under_cabinet",
        pos=(0.0, -0.4, 1.4),
    )
    env.place_entity(
        Light(type="pointlight", color=(180, 210, 255), intensity=0.35),
        name="cool_window_fill",
        pos=(-0.8, 0.6, 1.6),
    )
    env.place_entity(
        Light(type="ambient", color=(255, 255, 255), intensity=0.15),
        name="overhead",
    )

    runner = Runner(env, 0)
    runner.reset()


def test_world_maker_interface_for_mobile_manipulation() -> None:
    env = Environment(default_engine="newton")
    env.place_entity(Stuff("assets/rooms/warehouse_lane.xml"), name="warehouse")
    env.place_entity(
        Stuff("assets/props/tote.xml"),
        name="target_tote",
        pos=(2.0, 0.5, 0.0),
    )
    mobile_robot = env.place_entity(
        Robot("assets/robots/mobile_manipulator.xml"),
        name="mobile_arm",
        pos=(0.0, 0.0, 0.0),
    )
    env.place_entity(
        Camera(type="pointcloud", mode="fixed"),
        name="base_lidar",
        pos=(0.0, 0.0, 0.35),
    )
    env.place_entity(
        Camera(type="rgb", mode="track"),
        name="head_rgb",
        pos=(0.0, 0.0, 1.4),
    )

    mobile_robot.set_act_pos([0.0, 0.0, 0.0, 0.0, -0.5, 0.0, -2.0, 0.0, 1.5, 0.7])

    runner = Runner(env, 101, 10)
    runner.reset()
    runner.step([0.1, 0.0, 0.02, 0.0, -0.5, 0.0, -2.0, 0.0, 1.5, 0.7])


def test_world_maker_interface_for_humanoid_balance() -> None:
    env = Environment(default_engine="newton")
    env.place_entity(Stuff("assets/terrains/uneven_floor.usd"), name="terrain")
    humanoid = env.place_entity(
        Robot("assets/robots/humanoid_v1.usd"),
        name="humanoid",
        pos=(0.0, 0.0, 1.0),
    )
    env.place_entity(
        Camera(type="rgb", mode="track"),
        name="third_person",
        pos=(3.0, -3.0, 2.0),
    )

    humanoid.set_act_pos([0.0] * 32)

    runner = Runner(env, 5, 2)
    runner.reset()

    for action in walking_controller():
        runner.step(action)


def test_world_maker_interface_for_soft_goal_conditioned_tasks() -> None:
    env = Environment(default_engine="mujoco")
    env.place_entity(Stuff("assets/tables/table.xml"), name="table")
    block = env.place_entity(
        Stuff("assets/objects/green_block.xml"),
        name="block",
        pos=(0.25, -0.2, 0.8),
    )
    goal_marker = env.place_entity(
        Stuff("assets/markers/goal_disk.xml"),
        name="goal",
        pos=(0.45, -0.2, 0.805),
    )
    env.place_entity(Robot("assets/robots/franka_panda.xml"), name="panda")
    env.place_entity(Camera(type="rgb"), name="front_rgb", pos=(0.8, -0.7, 1.1))

    block.set_pos(Randomize.uniform((0.25, -0.2, 0.8), (0.45, 0.2, 0.8)))
    goal_marker.set_pos(
        Randomize.uniform(
            (0.45, -0.2, 0.805),
            (0.65, 0.2, 0.805),
            constraints=[Constraint.distance("block", "goal", min=0.15, max=0.50)],
        )
    )
    block.set_mass(Randomize.choice(0.08, 0.12, 0.16))
    goal_marker.set_fixed(True)

    runner = Runner(env, 99)
    observation = runner.reset()
    goal = observation["objects"]["goal"]["pos"]

    action = goal_conditioned_policy(observation, goal)
    runner.step(action)


def test_interface_for_asset_authoring_smoke_checks() -> None:
    assets_to_check = [
        "assets/objects/mug_blue/mug.xml",
        "assets/objects/mug_red/mug.xml",
        "assets/objects/cereal_box/model.xml",
        "assets/objects/frying_pan/model.xml",
    ]

    env = Environment(default_engine="mujoco")
    env.place_entity(Stuff("assets/tables/display_table.xml"), name="table")

    for idx, asset_uri in enumerate(assets_to_check):
        env.place_entity(
            Stuff(asset_uri),
            name=f"asset_{idx}",
            pos=(0.2 + idx * 0.15, 0.0, 0.8),
        )

    env.place_entity(Camera(type="rgb"), name="inspect_rgb", pos=(0.7, -0.7, 1.1))
    env.place_entity(Light(type="spot"), name="inspect_light", pos=(0.2, -0.4, 1.8))

    runner = Runner(env, 0)
    obs = runner.reset()

    assert obs["cameras"]["inspect_rgb"].shape == (480, 640, 3)


def scripted_pick_can_policy(obs):
    raise NotImplementedError


def policy_batch(observations):
    raise NotImplementedError


def find_done_indices(observations):
    raise NotImplementedError


def walking_controller():
    raise NotImplementedError


def goal_conditioned_policy(observation, goal):
    raise NotImplementedError
