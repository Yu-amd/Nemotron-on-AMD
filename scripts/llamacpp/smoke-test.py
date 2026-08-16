#!/usr/bin/env python3
"""Greedy llama.cpp smoke test. Isolated from Transformers / vLLM.

Usage:
  python3 scripts/llamacpp/smoke-test.py \
    --llama-cli tools/llamacpp/releases/b10453/cpu/llama-cli \
    --model tools/llamacpp/gguf/NVIDIA-Nemotron3-Nano-4B-Q4_K_M.gguf \
    --n-gpu-layers 0 \
    --platform ryzen-ai \
    --output-dir results/ryzen-ai/<run-id>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_PROMPTS = Path(__file__).resolve().parents[2] / "prompts" / "smoke-tests.json"
MAX_CAPTURE_BYTES = 2_000_000


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)
        handle.write("\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify_failure(text: str) -> str:
    lowered = text.lower()
    if any(tok in lowered for tok in ("out of memory", "oom", "failed to allocate", "vk_error_out_of_device_memory")):
        return "MEMORY"
    if "unknown model architecture" in lowered:
        return "MODEL ARCHITECTURE"
    if "ggml_vulkan" in lowered and "error" in lowered:
        return "KERNEL"
    if any(tok in lowered for tok in ("rocm", "hip", "hsa", "amdgpu")) and "error" in lowered:
        return "ROCM"
    if "tokenizer" in lowered:
        return "TOKENIZER"
    if "chat-template" in lowered or "jinja" in lowered:
        return "CHAT TEMPLATE"
    return "OTHER"


def detect_backend(text: str) -> str:
    if re.search(r"ggml_vulkan:\s+Found\s+\d+\s+Vulkan", text) or "Vulkan0" in text or "RADV" in text:
        return "vulkan"
    if re.search(r"ggml_cuda_init: found \d+ ROCm", text) or "using device ROCm" in text:
        return "hip"
    if "CPU :" in text or "n-gpu-layers 0" in text:
        return "cpu"
    return "unknown"


def llama_version(cli: Path) -> str:
    try:
        proc = subprocess.run(
            [str(cli), "--version"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        blob = (proc.stdout or "") + "\n" + (proc.stderr or "")
        return blob.strip()[:2000]
    except Exception as exc:  # noqa: BLE001
        return f"{type(exc).__name__}: {exc}"


def user_text(prompt: dict) -> str:
    messages = prompt.get("messages") or []
    parts = [str(m.get("content") or "") for m in messages if m.get("role") == "user"]
    return "\n".join(parts).strip()


def extract_generation(stdout: str, user: str) -> str:
    """Pull the assistant reply from llama-cli single-turn chat output."""
    timings = stdout.find("\n[ Prompt:")
    if timings < 0:
        timings = stdout.find("\nExiting...")
    region = stdout[:timings] if timings >= 0 else stdout
    trunc_token = " ... (truncated)\n"
    trunc = region.find(trunc_token)
    if trunc >= 0:
        return region[trunc + len(trunc_token) :].strip()
    needle = f"> {user}"
    idx = region.find(needle)
    if idx >= 0:
        return region[idx + len(needle) :].strip()
    prompt_at = region.find("\n> ")
    if prompt_at < 0:
        prompt_at = region.find("> ")
        if prompt_at < 0:
            return ""
        rest = region[prompt_at:]
    else:
        rest = region[prompt_at + 1 :]
    newline = rest.find("\n")
    if newline < 0:
        return ""
    return rest[newline + 1 :].strip()


def run_one(
    *,
    cli: Path,
    model: Path,
    prompt: dict,
    n_gpu_layers: int,
    n_predict: int,
    ctx: int,
    timeout: int,
    extra_args: list[str],
) -> dict:
    user = user_text(prompt)
    cmd = [
        str(cli),
        "--model",
        str(model),
        "--n-gpu-layers",
        str(n_gpu_layers),
        "--ctx-size",
        str(ctx),
        "--n-predict",
        str(n_predict),
        "--temp",
        "0",
        "--seed",
        "1",
        "--no-display-prompt",
        "--single-turn",
        "--no-warmup",
        "--jinja",
        "--chat-template-kwargs",
        '{"enable_thinking":false}',
        "--system-prompt",
        "You are a helpful assistant. Do not write a reasoning trace.",
        "-p",
        user,
    ]
    cmd.extend(extra_args)
    started = time.perf_counter()
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    elapsed = time.perf_counter() - started
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    combined = stdout + "\n" + stderr
    if len(stdout) > MAX_CAPTURE_BYTES or len(stderr) > MAX_CAPTURE_BYTES:
        return {
            "id": prompt.get("id"),
            "task": prompt.get("task"),
            "prompt": user,
            "expect": prompt.get("expect"),
            "command": cmd,
            "returncode": proc.returncode,
            "elapsed_sec": elapsed,
            "generation": "",
            "stdout_tail": stdout[-4000:],
            "stderr_tail": stderr[-4000:],
            "backend_hint": detect_backend(combined),
            "failure_class": "OTHER",
            "error": "captured output exceeded 2 MiB (likely interactive prompt loop)",
        }
    generation = extract_generation(stdout, user) if proc.returncode == 0 else ""
    return {
        "id": prompt.get("id"),
        "task": prompt.get("task"),
        "prompt": user,
        "expect": prompt.get("expect"),
        "command": cmd,
        "returncode": proc.returncode,
        "elapsed_sec": elapsed,
        "generation": generation,
        "stdout_tail": stdout[-8000:],
        "stderr_tail": stderr[-8000:],
        "backend_hint": detect_backend(combined),
        "failure_class": None if proc.returncode == 0 and generation else classify_failure(combined),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="llama.cpp greedy smoke test.")
    parser.add_argument("--llama-cli", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--platform", required=True, help="ryzen-ai or mi300x")
    parser.add_argument("--repo", default="nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF")
    parser.add_argument("--revision", default="")
    parser.add_argument("--n-gpu-layers", type=int, default=0)
    parser.add_argument("--n-predict", type=int, default=96)
    parser.add_argument("--ctx-size", type=int, default=4096)
    parser.add_argument("--prompts", default=str(DEFAULT_PROMPTS))
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--llama-arg", action="append", default=[], help="extra llama-cli args")
    args = parser.parse_args()

    cli = Path(args.llama_cli).resolve()
    model = Path(args.model).resolve()
    out_dir = Path(args.output_dir)
    log_dir = out_dir / "logs"
    llamacpp_dir = out_dir / "llamacpp"
    log_dir.mkdir(parents=True, exist_ok=True)
    llamacpp_dir.mkdir(parents=True, exist_ok=True)

    if not cli.is_file():
        print(f"ERROR: llama-cli not found: {cli}", file=sys.stderr)
        return 2
    if not model.is_file():
        print(f"ERROR: GGUF not found: {model}", file=sys.stderr)
        return 2

    prompts = json.loads(Path(args.prompts).read_text(encoding="utf-8"))["prompts"]
    version = llama_version(cli)
    model_sha = sha256_file(model)
    extra = list(args.llama_arg)

    results = []
    any_fail = False
    backends = set()
    for prompt in prompts:
        print(f"running {prompt.get('id')} …", flush=True)
        try:
            one = run_one(
                cli=cli,
                model=model,
                prompt=prompt,
                n_gpu_layers=args.n_gpu_layers,
                n_predict=args.n_predict,
                ctx=args.ctx_size,
                timeout=args.timeout,
                extra_args=extra,
            )
        except subprocess.TimeoutExpired as exc:
            any_fail = True
            one = {
                "id": prompt.get("id"),
                "task": prompt.get("task"),
                "prompt": user_text(prompt),
                "expect": prompt.get("expect"),
                "returncode": -1,
                "elapsed_sec": args.timeout,
                "generation": "",
                "stdout_tail": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
                "stderr_tail": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
                "backend_hint": "unknown",
                "failure_class": "OTHER",
                "error": "TimeoutExpired",
            }
        hint = one.get("backend_hint") or "unknown"
        if hint == "unknown":
            hint = "cpu" if args.n_gpu_layers == 0 else "gpu-offload"
            one["backend_hint"] = hint
        backends.add(hint)
        if one.get("returncode") != 0 or not one.get("generation"):
            any_fail = True
        results.append(one)
        (log_dir / f"llama-{one.get('id')}.stdout.log").write_text(one.get("stdout_tail") or "", encoding="utf-8")
        (log_dir / f"llama-{one.get('id')}.stderr.log").write_text(one.get("stderr_tail") or "", encoding="utf-8")

    smoke_result = "FAIL" if any_fail else "PASS"
    payload = {
        "timestamp_utc": utcnow(),
        "result": smoke_result,
        "platform": args.platform,
        "runtime": "llama.cpp",
        "llama_cli": str(cli),
        "llama_version": version,
        "model_path": str(model),
        "model_repo": args.repo,
        "model_revision": args.revision,
        "model_bytes": model.stat().st_size,
        "model_sha256": model_sha,
        "n_gpu_layers": args.n_gpu_layers,
        "n_predict": args.n_predict,
        "ctx_size": args.ctx_size,
        "enable_thinking": False,
        "backend_hints": sorted(backends),
        "prompts_path": args.prompts,
        "generations": results,
    }
    write_json(llamacpp_dir / "result.json", payload)

    metadata = {
        "date": utcnow(),
        "platform": args.platform,
        "model": args.repo,
        "model_revision": args.revision,
        "precision": "GGUF",
        "runtime": "llama.cpp",
        "runtime_version": version.splitlines()[0] if version else "",
        "result": smoke_result,
        "n_gpu_layers": args.n_gpu_layers,
        "backend_hints": sorted(backends),
        "model_sha256": model_sha,
        "notes": "llama.cpp greedy smoke. Not an Optimized or Production-ready claim. Not Transformers/vLLM.",
        "command": [
            "scripts/llamacpp/smoke-test.py",
            "--llama-cli",
            str(cli),
            "--model",
            str(model),
            "--n-gpu-layers",
            str(args.n_gpu_layers),
            "--platform",
            args.platform,
            "--output-dir",
            str(out_dir),
        ],
        "enable_thinking": False,
        "status_claim_allowed": "Runs (candidate) — not Validated until results are reviewed"
        if smoke_result == "PASS"
        else "FAIL",
    }
    write_json(out_dir / "run-metadata.json", metadata)
    print(json.dumps({"result": smoke_result, "n": len(results), "backends": sorted(backends)}, indent=2))
    return 0 if smoke_result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
