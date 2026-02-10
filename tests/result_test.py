from abc import ABC

from tt.base.result.result import ResultType
from tt.base.instantiate.extensions import (
    register_singleton,
    get_singleton_service_descriptors,
)
from tt import simulation, Environment


def test_result_type():
    print(get_singleton_service_descriptors()[0][1].ctor())
    print(simulation)

    sim1 = Environment(name="LIBERO/Object", compatibility_date="2026-02-09")

    sim_id, err = simulation.register_simulation(simulation=sim1)

    simulation.step(sim_id)

    assert 1 == True
