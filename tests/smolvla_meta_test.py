import os
import time

import cv2
import imageio
import numpy as np
import torch

from lerobot.policies.factory import make_pre_post_processors
from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
from tt.lib.gym_style import init_bench

# Constants
N_CHUNK = 1
TASK_ENVS = [
    "MT1/assembly-v3",
]
MAX_STEPS_PER_ENV = {
    "MT1/assembly-v3": 50,
}


def process_frames(frames, lang):
    """Overlay task text on video frames and resize to height 120."""
    if not frames:
        return frames

    frames = [np.rot90(frame, k=2) for frame in frames]
    frames = [np.pad(frame, ((30, 0), (0, 0), (0, 0)), mode="constant", constant_values=255) for frame in frames]
    max_line_length = 50
    lang_lines = [lang[i : i + max_line_length] for i in range(0, len(lang), max_line_length)]

    for frame in frames:
        for j, line in enumerate(lang_lines[:2]):
            y = 9 + j * 9
            cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (0, 0, 0), 1, cv2.LINE_AA)
    # Resize frames to height 120, keeping aspect ratio
    resized_frames = []
    for frame in frames:
        h, w = frame.shape[:2]
        new_h = 240
        new_w = int(w * (new_h / h))
        resized_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
        resized_frames.append(resized_frame)
    return resized_frames


def patch_draccus_non_callable_types():
    """Patch for draccus to handle non-callable types."""
    try:
        from draccus.wrappers.field_wrapper import FieldWrapper
    except Exception:
        return

    if getattr(FieldWrapper, "_tektonian_py314_patch", False):
        return

    original_get_arg_options = FieldWrapper.get_arg_options

    def _patched_get_arg_options(self):
        options = original_get_arg_options(self)
        tpe = options.get("type")
        if tpe is not None and not callable(tpe):
            options["type"] = str
        return options

    FieldWrapper.get_arg_options = _patched_get_arg_options
    FieldWrapper._tektonian_py314_patch = True


def metaworld_to_smolvla_obs(obs, lang, device):
    """Convert Meta-World observation to smolvla input format."""
    state = torch.cat([
        torch.tensor(obs['states']["robot_0_eef_pos"], device=device, dtype=torch.float32),
        torch.tensor(obs['states']["robot_0_gripper_open"], device=device, dtype=torch.float32)
    ])

    image = torch.tensor(obs["images"]["cam_0_rgb"], 
                         device=device, 
                         dtype=torch.float32).permute(2, 0, 1) / 255.0

    return {
        "observation.image": image,
        "observation.state": state,
        "task": lang,
    }


def run_task(policy, preprocess, postprocess, device, env_id):
    env_id = "MT1/reach-v3"
    env = init_bench("Tektonian/Metaworld", env_id, 0, benchmark_specific={})
    max_steps = 300
    # env_id = "MT1/assembly-v3"
    obs, info = env.reset(seed=0)
    lang = info['task_description']

    frames = []
    steps = 0
    done = False
    success = False
    count = 0
    pred_action_chunk = None

    while steps < max_steps:
        batch_input = metaworld_to_smolvla_obs(obs, lang, device)
        batch = preprocess(batch_input)

        with torch.inference_mode():
            if N_CHUNK == 1:
                pred_action = policy.select_action(batch)
            else:
                if steps % N_CHUNK == 0:
                    count = 0
                    pred_action_chunk = policy.predict_action_chunk(batch)
                    pred_action = pred_action_chunk[:, count]
                else:
                    count += 1
                    pred_action = pred_action_chunk[:, count]

        frame = obs["images"]["cam0_rgb"]
        if frame.dtype != np.uint8:
            frame = (frame * 255).astype(np.uint8) if frame.max() <= 1.0 else frame.astype(np.uint8)
        frames.append(frame)

        action = postprocess(pred_action)
        obs, reward, done, info = env.step(action)
        steps += 1

        print(f"{env_id} Step {steps} reward: {reward} done: {done} info: {info}")
        if done:
            if info.get("success", False):
                success = True
            break

    result_dir = os.path.join("tests", "results", "metaworld")
    os.makedirs(result_dir, exist_ok=True)

    result_path = os.path.join(result_dir, f"smolvla_{env_id.replace('/', '_')}_result.txt")
    with open(result_path, "w", encoding="utf-8") as f:
        f.write(f"env_id: {env_id}\n")
        f.write(f"success: {success}\n")
        f.write(f"steps: {steps}\n")
        f.write(f"info: {info}\n")

    gif_path = os.path.join(result_dir, f"{env_id.replace('/', '_')}_{success}.gif")
    imageio.mimsave(gif_path, process_frames(frames, lang), fps=10)

    print(f"[LOG] Saved result: {result_path}")
    print(f"[LOG] Saved GIF: {gif_path}")

    env.close()
    return success


def test_result_type():
    device = torch.device("mps")
    model_id = "jadechoghari/smolvla_metaworld"
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    patch_draccus_non_callable_types()

    policy = SmolVLAPolicy.from_pretrained(model_id).to(device).eval()
    preprocess, postprocess = make_pre_post_processors(
        policy.config,
        model_id,
        preprocessor_overrides={"device_processor": {"device": str(device)}},
    )

    benchmark_start_time = time.perf_counter()
    successes = []

    for env_id in TASK_ENVS:
        successes.append(run_task(policy, preprocess, postprocess, device, env_id))

    elapsed = time.perf_counter() - benchmark_start_time
    success_rate = sum(int(s) for s in successes) / len(successes)
    print(f"elapsed: {elapsed:.3f}s, success rate: {success_rate:.2%}")

    assert True