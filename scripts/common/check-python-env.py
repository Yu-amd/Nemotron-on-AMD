#!/usr/bin/env python3
"""Inspect the current Python interpreter. Read-only. No installs."""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from datetime import datetime, timezone


PACKAGES = [
    "torch",
    "transformers",
    "accelerate",
    "safetensors",
    "tokenizers",
    "vllm",
    "huggingface_hub",
    "sentencepiece",
    "sentence_transformers",
    "openai",
    "numpy",
]


def pkg_version(name: str):
    try:
        mod = __import__(name)
    except Exception as exc:  # noqa: BLE001
        return {"present": False, "error": f"{type(exc).__name__}: {exc}"}
    version = getattr(mod, "__version__", None)
    return {"present": True, "version": version, "file": getattr(mod, "__file__", None)}


def torch_details():
    try:
        import torch
    except Exception as exc:  # noqa: BLE001
        return {"present": False, "error": f"{type(exc).__name__}: {exc}"}

    info = {
        "present": True,
        "version": torch.__version__,
        "hip": getattr(torch.version, "hip", None),
        "cuda": getattr(torch.version, "cuda", None),
        "cuda_is_available": bool(torch.cuda.is_available()),
        "device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
        "devices": [],
        "warning": None,
    }
    if info["cuda"] and not info["hip"]:
        info["warning"] = (
            "This torch build exposes CUDA and not HIP. It is likely an NVIDIA wheel, "
            "not a ROCm/HIP wheel. Do not treat it as an AMD validation stack."
        )
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            entry = {"index": i, "name": torch.cuda.get_device_name(i)}
            try:
                props = torch.cuda.get_device_properties(i)
                entry["total_memory_bytes"] = int(props.total_memory)
            except Exception as exc:  # noqa: BLE001
                entry["properties_error"] = f"{type(exc).__name__}: {exc}"
            info["devices"].append(entry)
    return info


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect the current Python / ML environment.")
    parser.add_argument("--output", help="Write JSON to this path in addition to stdout.")
    args = parser.parse_args()

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "packages": {name: pkg_version(name.replace("-", "_")) for name in PACKAGES},
        "torch": torch_details(),
        "env": {
            key: os.environ.get(key)
            for key in sorted(os.environ)
            if key.startswith(
                ("ROCM", "HIP", "HSA", "CUDA", "HF_", "TRANSFORMERS_", "TORCH_", "VLLM_", "PYTORCH_")
            )
        },
    }

    text = json.dumps(report, indent=2, default=str)
    print(text)
    if args.output:
        parent = os.path.dirname(os.path.abspath(args.output))
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
