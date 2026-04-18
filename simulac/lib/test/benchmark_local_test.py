from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import msgpack
import pytest
import zstd
from PIL import Image
from websockets.exceptions import ConnectionClosed
from websockets.sync.client import ClientConnection, connect


LOCAL_SERVER_URL = "ws://localhost:3000/ws"
REPRO_SEED = 0
IMAGE_STABILITY_RUNS = 3


@dataclass(frozen=True)
class BenchmarkCase:
    benchmark_id: str
    env_id: str
    action_size: int
    build_args: Mapping[str, Any] = field(default_factory=dict)

    @property
    def empty_action(self) -> list[float]:
        return [0.0] * self.action_size

    @property
    def result_prefix(self) -> str:
        return self.benchmark_id


def _case_id(case: BenchmarkCase) -> str:
    return f"{case.benchmark_id}:{case.env_id}"


def _connect_or_skip() -> ClientConnection:
    try:
        return connect(
            LOCAL_SERVER_URL,
            open_timeout=3,
            close_timeout=1,
            ping_interval=None,
        )
    except OSError as exc:
        pytest.skip(f"Local benchmark server is unavailable at {LOCAL_SERVER_URL}: {exc}")


def _send_command(
    socket: ClientConnection,
    command: str,
    /,
    **args: Any,
) -> None:
    socket.send(json.dumps({"command": command, "args": args}))


def _receive_packed_response(socket: ClientConnection) -> Any:
    payload = socket.recv(timeout=20, decode=False)
    if not isinstance(payload, (bytes, bytearray)):
        raise AssertionError(
            f"Expected packed bytes from websocket, got {type(payload)!r}"
        )
    return msgpack.unpackb(zstd.decompress(payload))


def _receive_plain_response(socket: ClientConnection) -> Any:
    payload = socket.recv(timeout=10)
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")
    if not isinstance(payload, str):
        raise AssertionError(
            f"Expected text response from websocket, got {type(payload)!r}"
        )
    return json.loads(payload)


def _assert_images(images: Any) -> None:
    assert isinstance(images, Mapping), "obs.images must be a mapping"
    assert images, "obs.images must not be empty"

    rgb_images = {
        camera_name: pixels
        for camera_name, pixels in images.items()
        if camera_name.endswith("rgb")
    }
    for camera_name, pixels in rgb_images.items():
        assert isinstance(camera_name, str) and camera_name
        assert isinstance(pixels, Sequence) and pixels, (
            f"{camera_name} image must contain rows"
        )

        height = len(pixels)
        width = len(pixels[0])
        assert height != 3, f"{camera_name} image appears to be in CHW format"
        assert width > 0, f"{camera_name} image must contain columns"

        for row in pixels:
            assert isinstance(row, Sequence)
            assert len(row) == width, f"{camera_name} rows must have a consistent width"
            for pixel in row:
                assert isinstance(pixel, Sequence)
                assert len(pixel) == 3, f"{camera_name} pixels must be RGB triplets"
                for channel in pixel:
                    assert isinstance(channel, int)
                    assert 0 <= channel <= 255

        assert height > 0

    depth_images = {
        camera_name: pixels
        for camera_name, pixels in images.items()
        if camera_name.endswith("depth")
    }
    for camera_name, pixels in depth_images.items():
        assert isinstance(camera_name, str) and camera_name
        assert isinstance(pixels, Sequence) and pixels, (
            f"{camera_name} image must contain rows"
        )

        height = len(pixels)
        width = len(pixels[0])
        assert height > 0
        assert width > 0, f"{camera_name} image must contain columns"

        for row in pixels:
            assert isinstance(row, Sequence)
            assert len(row) == width, f"{camera_name} rows must have a consistent width"
            for value in row:
                assert isinstance(value, (int, float)) and not isinstance(value, bool), (
                    f"{camera_name} depth values must be numeric scalars"
                )


def _assert_reset_response(response: Any) -> dict[str, Any]:
    assert isinstance(response, dict), "reset response must unpack to a dict"
    assert "obs" in response, "reset response must include obs"
    obs = response["obs"]
    assert isinstance(obs, Mapping), "obs must be a mapping"
    _assert_images(obs.get("images"))
    return response


def _assert_step_response(response: Any) -> dict[str, Any]:
    assert isinstance(response, dict), "step response must unpack to a dict"
    assert "obs" in response, "step response must include obs"
    assert "reward" in response, "step response must include reward"
    assert "done" in response, "step response must include done"
    assert "info" in response, "step response must include info"

    obs = response["obs"]
    assert isinstance(obs, Mapping), "obs must be a mapping"
    _assert_images(obs.get("images"))
    return response


def _benchmark_result_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "trash" / "benchmark_test-result"


def _image_from_pixels(
    pixels: Sequence[Sequence[Any]],
    *,
    image_name: str,
) -> Image.Image:
    height = len(pixels)
    if height == 0:
        raise ValueError(f"{image_name} has no rows")

    width = len(pixels[0])
    if width == 0:
        raise ValueError(f"{image_name} has no columns")

    first_value = pixels[0][0]
    if isinstance(first_value, Sequence) and not isinstance(
        first_value, (str, bytes, bytearray)
    ):
        flat_pixels = bytearray()
        for row_index, row in enumerate(pixels):
            if len(row) != width:
                raise ValueError(
                    f"{image_name} row {row_index} has width {len(row)}; expected {width}"
                )
            for col_index, pixel in enumerate(row):
                if len(pixel) != 3:
                    raise ValueError(
                        f"{image_name} pixel ({row_index}, {col_index}) does not have 3 channels"
                    )
                for channel in pixel:
                    value = int(channel)
                    if not 0 <= value <= 255:
                        raise ValueError(
                            f"{image_name} pixel ({row_index}, {col_index}) has channel value {value}"
                        )
                    flat_pixels.append(value)
        return Image.frombytes("RGB", (width, height), bytes(flat_pixels))

    min_value = float(first_value)
    max_value = min_value
    for row_index, row in enumerate(pixels):
        if len(row) != width:
            raise ValueError(
                f"{image_name} row {row_index} has width {len(row)}; expected {width}"
            )
        for value in row:
            numeric_value = float(value)
            if numeric_value < min_value:
                min_value = numeric_value
            elif numeric_value > max_value:
                max_value = numeric_value

    scale = 0.0 if max_value == min_value else 255.0 / (max_value - min_value)
    flat_pixels = bytearray()
    for row in pixels:
        for value in row:
            numeric_value = float(value)
            if scale == 0.0:
                flat_pixels.append(0)
            else:
                flat_pixels.append(int((numeric_value - min_value) * scale))
    return Image.frombytes("L", (width, height), bytes(flat_pixels))


def _render_images(images: Mapping[str, Any], *, image_prefix: str) -> dict[str, Image.Image]:
    rendered_images: dict[str, Image.Image] = {}
    for camera_name, pixels in images.items():
        rendered_images[camera_name] = _image_from_pixels(
            pixels,
            image_name=f"{image_prefix}:{camera_name}",
        )
    return rendered_images


def _image_fingerprint(image: Image.Image) -> tuple[str, tuple[int, int], bytes]:
    return image.mode, image.size, image.tobytes()


def _assert_rendered_images_stable(
    first_images: Mapping[str, Image.Image],
    second_images: Mapping[str, Image.Image],
) -> None:
    assert set(first_images) == set(second_images), "Rendered camera set changed"
    for camera_name in first_images:
        assert _image_fingerprint(first_images[camera_name]) == _image_fingerprint(
            second_images[camera_name]
        ), f"{camera_name} rendered image is not stable"


def _save_step_result(
    case: BenchmarkCase,
    *,
    step_index: int,
    seed: int,
    step_result: Mapping[str, Any],
) -> None:
    output_dir = _benchmark_result_dir() / case.result_prefix / case.env_id
    output_dir.mkdir(parents=True, exist_ok=True)

    obs = step_result["obs"]
    assert isinstance(obs, Mapping), "obs must be a mapping"

    images = obs.get("images")
    assert isinstance(images, Mapping), "obs.images must be a mapping"

    rendered_images = _render_images(
        images,
        image_prefix=f"{case.benchmark_id}:{case.env_id}:step_{step_index}",
    )
    for camera_name, image in rendered_images.items():
        image.save(output_dir / f"step_{step_index}_{camera_name}.png")

    json_payload = {
        "benchmark_id": case.benchmark_id,
        "env_id": case.env_id,
        "obs": {key: value for key, value in obs.items() if key != "images"},
        "reward": step_result["reward"],
        "done": step_result["done"],
        "info": step_result["info"],
    }
    with (output_dir / f"step_{step_index}_seed_{seed}.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(json_payload, file, indent=4)


def _build_env(socket: ClientConnection, case: BenchmarkCase) -> dict[str, Any]:
    _send_command(socket, "build_env", env_id=case.env_id, **dict(case.build_args))
    response = _receive_packed_response(socket)
    assert isinstance(response, dict), "build_env response must unpack to a dict"
    return response


def _reset_env(socket: ClientConnection, *, seed: int) -> dict[str, Any]:
    _send_command(socket, "reset", seed=seed)
    return _assert_reset_response(_receive_packed_response(socket))


def _step_env(
    socket: ClientConnection,
    *,
    action: Sequence[float],
) -> dict[str, Any]:
    _send_command(socket, "step", action=list(action))
    return _assert_step_response(_receive_packed_response(socket))


def _close_env(socket: ClientConnection) -> None:
    _send_command(socket, "close")
    try:
        close_response = _receive_plain_response(socket)
    except ConnectionClosed:
        close_response = None

    assert close_response is None or isinstance(close_response, dict)


def _run_first_step(case: BenchmarkCase, *, seed: int) -> dict[str, Any]:
    socket = _connect_or_skip()
    try:
        _build_env(socket, case)
        _reset_env(socket, seed=seed)
        step_result = _step_env(socket, action=case.empty_action)
        _close_env(socket)
        return step_result
    finally:
        socket.close()


def _benchmark_cases() -> list[BenchmarkCase]:
    cases: list[BenchmarkCase] = []

    cases.extend(
        BenchmarkCase("calvin", env_id, 7)
        for env_id in (
            "calvin_scene_A",
            "calvin_scene_B",
            "calvin_scene_C",
            "calvin_scene_D",
        )
    )

    cases.extend(
        BenchmarkCase("meta_world", env_id, 4)
        for env_id in (
            "assembly-v3",
            "basketball-v3",
            "bin-picking-v3",
            "box-close-v3",
            "button-press-topdown-v3",
            "button-press-topdown-wall-v3",
            "button-press-v3",
            "button-press-wall-v3",
            "coffee-button-v3",
            "coffee-pull-v3",
            "coffee-push-v3",
            "dial-turn-v3",
            "disassemble-v3",
            "door-close-v3",
            "door-lock-v3",
            "door-open-v3",
            "door-unlock-v3",
            "hand-insert-v3",
            "drawer-close-v3",
            "drawer-open-v3",
            "faucet-open-v3",
            "faucet-close-v3",
            "hammer-v3",
            "handle-press-side-v3",
            "handle-press-v3",
            "handle-pull-side-v3",
            "handle-pull-v3",
            "lever-pull-v3",
            "peg-insert-side-v3",
            "pick-place-wall-v3",
            "pick-out-of-hole-v3",
            "reach-v3",
            "push-back-v3",
            "push-v3",
            "pick-place-v3",
            "plate-slide-v3",
            "plate-slide-side-v3",
            "plate-slide-back-v3",
            "plate-slide-back-side-v3",
            "peg-unplug-side-v3",
            "soccer-v3",
            "stick-push-v3",
            "stick-pull-v3",
            "push-wall-v3",
            "reach-wall-v3",
            "shelf-place-v3",
            "sweep-into-v3",
            "sweep-v3",
            "window-open-v3",
            "window-close-v3",
        )
    )

    cases.extend(
        BenchmarkCase(
            "bigym",
            env_id,
            15,
            build_args={"floating_base": True, "control_frequency": 50},
        )
        for env_id in (
            "DishwasherClose",
            "DishwasherCloseTrays",
            "DishwasherLoadCups",
            "DishwasherLoadCutlery",
            "DishwasherLoadPlates",
            "DishwasherOpen",
            "DishwasherOpenTrays",
            "DishwasherUnloadCups",
            "DishwasherUnloadCupsLong",
            "DishwasherUnloadCutlery",
            "DishwasherUnloadCutleryLong",
            "DishwasherUnloadPlates",
            "DishwasherUnloadPlatesLong",
            "DrawerTopClose",
            "DrawerTopOpen",
            "DrawersAllClose",
            "DrawersAllOpen",
            "FlipCup",
            "FlipCutlery",
            "FlipSandwich",
            "GroceriesStoreLower",
            "GroceriesStoreUpper",
            "MovePlate",
            "MoveTwoPlates",
            "PickBox",
            "PutCups",
            "ReachTarget",
            "ReachTargetDual",
            "ReachTargetSingle",
            "RemoveSandwich",
            "StackBlocks",
            "StoreBox",
            "StoreKitchenware",
            "TakeCups",
            "ToastSandwich",
            "WallCupboardClose",
            "WallCupboardOpen",
        )
    )

    cases.extend(
        BenchmarkCase("robomimic", env_id, 14 if env_id == "TwoArmTransport" else 7)
        for env_id in (
            "Lift",
            "PickPlaceCan",
            "ToolHang",
            "NutAssemblySquare",
            "TwoArmTransport",
        )
    )

    return cases


BENCHMARK_CASES = _benchmark_cases()


@pytest.mark.integration
@pytest.mark.parametrize("case", BENCHMARK_CASES, ids=_case_id)
def test_benchmark_roundtrip(case: BenchmarkCase) -> None:
    socket = _connect_or_skip()
    try:
        _build_env(socket, case)
        _reset_env(socket, seed=REPRO_SEED)
        step_result = _step_env(socket, action=case.empty_action)
        _save_step_result(case, step_index=0, seed=REPRO_SEED, step_result=step_result)
        _close_env(socket)
    finally:
        socket.close()


@pytest.mark.integration
@pytest.mark.parametrize("case", BENCHMARK_CASES, ids=_case_id)
def test_benchmark_seed_reproducibility(case: BenchmarkCase) -> None:
    socket = _connect_or_skip()
    try:
        _build_env(socket, case)
        first_reset = _reset_env(socket, seed=REPRO_SEED)
        second_reset = _reset_env(socket, seed=REPRO_SEED)
        assert first_reset["obs"] == second_reset["obs"], (
            "reset with the same seed should generate identical obs"
        )
        _close_env(socket)
    finally:
        socket.close()


@pytest.mark.integration
@pytest.mark.parametrize("case", BENCHMARK_CASES, ids=_case_id)
def test_benchmark_image_generation_stability(case: BenchmarkCase) -> None:
    baseline_step = _run_first_step(case, seed=REPRO_SEED)
    baseline_obs = baseline_step["obs"]
    assert isinstance(baseline_obs, Mapping), "obs must be a mapping"
    baseline_images_payload = baseline_obs.get("images")
    assert isinstance(baseline_images_payload, Mapping), "obs.images must be a mapping"
    baseline_images = _render_images(
        baseline_images_payload,
        image_prefix=f"{case.benchmark_id}:{case.env_id}:baseline",
    )

    for run_index in range(1, IMAGE_STABILITY_RUNS):
        step_result = _run_first_step(case, seed=REPRO_SEED)
        obs = step_result["obs"]
        assert isinstance(obs, Mapping), "obs must be a mapping"
        images_payload = obs.get("images")
        assert isinstance(images_payload, Mapping), "obs.images must be a mapping"

        assert images_payload == baseline_images_payload, (
            f"obs.images changed across deterministic runs for {case.env_id}"
        )
        rendered_images = _render_images(
            images_payload,
            image_prefix=f"{case.benchmark_id}:{case.env_id}:run_{run_index}",
        )
        _assert_rendered_images_stable(baseline_images, rendered_images)
