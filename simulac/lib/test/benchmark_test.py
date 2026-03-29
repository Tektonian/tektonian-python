import pytest
from simulac.lib.gym_style import init_bench, make_vec


@pytest.mark.integration
def test_libero_benchmark():
    env = init_bench(
        "Tektonian/Libero",
        "libero_90/KITCHEN_SCENE2_put_the_black_bowl_at_the_back_on_the_plate",
        0,
        {
            "control_mode": "ee_pose",
        },
    )
    EMPTY_ACTION = [0] * 7
    obs_history = []
    obs_history.append(env.step(EMPTY_ACTION))
    for _ in range(4):
        obs_history.append(env.step(EMPTY_ACTION))

    reset = env.reset(0)
    for i in range(len(obs_history)):
        ret = env.step(EMPTY_ACTION)
        assert ret == obs_history[i]

    new_env = init_bench(
        "Tektonian/Libero",
        "libero_10/LIVING_ROOM_SCENE2_put_both_the_cream_cheese_box_and_the_butter_in_the_basket",
        0,
        {
            "control_mode": "ee_pose",
        },
    )
    new_obs = new_env.step(EMPTY_ACTION)
    assert obs_history[0] != new_obs


def test_parallel_libero():

@pytest.mark.integration
def test_parallel_libero():
    return
    ast_option = ["Tektonian/Libero", "env", 0]
    options = dict(
        benchmark_specific={
            "task_name": "",
            "task_id": 0,
            "seed": 0,
            "control_mode": "ee_pose",
            "env_id": "libero_10",
        },
    )

    env1 = init_bench(*ast_option, **options)
    env2 = init_bench(*ast_option, **options)
    env3 = init_bench(*ast_option, **options)

    vec_env = make_vec([env1, env2, env3])

    for i in range(50):
        ret = vec_env.step([[0] * 7, [0] * 7, [0] * 7])
        print("recv", len(ret))
