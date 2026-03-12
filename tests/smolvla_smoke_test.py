import os
import json
from pathlib import Path
from typing import Any

import torch
from huggingface_hub import snapshot_download

# ✅ lerobot 0.4.x에서의 SmolVLA import 경로 (공식 예제와 동일)
from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
from lerobot.policies.factory import make_pre_post_processors


def patch_draccus_non_callable_types() -> None:
    """
    Python 3.14에서 argparse가 non-callable `type=`(예: Dict[...] | None)을
    엄격히 거부해서 draccus config 파싱이 깨지는 문제를 우회한다.
    """
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


def mps_mem(tag: str):
    if torch.backends.mps.is_available():
        cur = torch.mps.current_allocated_memory() / 1024**2
        drv = torch.mps.driver_allocated_memory() / 1024**2
        print(f"[{tag}] MPS current={cur:.1f} MB | driver={drv:.1f} MB")


def read_shapes_from_policy_preprocessor(repo_dir: Path):
    """
    policy_preprocessor.json이 있으면 거기서 image/state/action shape를 읽고,
    없으면 (3,256,256), state=8, action=7로 fallback.
    이미지가 없을 수도 있으니 None으로 반환.
    """
    pp = repo_dir / "policy_preprocessor.json"
    if not pp.exists():
        Warning(f"policy_preprocessor.json not found in {repo_dir}, using default shapes")
        return None, None, None, None

    data = json.loads(pp.read_text())
    img_shapes = []
    st = None
    act = None
    for step in data.get("steps", []):
        if step.get("registry_name") == "normalizer_processor":
            feats = step.get("config", {}).get("features", {})
            for k, v in feats.items():
                if k.startswith("observation.images."):
                    shape = v.get("shape", None)
                    if shape is not None:
                        img_shapes.append(tuple(shape))
            st = feats.get("observation.state", {}).get("shape", [8])
            act = feats.get("action", {}).get("shape", [7])
            break

    return dict(image=img_shapes if len(img_shapes) > 0 else None,
                state=tuple(st) if st is not None else None,
                action=tuple(act) if act is not None else None)


def main():
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    patch_draccus_non_callable_types()

    # model_id = "HuggingFaceVLA/smolvla_libero"
    model_id = "jadechoghari/smolvla_metaworld"

    # ✅ macOS면 mps 우선
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    
    dtype = torch.float32

    print("device:", device, "dtype:", dtype)

    # 1) repo 다운로드(로컬에서 policy_preprocessor/config 확인용)
    local_dir = Path(snapshot_download(repo_id=model_id))
    shapes = read_shapes_from_policy_preprocessor(local_dir)
    print("expected shapes:", shapes)

    mps_mem("before load")

    # 2) policy 로드
    model = SmolVLAPolicy.from_pretrained(model_id).to(device=device, dtype=dtype).eval()

    # 3) 전/후처리 생성
    #    ✅ 공식 예제에서 MPS 사용 시 device_processor를 override 하라고 안내
    #       (안 하면 기본이 CUDA로 잡히는 경우가 있어 device mismatch 발생 가능)
    preprocess, postprocess = make_pre_post_processors(
        model.config,
        model_id,
        preprocessor_overrides={"device_processor": {"device": str(device)}},
    )
    print(preprocess)

    # ✅ LeRobot preprocessor는 "batch" 형식(평탄화된 observation.* 키)을 받음
    
    # Create a dummy batch for Libero 
    # batch = {
    #     "observation.images.image": torch.zeros(*img1_shape, device=device, dtype=dtype),
    #     "observation.images.image2": torch.zeros(*img2_shape, device=device, dtype=dtype),
    #     "observation.state": torch.zeros(state_dim, device=device, dtype=dtype),
    #     # SmolVLA tokenizer preprocessor requires complementary_data["task"].
    #     "task": "pick up the object",
    # }

    # Create a dummy batch for Metaworld
    batch = {
        "observation.image": torch.zeros((3,480,480), device=device, dtype=dtype),
        "observation.state": torch.zeros(*shapes["state"], device=device, dtype=dtype),
        "task": "pick up the object",
    }
    
    obs_proc = preprocess(batch)

    mps_mem("after preprocess")

    with torch.inference_mode():
        # ✅ SmolVLA 정책은 예제에서 select_action()을 사용
        action = model.select_action(obs_proc)
        # ✅ 하지만 내부적으로는 predict_action_chunk()이 실제 forward를 담당하므로, 직접 호출해보기도 함
        chunks = model.predict_action_chunk(obs_proc)
        

    action = postprocess(action)

    mps_mem("after forward")

    # 출력 형태 정리
    if isinstance(action, dict):
        print("action keys:", list(action.keys()))
        a = action.get("action", None)
        print("action['action']:", a)
        if hasattr(a, "shape"):
            print("shape:", tuple(a.shape))
    else:
        print("action:", action)
        if hasattr(action, "shape"):
            print("shape:", tuple(action.shape))


if __name__ == "__main__":
    main()
