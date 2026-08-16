#!/usr/bin/env python3
"""Nemotron Transformers smoke test for AMD Instinct / ROCm PyTorch.

Goal: MODEL LOADS → MODEL GENERATES → output is captured reproducibly.

This is not a performance benchmark and is not a production-readiness test.

Usage:
  python scripts/mi300x/transformers-smoke-test.py \
    --model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
    --output-dir results/mi300x/<run-id>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_PROMPTS = Path(__file__).resolve().parents[2] / "prompts" / "smoke-tests.json"
OFFICIAL_NANO_BF16 = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(_SCRIPTS_DIR / "common") not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR / "common"))
from hf_revision import cached_snapshot_hash  # noqa: E402


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)
        handle.write("\n")


def peek_memory():
    try:
        import torch

        if not torch.cuda.is_available():
            return {"available": False}
        torch.cuda.synchronize()
        return {
            "available": True,
            "allocated_bytes": int(torch.cuda.memory_allocated()),
            "reserved_bytes": int(torch.cuda.memory_reserved()),
            "max_allocated_bytes": int(torch.cuda.max_memory_allocated()),
            "max_reserved_bytes": int(torch.cuda.max_memory_reserved()),
        }
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def classify_failure(exc: BaseException) -> str:
    text = f"{type(exc).__name__}: {exc}".lower()
    if "out of memory" in text or "hiperroroutofmemory" in text or "oom" in text:
        return "MEMORY"
    if "tokenizer" in text:
        return "TOKENIZER"
    if "chat_template" in text or "jinja" in text:
        return "CHAT TEMPLATE"
    if "trust_remote_code" in text or "remote code" in text:
        return "CUSTOM CODE"
    if "vllm" in text:
        return "VLLM"
    if any(token in text for token in ("rocm", "hip", "hsa", "amdgpu")):
        return "ROCM"
    if "torch" in text or "cuda" in text:
        return "PYTORCH"
    if "transformers" in text or "mamba" in text or "moe" in text:
        return "TRANSFORMERS"
    if "architecture" in text or "config" in text:
        return "MODEL ARCHITECTURE"
    return "OTHER"


def load_prompts(path: Path, names: list[str] | None) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    prompts = data["prompts"] if isinstance(data, dict) and "prompts" in data else data
    if names:
        wanted = set(names)
        prompts = [p for p in prompts if p.get("id") in wanted]
    return prompts


def apply_chat_template(tokenizer, messages, enable_thinking: bool, trust_remote_code: bool):
    kwargs = {
        "tokenize": True,
        "add_generation_prompt": True,
        "return_tensors": "pt",
    }
    # Official Nemotron 3 Nano card: enable_thinking is a chat-template flag.
    # If this tokenizer does not accept it, record that and retry without it.
    notes = {"enable_thinking_accepted": True}
    try:
        encoded = tokenizer.apply_chat_template(
            messages, enable_thinking=enable_thinking, **kwargs
        )
    except TypeError:
        encoded = tokenizer.apply_chat_template(messages, **kwargs)
        notes["enable_thinking_accepted"] = False
    notes["apply_chat_template_type"] = type(encoded).__name__
    return encoded, notes


def to_input_ids_tensor(encoded):
    """Transformers 5.x may return a BatchEncoding instead of a Tensor.

    First MI300X FAIL (2026-08-15_172557Z) was AttributeError on encoded.shape
    after a successful model load. That log is preserved. This unwrap is the
    single justified harness fix.
    """
    obj = encoded
    if hasattr(obj, "keys"):
        try:
            if "input_ids" in obj:
                obj = obj["input_ids"]
        except Exception:
            pass
    if hasattr(obj, "input_ids") and not hasattr(obj, "shape"):
        try:
            obj = obj.input_ids
        except Exception:
            pass
    if not hasattr(obj, "shape"):
        raise TypeError(f"apply_chat_template returned {type(encoded).__name__} without a tensor shape")
    return obj


def main() -> int:
    parser = argparse.ArgumentParser(description="Transformers smoke test for Nemotron on ROCm.")
    parser.add_argument("--model", default=OFFICIAL_NANO_BF16)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--prompts", default=str(DEFAULT_PROMPTS))
    parser.add_argument("--prompt-ids", nargs="*", default=None)
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="0 uses greedy decoding. NVIDIA Nano reasoning-on recipe uses 1.0; this smoke test is correctness-first.",
    )
    parser.add_argument(
        "--enable-thinking",
        action="store_true",
        help="Pass enable_thinking=True into the chat template. Default is False for deterministic smoke tests.",
    )
    parser.add_argument("--trust-remote-code", action="store_true")
    parser.add_argument(
        "--device",
        default="cuda:0",
        help="Torch device. ROCm builds typically use the torch.cuda namespace.",
    )
    parser.add_argument("--dtype", default="bfloat16")
    parser.add_argument("--revision", default=None)
    args = parser.parse_args()
    if not args.revision:
        args.revision = cached_snapshot_hash(args.model)
        if args.revision:
            print(f"using cached snapshot revision={args.revision}")

    out_dir = Path(args.output_dir)
    transformers_dir = out_dir / "transformers"
    logs_dir = out_dir / "logs"
    transformers_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_path = logs_dir / "transformers-smoke-test.log"

    class Tee:
        def __init__(self, *streams):
            self.streams = streams

        def write(self, data):
            for stream in self.streams:
                stream.write(data)
                stream.flush()

        def flush(self):
            for stream in self.streams:
                stream.flush()

    log_handle = log_path.open("w", encoding="utf-8")
    sys.stdout = Tee(sys.__stdout__, log_handle)
    sys.stderr = Tee(sys.__stderr__, log_handle)

    metadata = {
        "date": utcnow(),
        "platform": "mi300x",
        "gpu": None,
        "model": args.model,
        "model_revision": args.revision,
        "precision": args.dtype,
        "runtime": "transformers",
        "runtime_version": None,
        "rocm_version": None,
        "pytorch_version": None,
        "result": "NOT TESTED",
        "notes": (
            "Transformers smoke test. This is not an Optimized or Production-ready claim. "
            "NVIDIA Nano BF16 was selected as the first load/generate validation target."
        ),
        "command": sys.argv,
        "enable_thinking": args.enable_thinking,
        "trust_remote_code_requested": args.trust_remote_code,
        "trust_remote_code_required": "Unknown / requires validation",
        "custom_remote_code": "Unknown / requires validation",
    }
    result_payload = {
        "metadata": metadata,
        "environment": {},
        "load": {},
        "generations": [],
        "summary": {},
    }

    try:
        import torch
        from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer, __version__ as transformers_version
    except Exception as exc:  # noqa: BLE001
        metadata["result"] = "FAIL"
        result_payload["summary"] = {
            "success": False,
            "failure_layer": classify_failure(exc),
            "error": f"{type(exc).__name__}: {exc}",
        }
        write_json(transformers_dir / "result.json", result_payload)
        write_json(out_dir / "run-metadata.json", metadata)
        print(traceback.format_exc())
        return 1

    dtype_map = {
        "bfloat16": torch.bfloat16,
        "bf16": torch.bfloat16,
        "float16": torch.float16,
        "fp16": torch.float16,
        "float32": torch.float32,
    }
    if args.dtype not in dtype_map:
        print(f"unsupported dtype: {args.dtype}", file=sys.stderr)
        return 2
    torch_dtype = dtype_map[args.dtype]

    env = {
        "python": sys.version,
        "executable": sys.executable,
        "torch_version": torch.__version__,
        "torch_hip": getattr(torch.version, "hip", None),
        "torch_cuda_build": getattr(torch.version, "cuda", None),
        "transformers_version": transformers_version,
        "cuda_is_available": bool(torch.cuda.is_available()),
        "device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
        "device_names": [],
        "cuda_build_without_hip": bool(getattr(torch.version, "cuda", None) and not getattr(torch.version, "hip", None)),
    }
    if env["cuda_is_available"]:
        env["device_names"] = [torch.cuda.get_device_name(i) for i in range(env["device_count"])]
        metadata["gpu"] = env["device_names"][0] if env["device_names"] else None
    metadata["pytorch_version"] = torch.__version__
    metadata["runtime_version"] = transformers_version
    metadata["rocm_version"] = getattr(torch.version, "hip", None)
    result_payload["environment"] = env

    if env["cuda_build_without_hip"]:
        metadata["result"] = "BLOCKED"
        result_payload["summary"] = {
            "success": False,
            "failure_layer": "PYTORCH",
            "error": "Installed torch looks like a CUDA build, not ROCm/HIP. Refusing to treat this as AMD validation.",
        }
        write_json(transformers_dir / "result.json", result_payload)
        write_json(out_dir / "run-metadata.json", metadata)
        print(result_payload["summary"]["error"], file=sys.stderr)
        return 1

    if not env["cuda_is_available"]:
        metadata["result"] = "FAIL"
        result_payload["summary"] = {
            "success": False,
            "failure_layer": "ROCM",
            "error": "torch.cuda.is_available() is False. On ROCm builds this usually means HIP cannot see a GPU.",
        }
        write_json(transformers_dir / "result.json", result_payload)
        write_json(out_dir / "run-metadata.json", metadata)
        print(result_payload["summary"]["error"], file=sys.stderr)
        return 1

    print(f"model={args.model}")
    print(f"device={args.device}")
    print(f"dtype={args.dtype}")
    print(f"transformers={transformers_version}")
    print(f"torch={torch.__version__} hip={env['torch_hip']}")
    print(f"gpu={metadata['gpu']}")

    trust_remote_code = args.trust_remote_code
    config_notes = {}
    try:
        config = AutoConfig.from_pretrained(
            args.model,
            revision=args.revision,
            trust_remote_code=trust_remote_code,
        )
        config_notes["model_type"] = getattr(config, "model_type", None)
        config_notes["architectures"] = getattr(config, "architectures", None)
        config_notes["auto_map"] = getattr(config, "auto_map", None)
        config_notes["max_position_embeddings"] = getattr(config, "max_position_embeddings", None)
        if config_notes["auto_map"]:
            metadata["custom_remote_code"] = "likely required (config.auto_map present)"
        else:
            metadata["custom_remote_code"] = "not indicated by config.auto_map"
            metadata["trust_remote_code_required"] = "probably no for current Transformers, still recorded from load path"
    except Exception as exc:  # noqa: BLE001
        if (not trust_remote_code) and "trust_remote_code" in str(exc).lower():
            print("config load failed without trust_remote_code; retrying with trust_remote_code=True")
            trust_remote_code = True
            metadata["trust_remote_code_required"] = True
            metadata["custom_remote_code"] = "required for AutoConfig"
            config = AutoConfig.from_pretrained(
                args.model,
                revision=args.revision,
                trust_remote_code=True,
            )
            config_notes["model_type"] = getattr(config, "model_type", None)
            config_notes["architectures"] = getattr(config, "architectures", None)
            config_notes["retry_trust_remote_code"] = True
        else:
            metadata["result"] = "FAIL"
            result_payload["summary"] = {
                "success": False,
                "failure_layer": classify_failure(exc),
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            }
            write_json(transformers_dir / "result.json", result_payload)
            write_json(out_dir / "run-metadata.json", metadata)
            print(traceback.format_exc())
            return 1

    result_payload["load"]["config"] = config_notes
    if not metadata.get("model_revision"):
        metadata["model_revision"] = getattr(config, "_commit_hash", None) or args.revision

    print("loading tokenizer...")
    tok_started = time.perf_counter()
    try:
        tokenizer = AutoTokenizer.from_pretrained(
            args.model,
            revision=args.revision,
            trust_remote_code=trust_remote_code,
        )
    except Exception as exc:  # noqa: BLE001
        if (not trust_remote_code) and "trust_remote_code" in str(exc).lower():
            trust_remote_code = True
            metadata["trust_remote_code_required"] = True
            tokenizer = AutoTokenizer.from_pretrained(
                args.model,
                revision=args.revision,
                trust_remote_code=True,
            )
        else:
            metadata["result"] = "FAIL"
            result_payload["summary"] = {
                "success": False,
                "failure_layer": "TOKENIZER",
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            }
            write_json(transformers_dir / "result.json", result_payload)
            write_json(out_dir / "run-metadata.json", metadata)
            print(traceback.format_exc())
            return 1
    tok_elapsed = time.perf_counter() - tok_started
    result_payload["load"]["tokenizer_sec"] = tok_elapsed
    result_payload["load"]["tokenizer_name_or_path"] = args.model
    print(f"tokenizer loaded in {tok_elapsed:.2f}s")

    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.empty_cache()

    print("loading model...")
    load_started = time.perf_counter()
    mem_before = peek_memory()
    try:
        model = AutoModelForCausalLM.from_pretrained(
            args.model,
            revision=args.revision,
            torch_dtype=torch_dtype,
            trust_remote_code=trust_remote_code,
            low_cpu_mem_usage=True,
        )
        model.to(args.device)
        model.eval()
    except Exception as exc:  # noqa: BLE001
        metadata["result"] = "FAIL"
        result_payload["load"]["memory_before"] = mem_before
        result_payload["load"]["memory_after_failure"] = peek_memory()
        result_payload["summary"] = {
            "success": False,
            "failure_layer": classify_failure(exc),
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }
        write_json(transformers_dir / "result.json", result_payload)
        write_json(out_dir / "run-metadata.json", metadata)
        print(traceback.format_exc())
        return 1
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    load_elapsed = time.perf_counter() - load_started
    mem_after_load = peek_memory()
    result_payload["load"].update(
        {
            "model_load_sec": load_elapsed,
            "memory_before": mem_before,
            "memory_after_load": mem_after_load,
            "trust_remote_code_used": trust_remote_code,
        }
    )
    metadata["trust_remote_code_required"] = bool(trust_remote_code and args.trust_remote_code) or (
        trust_remote_code and not args.trust_remote_code
    )
    if not args.trust_remote_code and not trust_remote_code:
        metadata["trust_remote_code_required"] = False
    print(f"model loaded in {load_elapsed:.2f}s")
    print(f"memory_after_load={mem_after_load}")

    prompts = load_prompts(Path(args.prompts), args.prompt_ids)
    failures = 0
    for item in prompts:
        prompt_id = item.get("id", "unnamed")
        messages = item.get("messages")
        if messages is None:
            messages = [{"role": "user", "content": item["prompt"]}]
        enable_thinking = bool(item["enable_thinking"]) if "enable_thinking" in item else args.enable_thinking
        temperature = float(item["temperature"]) if "temperature" in item else args.temperature
        top_p = item.get("top_p")
        do_sample = item.get("do_sample")
        max_new_tokens = int(item.get("max_new_tokens", args.max_new_tokens))
        print(f"\n=== prompt {prompt_id} thinking={enable_thinking} temp={temperature} ===")
        record = {
            "id": prompt_id,
            "messages": messages,
            "enable_thinking": enable_thinking,
            "success": False,
        }
        try:
            encoded, tmpl_notes = apply_chat_template(
                tokenizer, messages, enable_thinking, trust_remote_code
            )
            record["chat_template"] = tmpl_notes
            encoded = to_input_ids_tensor(encoded).to(args.device)
            input_len = int(encoded.shape[-1])
            gen_kwargs = {
                "max_new_tokens": max_new_tokens,
                "eos_token_id": tokenizer.eos_token_id,
            }
            sample = bool(do_sample) if do_sample is not None else temperature > 0
            if not sample:
                gen_kwargs.update({"do_sample": False, "num_beams": 1})
            else:
                gen_kwargs.update({"do_sample": True, "temperature": temperature})
                if top_p is not None:
                    gen_kwargs["top_p"] = float(top_p)

            if torch.cuda.is_available():
                torch.cuda.synchronize()
            gen_started = time.perf_counter()
            with torch.inference_mode():
                outputs = model.generate(encoded, **gen_kwargs)
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            gen_elapsed = time.perf_counter() - gen_started
            generated_ids = outputs[0][input_len:]
            text = tokenizer.decode(generated_ids, skip_special_tokens=False)
            text_clean = tokenizer.decode(generated_ids, skip_special_tokens=True)
            output_len = int(generated_ids.shape[-1])
            tps = (output_len / gen_elapsed) if gen_elapsed > 0 else None
            record.update(
                {
                    "success": True,
                    "prompt_text": messages[-1]["content"] if messages else None,
                    "generated_text_raw": text,
                    "generated_text": text_clean,
                    "input_tokens": input_len,
                    "output_tokens": output_len,
                    "generation_sec": gen_elapsed,
                    "output_tokens_per_sec": tps,
                    "max_new_tokens": max_new_tokens,
                    "temperature": temperature,
                    "do_sample": sample,
                    "top_p": top_p,
                    "gpu_memory": peek_memory(),
                }
            )
            print(f"input_tokens={input_len} output_tokens={output_len} gen_sec={gen_elapsed:.2f} tps={tps}")
            print("--- generated text ---")
            print(text_clean)
        except Exception as exc:  # noqa: BLE001
            failures += 1
            record.update(
                {
                    "success": False,
                    "failure_layer": classify_failure(exc),
                    "error": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc(),
                }
            )
            print(traceback.format_exc())
        result_payload["generations"].append(record)

    success_n = sum(1 for g in result_payload["generations"] if g.get("success"))
    metadata["result"] = "PASS" if success_n == len(result_payload["generations"]) and result_payload["generations"] else "FAIL"
    if metadata["result"] == "PASS":
        metadata["notes"] += " Smoke-test generations completed. Quality is not yet scored; treat as Runs candidate pending review."
        # Explicit: a passing smoke test does not promote the matrix to Validated/Optimized.
        metadata["status_claim_allowed"] = "Runs (candidate) — not Validated until results are reviewed"
    result_payload["summary"] = {
        "success": metadata["result"] == "PASS",
        "prompts_total": len(result_payload["generations"]),
        "prompts_passed": success_n,
        "prompts_failed": failures,
        "peak_memory": peek_memory(),
        "trust_remote_code_used": trust_remote_code,
    }
    result_payload["metadata"] = metadata
    write_json(transformers_dir / "result.json", result_payload)
    write_json(out_dir / "run-metadata.json", metadata)
    print(f"\nresult={metadata['result']} passed={success_n}/{len(result_payload['generations'])}")
    print(f"wrote {transformers_dir / 'result.json'}")
    return 0 if metadata["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
