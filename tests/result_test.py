from abc import ABC
import random
import time

from tt.lib.gym_style import init_bench


def test_result_type():
    # env = init_bench(
    #     "Tektonian/Libero",
    #     "libero_10/KITCHEN_SCENE3_turn_on_the_stove_and_put_the_moka_pot_on_it",
    #     0,
    # )

    # env.reset(0)
    # start_time = time.time()
    # for _ in range(20):
    #     env.step([0, 0, 0, 0, 0, 0, 0])
    # end_time = time.time()

    # print(
    #     f"elapsed: {end_time - start_time}"
    # )  # about 3~4 seconds vcpu: 1~1.2 vcpu ram: 3.4GB / 2 instances -> 1.6 vcpu  same ram / 3 instances -> crash

    # assert 1 == True

    # return

    # # test start: Bigym MovePlate
    # env = init_bench(
    #     "Tektonian/Bigym",
    #     "MovePlate",
    #     0,
    #     benchmark_specific={"floating_base": True, "control_frequency": 50},
    # )
    
    # obs, info = env.reset(seed=0)
    # lang = info['task_description']
    # for _ in range(20):
    #     obs, rew, done, info = env.step([0] * 15)
    
    
    # assert 1 == True
    # return
    # # test end

    # test start: robomimic
    env = init_bench(
        "Tektonian/Robomimic",
        "transport",#"square",#"can",#"lift",
        0,
        benchmark_specific={"floating_base": True, "control_frequency": 50},
    )
    
    obs, info = env.reset(seed=0)
    lang = info['task_description']
    for _ in range(20):
        obs, rew, done, info = env.step([0] * 14)
    
    assert 1 == True
    return
    # test end

    # "assembly-v3","basketball-v3","bin-picking-v3","box-close-v3","button-press-topdown-v3","button-press-topdown-wall-v3","button-press-v3","button-press-wall-v3","coffee-button-v3","coffee-pull-v3","coffee-push-v3","dial-turn-v3","disassemble-v3","door-close-v3","door-lock-v3","door-open-v3","door-unlock-v3","hand-insert-v3","drawer-close-v3","drawer-open-v3","faucet-open-v3","faucet-close-v3","hammer-v3","handle-press-side-v3","handle-press-v3","handle-pull-side-v3","handle-pull-v3","lever-pull-v3","pick-place-wall-v3","pick-out-of-hole-v3","pick-place-v3","plate-slide-v3","plate-slide-side-v3","plate-slide-back-v3","plate-slide-back-side-v3","peg-insert-side-v3","peg-unplug-side-v3","soccer-v3","stick-push-v3","stick-pull-v3","push-v3","push-wall-v3","push-back-v3","reach-v3","reach-wall-v3","shelf-place-v3","sweep-into-v3","sweep-v3","window-open-v3","window-close-v3",
    # camera_name = '' # one of: ['corner', 'corner2', 'corner3', 'corner4', 'topview', 'behindGripper', 'gripperPOV']
    init_bench("Tektonian/Metaworld", "assembly-v3", 0, env_specific={})

    init_bench("Tektonian/Calvin", "A")

    init_bench(
        "Tektonian/Robosuite",
        "assembly-v3",
        0,
        env_specific={
            """
            Robot, GripperTypes는 default로 설정되도록?
            """
            "robots": [],  # ["Sawyer", "Panda"] https://github.com/ARISE-Initiative/robosuite/blob/6c10ef24a4bb52f59199976125060ce793470e6e/robosuite/robots/__init__.py#L15
            "gripper_types": ["PandaGripper", "RethinkGripper"],
            "env_configuration": "opposed",  # "opposed" | "parallel"
        },
    )
