from abc import ABC
import random

from tt.base.result.result import ResultType
from tt.base.instantiate.extensions import (
    register_singleton,
    get_singleton_service_descriptors,
)
from tt import simulation, Environment


def test_result_type():
    print(get_singleton_service_descriptors()[0][1].ctor())
    print(simulation)

    sim1 = Environment(
        name="LIBERO/libero_10", compatibility_date="2026-02-09", task="0"
    )

    sim1.reset()
    sim1.step([random.random()] * 7)
    sim1.step([random.random()] * 7)
    sim1.step([random.random()] * 7)
    sim1.step([random.random()] * 7)
    sim1.close()
    # sim_id, err = simulation.register_simulation(simulation=sim1)

    # rand_action = []

    # simulation.step(sim_id, [random.random()] * 7)

    assert 1 == True
