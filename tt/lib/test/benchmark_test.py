from tt.lib.gym_style import init_bench, make_vec


def test_libero_benchmark():
    env = init_bench(
        "Tektonian/Libero",
        "env",
        0,
        {
            "task_name": "",
            "task_id": 0,
            "seed": 0,
            "control_mode": "ee_pose",
            "env_id": "libero_10",
        },
    )


def test_parallel_libero():

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
