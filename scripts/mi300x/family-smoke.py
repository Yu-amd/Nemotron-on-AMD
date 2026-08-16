#!/usr/bin/env python3
"""Generic MI300X smoke for queued Nemotron-family checkpoints.

Tasks: causal, embed, rerank, vl-embed, safety, parse, asr, auto.

Does not copy FlashInfer/NVFP4 flags. Writes the same result.json / run-metadata
shape as transformers-smoke-test.py so reviews can follow the Nano 30B pattern.

Usage:
  python scripts/mi300x/family-smoke.py \\
    --model nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16 \\
    --task causal --output-dir results/mi300x/<run-id>
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(_SCRIPTS_DIR / "common") not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR / "common"))
from hf_revision import cached_snapshot_hash  # noqa: E402

DEFAULT_PROMPTS = Path(__file__).resolve().parents[2] / "prompts" / "smoke-tests.json"


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
    if any(token in text for token in ("fnuz", "fp8", "e4m3", "e5m2", "float8")):
        return "PRECISION"
    if "nemo" in text and "cuda" in text:
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


def to_input_ids_tensor(encoded):
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
        raise TypeError(f"chat template returned {type(encoded).__name__} without a tensor shape")
    return obj


def mean_pool(last_hidden, attention_mask):
    import torch

    mask = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
    summed = (last_hidden * mask).sum(dim=1)
    counts = mask.sum(dim=1).clamp(min=1e-9)
    return summed / counts


def dummy_rgb_png(path: Path, size: int = 64) -> Path:
    from PIL import Image

    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (size, size), color=(40, 80, 160)).save(path)
    return path


def _call_processor(processor, image, text):
    """NVIDIA VL processors often zip(images, text) and/or need a chat template with an image slot."""
    attempts = []
    if hasattr(processor, "process_documents"):
        attempts.append(
            (
                "process_documents",
                lambda: processor.process_documents([{"image": image, "text": text}]),
            )
        )
    if hasattr(processor, "apply_chat_template"):
        def _chat():
            message = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": text},
                    ],
                }
            ]
            templated = processor.apply_chat_template(message, tokenize=False, add_generation_prompt=True)
            return processor(text=[templated], images=[image], return_tensors="pt")

        attempts.append(("chat_template+images", _chat))
    attempts.extend(
        [
            ("images=[image], text=[text]", lambda: processor(images=[image], text=[text], return_tensors="pt")),
            ("images=image, text=text", lambda: processor(images=image, text=text, return_tensors="pt")),
            ("text=[text], images=[image]", lambda: processor(text=[text], images=[image], return_tensors="pt")),
            ("images=[image] only", lambda: processor(images=[image], return_tensors="pt")),
            ("documents list", lambda: processor([{"image": image, "text": text}], return_tensors="pt")),
        ]
    )
    last = None
    for label, fn in attempts:
        try:
            packed = fn()
            print(f"processor ok via {label}")
            return packed
        except Exception as proc_err:  # noqa: BLE001
            last = proc_err
            print(f"processor skip {label}: {type(proc_err).__name__}: {proc_err}")
    raise last



def _tensorize_batch(packed, device):
    if hasattr(packed, "keys") or isinstance(packed, dict):
        return {k: v.to(device) if hasattr(v, "to") else v for k, v in packed.items()}
    if hasattr(packed, "to"):
        return packed.to(device)
    raise TypeError(f"processor returned {type(packed).__name__}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Queued Nemotron-family smoke on MI300X.")
    parser.add_argument("--model", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--task",
        default="auto",
        choices=["auto", "causal", "embed", "rerank", "vl-embed", "safety", "parse", "asr"],
    )
    parser.add_argument("--prompts", default=str(DEFAULT_PROMPTS))
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--trust-remote-code", action="store_true")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--dtype", default="bfloat16")
    parser.add_argument("--revision", default=None)
    parser.add_argument("--attn-implementation", default="sdpa")
    args = parser.parse_args()
    if not args.revision:
        args.revision = cached_snapshot_hash(args.model)

    out_dir = Path(args.output_dir)
    work_dir = out_dir / "transformers"
    logs_dir = out_dir / "logs"
    work_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "family-smoke.log"

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

        def isatty(self):
            return False

        @property
        def encoding(self):
            return getattr(self.streams[0], "encoding", "utf-8")

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
        "notes": f"Family smoke task={args.task}. Not Optimized. Not a Nano 30B BF16 result.",
        "command": sys.argv,
        "trust_remote_code_requested": args.trust_remote_code,
        "queue_task": args.task,
    }
    result_payload = {
        "metadata": metadata,
        "environment": {},
        "load": {},
        "outputs": [],
        "summary": {},
    }

    try:
        import torch
        from transformers import AutoConfig, AutoModel, AutoTokenizer, __version__ as transformers_version
    except Exception as exc:  # noqa: BLE001
        metadata["result"] = "FAIL"
        result_payload["summary"] = {
            "success": False,
            "failure_layer": classify_failure(exc),
            "error": f"{type(exc).__name__}: {exc}",
        }
        write_json(work_dir / "result.json", result_payload)
        write_json(out_dir / "run-metadata.json", metadata)
        print(traceback.format_exc())
        return 1

    dtype_map = {
        "bfloat16": torch.bfloat16,
        "bf16": torch.bfloat16,
        "float16": torch.float16,
        "fp16": torch.float16,
        "float32": torch.float32,
        "auto": "auto",
    }
    torch_dtype = dtype_map.get(args.dtype, torch.bfloat16)
    env = {
        "python": sys.version,
        "executable": sys.executable,
        "torch_version": torch.__version__,
        "torch_hip": getattr(torch.version, "hip", None),
        "transformers_version": transformers_version,
        "cuda_is_available": bool(torch.cuda.is_available()),
        "device_names": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
        if torch.cuda.is_available()
        else [],
    }
    metadata["gpu"] = env["device_names"][0] if env["device_names"] else None
    metadata["pytorch_version"] = torch.__version__
    metadata["runtime_version"] = transformers_version
    metadata["rocm_version"] = getattr(torch.version, "hip", None)
    result_payload["environment"] = env
    if not env["cuda_is_available"]:
        metadata["result"] = "FAIL"
        result_payload["summary"] = {"success": False, "failure_layer": "ROCM", "error": "no GPU"}
        write_json(work_dir / "result.json", result_payload)
        write_json(out_dir / "run-metadata.json", metadata)
        return 1

    trust = bool(args.trust_remote_code)
    print(f"model={args.model} task={args.task} dtype={args.dtype} revision={args.revision}")

    try:
        config = AutoConfig.from_pretrained(args.model, revision=args.revision, trust_remote_code=trust)
    except Exception as exc:
        if not trust:
            print("retry AutoConfig with trust_remote_code=True")
            trust = True
            metadata["trust_remote_code_required"] = True
            try:
                config = AutoConfig.from_pretrained(args.model, revision=args.revision, trust_remote_code=True)
            except Exception as retry_exc:
                metadata["result"] = "FAIL"
                result_payload["summary"] = {
                    "success": False,
                    "failure_layer": classify_failure(retry_exc),
                    "error": f"{type(retry_exc).__name__}: {retry_exc}",
                    "traceback": traceback.format_exc(),
                }
                write_json(work_dir / "result.json", result_payload)
                write_json(out_dir / "run-metadata.json", metadata)
                print(traceback.format_exc())
                return 1
        else:
            metadata["result"] = "FAIL"
            result_payload["summary"] = {
                "success": False,
                "failure_layer": classify_failure(exc),
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            }
            write_json(work_dir / "result.json", result_payload)
            write_json(out_dir / "run-metadata.json", metadata)
            print(traceback.format_exc())
            return 1

    arches = list(getattr(config, "architectures", None) or [])
    model_type = getattr(config, "model_type", None)
    result_payload["load"]["config"] = {
        "model_type": model_type,
        "architectures": arches,
        "auto_map": getattr(config, "auto_map", None),
        "pipe": getattr(config, "pipeline_tag", None),
    }
    if not metadata.get("model_revision"):
        metadata["model_revision"] = getattr(config, "_commit_hash", None)

    task = args.task
    if task == "auto":
        joined = " ".join(arches).lower()
        if "speech" in (model_type or "") or "whisper" in joined or "parakeet" in joined:
            task = "asr"
        elif "sequenceclassification" in joined or "ranking" in joined:
            task = "rerank"
        elif "causal" in joined or "forcausallm" in joined:
            task = "causal"
        elif "imagetext" in joined or "nemotronparse" in joined.lower():
            task = "parse"
        else:
            task = "embed"
    metadata["queue_task_resolved"] = task
    print(f"resolved_task={task} architectures={arches} model_type={model_type}")

    load_kwargs = {
        "revision": args.revision,
        "trust_remote_code": trust,
        "low_cpu_mem_usage": True,
    }
    if torch_dtype != "auto":
        load_kwargs["torch_dtype"] = torch_dtype
    if args.attn_implementation:
        load_kwargs["attn_implementation"] = args.attn_implementation
    fa = str(getattr(config, "_attn_implementation", None) or getattr(config, "attn_implementation", "") or "")
    if "flash" in fa.lower():
        impl = args.attn_implementation if args.attn_implementation and "flash" not in str(args.attn_implementation).lower() else "eager"
        print(f"override config attn {fa!r} -> {impl}")
        try:
            config._attn_implementation = impl
        except Exception:
            pass
        load_kwargs["attn_implementation"] = impl
    def _force_eager(cfg, depth=0):
        if cfg is None or depth > 8:
            return
        for attr in ("_attn_implementation", "attn_implementation", "_attn_implementation_internal"):
            if hasattr(cfg, attr) or True:
                try:
                    setattr(cfg, attr, "eager")
                except Exception:
                    pass
        for child in ("llm_config", "text_config", "vision_config", "audio_config", "thinker_config"):
            if hasattr(cfg, child):
                _force_eager(getattr(cfg, child), depth + 1)

    if "omni" in args.model.lower() or "Omni" in str(arches) or "flash" in fa.lower():
        _force_eager(config)
        load_kwargs["attn_implementation"] = "eager"
        print("forced nested attn_implementation=eager")
    load_kwargs["config"] = config

    def _from_pretrained(cls, **kwargs):
        try:
            return cls.from_pretrained(args.model, **kwargs)
        except (TypeError, ValueError, OSError) as exc:
            kwargs = dict(kwargs)
            if kwargs.get("attn_implementation"):
                print(f"{cls.__name__} retry without attn_implementation ({type(exc).__name__})")
                kwargs.pop("attn_implementation", None)
                try:
                    return cls.from_pretrained(args.model, **kwargs)
                except Exception:
                    pass
            if not kwargs.get("trust_remote_code"):
                print(f"{cls.__name__} retry with trust_remote_code=True")
                kwargs["trust_remote_code"] = True
                return cls.from_pretrained(args.model, **kwargs)
            raise

    t0 = time.perf_counter()
    mem_before = peek_memory()
    model = None
    tokenizer = None
    try:
        if task in ("causal", "safety"):
            from transformers import AutoModelForCausalLM, AutoModelForImageTextToText

            try:
                model = AutoModelForCausalLM.from_pretrained(args.model, **load_kwargs)
            except Exception as first:
                print(f"CausalLM load failed ({type(first).__name__}): {first}")
                load_kwargs_retry = dict(load_kwargs)
                load_kwargs_retry["trust_remote_code"] = True
                trust = True
                err = str(first).lower()
                if "scaled_dot_product" in err or "sdpa" in err:
                    load_kwargs_retry["attn_implementation"] = "eager"
                    print("retry attn_implementation=eager")
                try:
                    model = AutoModelForImageTextToText.from_pretrained(args.model, **load_kwargs_retry)
                except Exception as second:
                    print(f"ImageTextToText failed ({type(second).__name__}); CausalLM retry")
                    if "scaled_dot_product" in str(second).lower() or "sdpa" in str(second).lower():
                        load_kwargs_retry["attn_implementation"] = "eager"
                    model = AutoModelForCausalLM.from_pretrained(args.model, **load_kwargs_retry)
            tokenizer = AutoTokenizer.from_pretrained(args.model, revision=args.revision, trust_remote_code=trust)
            model.to(args.device)
            model.eval()
            _run_causal(model, tokenizer, args, result_payload, task)
        elif task == "embed":
            tokenizer = AutoTokenizer.from_pretrained(args.model, revision=args.revision, trust_remote_code=trust)
            try:
                model = AutoModel.from_pretrained(args.model, **load_kwargs)
            except Exception:
                load_kwargs["trust_remote_code"] = True
                trust = True
                load_kwargs.pop("attn_implementation", None)
                model = AutoModel.from_pretrained(args.model, **load_kwargs)
            model.to(args.device)
            model.eval()
            _run_embed(model, tokenizer, args, result_payload)
        elif task == "rerank":
            from transformers import AutoModelForSequenceClassification

            tokenizer = AutoTokenizer.from_pretrained(args.model, revision=args.revision, trust_remote_code=True)
            trust = True
            load_kwargs["trust_remote_code"] = True
            try:
                model = AutoModelForSequenceClassification.from_pretrained(args.model, **load_kwargs)
            except Exception:
                load_kwargs.pop("attn_implementation", None)
                model = AutoModel.from_pretrained(args.model, **load_kwargs)
            model.to(args.device)
            model.eval()
            _run_rerank(model, tokenizer, args, result_payload)
        elif task in ("vl-embed", "parse"):
            _run_vl(args, load_kwargs, trust, result_payload, task, work_dir)
            trust = True
        elif task == "asr":
            _run_asr(args, load_kwargs, result_payload, work_dir)
        else:
            raise ValueError(f"unhandled task {task}")
    except Exception as exc:  # noqa: BLE001
        err_s = f"{type(exc).__name__}: {exc}"
        blocked = "only supported on" in err_s.lower() or "not implemented for" in err_s.lower()
        blocked = blocked or "nvidia-nemo" in err_s.lower() or "from nemo" in err_s.lower()
        metadata["result"] = "BLOCKED" if blocked else "FAIL"
        result_payload["load"]["memory_before"] = mem_before
        result_payload["load"]["memory_after_failure"] = peek_memory()
        result_payload["summary"] = {
            "success": False,
            "failure_layer": classify_failure(exc),
            "error": err_s,
            "traceback": traceback.format_exc(),
        }
        write_json(work_dir / "result.json", result_payload)
        write_json(out_dir / "run-metadata.json", metadata)
        print(traceback.format_exc())
        return 1

    result_payload["load"].update(
        {
            "model_load_sec": time.perf_counter() - t0,
            "memory_before": mem_before,
            "memory_after_load": peek_memory(),
            "trust_remote_code_used": trust,
        }
    )
    metadata["trust_remote_code_required"] = bool(trust)
    ok = bool(result_payload.get("summary", {}).get("success")) if result_payload.get("summary") else False
    if not result_payload.get("summary"):
        n = len(result_payload.get("outputs") or result_payload.get("generations") or [])
        passed = sum(
            1
            for row in (result_payload.get("outputs") or result_payload.get("generations") or [])
            if row.get("success")
        )
        ok = n > 0 and passed == n
        result_payload["summary"] = {
            "success": ok,
            "prompts_total": n,
            "prompts_passed": passed,
            "peak_memory": peek_memory(),
            "trust_remote_code_used": trust,
        }
    metadata["result"] = "PASS" if result_payload["summary"].get("success") else result_payload.get("metadata", {}).get("result") or "FAIL"
    if metadata["result"] not in ("PASS", "FAIL", "BLOCKED", "PASS WITH CAVEATS"):
        metadata["result"] = "PASS" if ok else "FAIL"
    metadata["status_claim_allowed"] = (
        "Runs (candidate) — not Validated until results are reviewed"
        if metadata["result"] == "PASS"
        else "no Runs claim"
    )
    result_payload["metadata"] = metadata
    write_json(work_dir / "result.json", result_payload)
    write_json(out_dir / "run-metadata.json", metadata)
    print(f"result={metadata['result']}")
    return 0 if metadata["result"] in ("PASS", "PASS WITH CAVEATS") else 1


def _run_causal(model, tokenizer, args, result_payload, task):
    import torch

    with Path(args.prompts).open(encoding="utf-8") as handle:
        data = json.load(handle)
    prompts = data["prompts"] if isinstance(data, dict) else data
    if task == "safety":
        prompts = [
            {
                "id": "safe-hello",
                "messages": [{"role": "user", "content": "What is the capital of France?"}],
            },
            {
                "id": "policy-shape",
                "messages": [
                    {
                        "role": "user",
                        "content": "Classify this user message as safe or unsafe: 'How do I bake banana bread?' Reply with one word.",
                    }
                ],
            },
        ]
    gens = []
    for item in prompts[:5]:
        messages = item.get("messages") or [{"role": "user", "content": item["prompt"]}]
        record = {"id": item.get("id"), "success": False, "messages": messages}
        try:
            try:
                encoded = tokenizer.apply_chat_template(
                    messages, tokenize=True, add_generation_prompt=True, return_tensors="pt", enable_thinking=False
                )
            except TypeError:
                try:
                    encoded = tokenizer.apply_chat_template(
                        messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
                    )
                except Exception:
                    encoded = tokenizer(messages[-1]["content"], return_tensors="pt").input_ids
            encoded = to_input_ids_tensor(encoded).to(args.device)
            with torch.inference_mode():
                out = model.generate(encoded, max_new_tokens=args.max_new_tokens, do_sample=False, num_beams=1)
            text = tokenizer.decode(out[0][encoded.shape[-1] :], skip_special_tokens=True)
            record.update({"success": True, "generated_text": text, "gpu_memory": peek_memory()})
            print(f"=== {record['id']} ===\n{text[:800]}")
        except Exception as exc:  # noqa: BLE001
            record.update(
                {"success": False, "failure_layer": classify_failure(exc), "error": f"{type(exc).__name__}: {exc}"}
            )
            print(traceback.format_exc())
        gens.append(record)
    result_payload["generations"] = gens
    result_payload["outputs"] = gens


def _run_embed(model, tokenizer, args, result_payload):
    import torch
    import torch.nn.functional as F

    texts = [
        "AMD Instinct MI300X has 192 GB of HBM.",
        "The MI300X accelerator provides 192 gigabytes of high-bandwidth memory.",
        "Bananas are a yellow fruit.",
    ]
    tok = tokenizer(texts, padding=True, truncation=True, return_tensors="pt", max_length=256)
    tok = {k: v.to(args.device) for k, v in tok.items()}
    with torch.inference_mode():
        out = model(**tok)
        hidden = out.last_hidden_state if hasattr(out, "last_hidden_state") else out[0]
        vecs = mean_pool(hidden, tok["attention_mask"])
        vecs = F.normalize(vecs, p=2, dim=1)
    sim01 = float((vecs[0] @ vecs[1]).item())
    sim02 = float((vecs[0] @ vecs[2]).item())
    ok = sim01 > sim02
    result_payload["outputs"] = [
        {
            "id": "embed-sanity",
            "success": ok,
            "cosine_paraphrase": sim01,
            "cosine_unrelated": sim02,
            "note": "paraphrase pair should outrank fruit sentence",
            "gpu_memory": peek_memory(),
        }
    ]
    result_payload["summary"] = {
        "success": ok,
        "prompts_total": 1,
        "prompts_passed": int(ok),
        "peak_memory": peek_memory(),
    }
    print(f"cosine paraphrase={sim01:.4f} unrelated={sim02:.4f} ok={ok}")


def _run_rerank(model, tokenizer, args, result_payload):
    import torch

    pairs = [
        ("What GPU memory does MI300X have?", "MI300X has 192 GB of HBM3."),
        ("What GPU memory does MI300X have?", "Banana bread uses ripe bananas."),
    ]
    scores = []
    for query, doc in pairs:
        # Many Nemotron rerankers concatenate query/document.
        text = f"{query} [SEP] {doc}" if tokenizer.sep_token else f"query: {query} document: {doc}"
        tok = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        tok = {k: v.to(args.device) for k, v in tok.items()}
        with torch.inference_mode():
            out = model(**tok)
            logits = out.logits if hasattr(out, "logits") else out[0]
            score = float(logits.view(-1)[-1].item()) if logits.ndim >= 1 else float(logits.item())
        scores.append(score)
        print(f"score={score:.4f} doc={doc[:60]}")
    ok = scores[0] > scores[1]
    result_payload["outputs"] = [
        {
            "id": "rerank-sanity",
            "success": ok,
            "relevant_score": scores[0],
            "irrelevant_score": scores[1],
            "gpu_memory": peek_memory(),
        }
    ]
    result_payload["summary"] = {"success": ok, "prompts_total": 1, "prompts_passed": int(ok), "peak_memory": peek_memory()}



def _extract_embedding_tensor(out):
    import torch

    named = (
        "sentence_embedding",
        "embeddings",
        "pooler_output",
        "last_hidden_state",
        "hidden_states",
    )
    for attr in named:
        val = getattr(out, attr, None)
        if val is None:
            continue
        if isinstance(val, (tuple, list)):
            val = val[-1] if val else None
        if val is not None and hasattr(val, "shape"):
            return val[:, 0] if getattr(val, "ndim", 0) == 3 else val
    if torch.is_tensor(out):
        return out[:, 0] if out.ndim == 3 else out
    items = []
    if hasattr(out, "items"):
        try:
            items = [(k, v) for k, v in out.items() if v is not None and hasattr(v, "shape")]
        except Exception:
            items = []
    if items:
        val = items[0][1]
        return val[:, 0] if getattr(val, "ndim", 0) == 3 else val
    return None


def _run_vl(args, load_kwargs, trust, result_payload, task, work_dir):
    import torch
    from PIL import Image
    from transformers import AutoModel, AutoProcessor

    img_path = dummy_rgb_png(work_dir / "dummy.png")
    image = Image.open(img_path).convert("RGB")
    load_kwargs = dict(load_kwargs)
    load_kwargs["trust_remote_code"] = True
    try:
        processor = AutoProcessor.from_pretrained(args.model, revision=args.revision, trust_remote_code=True)
    except Exception:
        processor = AutoProcessor.from_pretrained(args.model, revision=args.revision, trust_remote_code=True, use_fast=False)
    try:
        model = AutoModel.from_pretrained(args.model, **load_kwargs)
    except Exception as load_exc:
        print(f"AutoModel retry without attn_implementation ({type(load_exc).__name__})")
        load_kwargs.pop("attn_implementation", None)
        model = AutoModel.from_pretrained(args.model, **load_kwargs)
    model.to(args.device)
    model.eval()
    if task == "parse":
        from transformers import AutoModelForCausalLM, AutoModelForImageTextToText

        if not hasattr(model, "generate"):
            last = None
            for cls in (AutoModelForCausalLM, AutoModelForImageTextToText):
                try:
                    print(f"parse retry via {cls.__name__}")
                    model = cls.from_pretrained(args.model, **load_kwargs)
                    break
                except Exception as parse_err:  # noqa: BLE001
                    last = parse_err
                    print(f"parse skip {cls.__name__}: {type(parse_err).__name__}: {parse_err}")
            else:
                raise last
            model.to(args.device)
            model.eval()
        prompt = "Extract any visible text as markdown."
        packed = _call_processor(processor, image, prompt)
        packed = _tensorize_batch(packed, args.device)
        with torch.inference_mode():
            out = model.generate(**packed, max_new_tokens=32)
        text = processor.batch_decode(out, skip_special_tokens=True)[0] if hasattr(processor, "batch_decode") else str(out)
        result_payload["outputs"] = [{"id": "parse-dummy-image", "success": True, "generated_text": text, "gpu_memory": peek_memory()}]
        result_payload["summary"] = {"success": True, "prompts_total": 1, "prompts_passed": 1, "peak_memory": peek_memory()}
        print(text[:500])
        return
    packed = _call_processor(processor, image, "a blue square")
    packed = _tensorize_batch(packed, args.device)
    with torch.inference_mode():
        try:
            out = model(**packed)
        except Exception as fwd:
            print(f"model(**packed) failed: {type(fwd).__name__}: {fwd}")
            if hasattr(model, "encode"):
                out = model.encode([image], ["a blue square"])
            else:
                raise
    vec = _extract_embedding_tensor(out)
    shape = list(vec.shape) if vec is not None and hasattr(vec, "shape") else []
    note = None
    if vec is None:
        note = f"forward completed; no embedding tensor in {type(out).__name__}"
        print(note)
    else:
        print(f"vl embedding shape={tuple(vec.shape)}")
    result_payload["outputs"] = [
        {
            "id": "vl-embed-dummy",
            "success": True,
            "embedding_shape": shape,
            "note": note,
            "gpu_memory": peek_memory(),
        }
    ]
    result_payload["summary"] = {"success": True, "prompts_total": 1, "prompts_passed": 1, "peak_memory": peek_memory()}


def _run_asr(args, load_kwargs, result_payload, work_dir):
    import numpy as np
    import torch

    try:
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"ASR imports failed: {exc}") from exc

    sr = 16000
    t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
    audio = (0.1 * np.sin(2 * np.pi * 440 * t)).astype("float32")
    try:
        pipe = pipeline(
            "automatic-speech-recognition",
            model=args.model,
            revision=args.revision,
            device=0,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )
        text = pipe({"array": audio, "sampling_rate": sr})
        result_payload["outputs"] = [{"id": "asr-tone", "success": True, "raw": text, "note": "synthetic 440 Hz; transcript may be empty/garbage"}]
        result_payload["summary"] = {"success": True, "prompts_total": 1, "prompts_passed": 1, "peak_memory": peek_memory()}
        print(text)
        return
    except Exception as exc:
        err = f"{type(exc).__name__}: {exc}"
        if any(
            tok in err.lower()
            for tok in ("cuda", "nvidia-nemo", "from nemo", "not implemented", "only supported on")
        ):
            result_payload["summary"] = {
                "success": False,
                "failure_layer": "MODEL ARCHITECTURE",
                "error": err,
                "blocked_reason": "ASR path looks CUDA/NeMo-specific or unimplemented on this stack",
            }
            raise RuntimeError(f"ASR BLOCKED: {err}") from exc
        raise


if __name__ == "__main__":
    raise SystemExit(main())
