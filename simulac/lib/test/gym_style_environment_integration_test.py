from __future__ import annotations

from typing import Any

import requests
import pytest

from simulac.lib.gym_style import init_bench, make_vec
from simulac.sdk.runtime import obtain_runtime


def _require_integration_ready() -> None:
    runtime = obtain_runtime()
    token = runtime.environment_variable.token
    if token is None:
        pytest.skip("SIMULAC_API_KEY is required for benchmark integration tests.")

    base_url = runtime.environment_variable.base_url
    try:
        requests.get(base_url, timeout=3)
    except requests.RequestException as err:
        pytest.skip(f"Benchmark backend is not reachable: {err!r}")


def _install_send_wrapper(
    env: Any,
    *,
    inject_step_failure: bool = False,
    step_failure_exc: Exception | None = None,
) -> dict[str, int]:
    original_send = env._send_command
    state: dict[str, int] = {"step": 0, "reset": 0, "other": 0, "fail": 0}

    def _send_wrapper(_socket: object, command: str, /, **args: Any) -> None:
        if command == "step":
            state["step"] += 1
            if inject_step_failure and state["fail"] == 0:
                state["fail"] = 1
                raise step_failure_exc or ConnectionError("injected integration failure")
        elif command == "reset":
            state["reset"] += 1
        else:
            state["other"] += 1

        return original_send(_socket, command, **args)

    env._send_command = _send_wrapper  # type: ignore[method-assign]
    return state


@pytest.mark.integration
def test_integration_make_vec_real_envs_step() -> None:
    _require_integration_ready()

    env_a = init_bench(
        "Tektonian/Metaworld",
        "assembly-v3",
        0,
        {},
    )
    env_b = init_bench(
        "Tektonian/Metaworld",
        "reach-v3",
        0,
        {},
    )
    vec = make_vec([env_a, env_b])

    try:
        reset_results = vec.reset([0, 1])
        assert len(reset_results) == 2
        for obs, info in reset_results:
            assert isinstance(obs, dict)
            assert isinstance(info, dict)

        actions = [[0.0] * 4, [0.0] * 4]
        results = vec.step(actions)

        assert len(results) == 2
        for obs, reward, done, info in results:
            assert isinstance(obs, dict)
            assert isinstance(reward, float | int)
            assert isinstance(done, bool)
            assert isinstance(info, dict)
    finally:
        vec.close()


@pytest.mark.integration
def test_integration_make_vec_error_isolation_and_recovery() -> None:
    _require_integration_ready()

    env_ok = init_bench(
        "Tektonian/Metaworld",
        "assembly-v3",
        11,
        {},
    )
    env_fail = init_bench(
        "Tektonian/Metaworld",
        "reach-v3",
        11,
        {},
    )

    fail_state = _install_send_wrapper(
        env_fail,
        inject_step_failure=True,
        step_failure_exc=ConnectionError("integration injected recoverable failure"),
    )
    ok_state = _install_send_wrapper(env_ok)
    vec = make_vec([env_fail, env_ok])

    try:
        vec.reset([11, 12])

        actions = [[0.0] * 4, [0.0] * 4]
        results = vec.step(actions)

        assert len(results) == 2
        assert fail_state["step"] >= 2
        assert ok_state["step"] == 1

        obs_fail, reward_fail, done_fail, info_fail = results[0]
        assert isinstance(obs_fail, dict)
        assert isinstance(reward_fail, float | int)
        assert isinstance(done_fail, bool)
        assert isinstance(info_fail, dict)

        obs_ok, reward_ok, done_ok, info_ok = results[1]
        assert isinstance(obs_ok, dict)
        assert isinstance(reward_ok, float | int)
        assert isinstance(done_ok, bool)
        assert isinstance(info_ok, dict)

        assert fail_state["fail"] == 1
        assert ok_state["fail"] == 0
    finally:
        vec.close()
