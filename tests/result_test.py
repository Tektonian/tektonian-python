from abc import ABC
import random

from tt.base.result.result import ResultType
from tt.base.instantiate.extensions import (
    register_singleton,
    get_singleton_service_descriptors,
)
from tt import simulation, Environment

import os
import torch
from lerobot.policies.factory import make_pre_post_processors
from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
import numpy as np
import time


def libero_to_smolvla_obs(obs, lang, device) -> dict:
    # ref: https://huggingface.co/docs/lerobot/en/env_processor
    # Extract components similar to _process_observation
    eef_pos = torch.tensor(obs['robot0_eef_pos'], device=device, dtype=torch.float32)  # 3D
    quat = torch.tensor(obs['robot0_eef_quat'], device=device, dtype=torch.float32)    # 4D
    # Convert quaternion to axis-angle
    def quat2axisangle(q):
        # q: (..., 4)
        norm_q = q / q.norm(dim=-1, keepdim=True)
        w, xyz = norm_q[..., 0], norm_q[..., 1:]
        angle = 2 * torch.acos(torch.clamp(w, -1.0, 1.0))
        s = torch.sqrt(1 - w ** 2)
        axis = torch.where(s.unsqueeze(-1) < 1e-6, torch.zeros_like(xyz), xyz / s.unsqueeze(-1))
        return axis * angle.unsqueeze(-1)
    eef_axisangle = quat2axisangle(quat)  # 3D
    gripper = torch.tensor(obs['robot0_gripper_qpos'], device=device, dtype=torch.float32)  # 2D
    state = torch.cat([eef_pos, eef_axisangle, gripper], dim=-1)  # 8D
    def normalize_image(img):
        img = torch.tensor(img, device=device, dtype=torch.float32) / 255.0
        if img.ndim == 3 and img.shape[2] == 3:  # HWC
            img = img.permute(2, 0, 1)  # CHW
        return img
    agentview_img = normalize_image(obs['agentview_image'])
    eye_in_hand_img = normalize_image(obs['robot0_eye_in_hand_image'])
    return {
        "observation.images.image": agentview_img,
        "observation.images.image2": eye_in_hand_img,
        "observation.state": state,
        "task": lang,
    }

def test_result_type(debug=True):
    device = torch.device("mps")  # Set device to Apple Silicon GPU
    # Load SmolVLA policy from HuggingFace ------------------
    MODEL_ID = "HuggingFaceVLA/smolvla_libero"
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")  # Avoid tokenizer parallelism warning

    policy = SmolVLAPolicy.from_pretrained(MODEL_ID).to(device).eval()  # Load and prepare policy
    preprocess, postprocess = make_pre_post_processors(
        policy.config,
        MODEL_ID,
        preprocessor_overrides={"device_processor": {"device": str(device)}},
    )
    # -------------------------------------------------------

    print(get_singleton_service_descriptors()[0][1].ctor())  # Debug: print a singleton service
    print(simulation)  # Debug: print simulation module

    # Create environment
    env = Environment(
        name="LIBERO/libero_spatial", 
        compatibility_date="2026-02-09", 
        task_id="0",
        control_mode="ee_pose", # 7D action: (x, y, z) + axis-angle(3D) + gripper(1D)
        camera_spec={"heights": 256, "widths": 256},
        max_steps=10
    )

    max_episodes = 2  # Number of episodes to run
    successes = 0  # Track number of successful episodes
    for episode in range(max_episodes):
        obs, lang = env.reset()  # Reset environment and get initial observation and language
        done = False
        steps = 0
        episode_success = False

        while not done:
            # Preprocess observation for the policy
            batch_input = libero_to_smolvla_obs(obs, lang, device)
            batch = preprocess(batch_input)

            # Get action from policy
            if debug:
                t0 = time.perf_counter()
            with torch.inference_mode():
                pred_action = policy.select_action(batch)
            if debug:
                t1 = time.perf_counter()
                print(f"[DEBUG] Inference time: {t1 - t0:.6f} seconds")

            # Postprocess action and step environment
            action = postprocess(pred_action)
            if debug:
                t2 = time.perf_counter()
            obs, reward, done, info = env.step(action)
            if debug:
                t3 = time.perf_counter()
                print(f"[DEBUG] Step time: {t3 - t2:.6f} seconds")
            episode_success = episode_success or info.get("success", False)  # Track success

            steps += 1
            
            print(f"Episode {episode + 1} Step {steps} done: {done} info: {info}")

        successes += int(episode_success)  # Increment successes if episode was successful

    # Calculate and print success rate
    success_rate = successes / max_episodes
    print(f"Success rate: {success_rate:.2%} ({successes}/{max_episodes})")

    env.close()  # Clean up environment

if __name__ == "__main__":
    test_result_type()
