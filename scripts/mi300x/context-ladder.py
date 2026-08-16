#!/usr/bin/env python3
"""Engineering context-ladder against a local OpenAI-compatible server.

Not an official benchmark. Do not jump to 1M.

Prompt: unique HEAD/TAIL secrets plus repeated filler. The question can only
be answered from the first and last markers.

Usage:
  python scripts/mi300x/context-ladder.py \
    --base-url http://127.0.0.1:8000/v1 \
    --model nemotron-nano-bf16 \
    --output-dir results/mi300x/<run-id> \
    --tokenizer nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
    --lengths 4096 8192 16384
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import traceback
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HEAD = "HEAD_SECRET: the secret color is indigo."
TAIL = "TAIL_SECRET: the secret number is 4172."
QUESTION = (
    "What is the secret color from HEAD_SECRET and the secret number from TAIL_SECRET? "
    "Reply with exactly two fields and nothing else: COLOR=indigo NUMBER=4172"
)
FILLER = (
    "The filler sentence exists only to occupy context and is not needed for the answer. "
    "AMD Instinct MI300X has 192 GB HBM. ROCm is the host software path. "
)


def as_token_ids(encoded) -> list[int]:
    obj = encoded
    if hasattr(obj, "keys"):
        try:
            if "input_ids" in obj:
                obj = obj["input_ids"]
        except Exception:
            pass
    if hasattr(obj, "tolist"):
        obj = obj.tolist()
    if obj and isinstance(obj[0], list):
        obj = obj[0]
    return list(obj)


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)
        handle.write("\n")


def build_user_text(tokenizer, target_tokens: int) -> tuple[str, int]:
    """Build a chat-templated prompt whose token length is about target_tokens."""

    def templated_len(middle: str) -> int:
        user = f"{HEAD}\n\n{middle}\n\n{TAIL}\n\n{QUESTION}"
        ids = tokenizer.apply_chat_template(
            [{"role": "user", "content": user}],
            tokenize=True,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        return int(len(as_token_ids(ids))), user

    empty_len, _ = templated_len("")
    if empty_len >= target_tokens:
        raise ValueError(f"chat template overhead {empty_len} >= target {target_tokens}")
    filler_ids = tokenizer.encode(FILLER, add_special_tokens=False)
    if not filler_ids:
        raise ValueError("filler produced no tokens")
    # Leave a few tokens of slack so we do not exceed max_model_len.
    budget = max(target_tokens - empty_len - 8, len(filler_ids))
    n = max(budget // len(filler_ids), 1)
    _, user = templated_len(FILLER * n)
    actual = tokenizer.apply_chat_template(
        [{"role": "user", "content": user}],
        tokenize=True,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    return user, int(len(as_token_ids(actual)))


def chat_completion(base_url: str, model: str, user_text: str, max_tokens: int, timeout: int) -> dict:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": user_text}],
        "max_tokens": max_tokens,
        "temperature": 0,
        "chat_template_kwargs": {"enable_thinking": False},
        "stream": False,
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            elapsed = time.perf_counter() - started
            payload = json.loads(raw.decode("utf-8"))
            usage = payload.get("usage") or {}
            choice = (payload.get("choices") or [{}])[0]
            message = choice.get("message") or {}
            text = message.get("content") or ""
            return {
                "ok": True,
                "end_to_end_sec": elapsed,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "text": text,
                "reasoning": message.get("reasoning"),
                "response": payload,
            }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "end_to_end_sec": time.perf_counter() - started,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }


def judge(text: str) -> dict:
    lowered = (text or "").lower()
    color_ok = bool(re.search(r"color\s*=\s*indigo", lowered)) or ("indigo" in lowered)
    number_ok = bool(re.search(r"number\s*=\s*4172", lowered)) or ("4172" in lowered)
    return {
        "color_ok": color_ok,
        "number_ok": number_ok,
        "pass": color_ok and number_ok,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Engineering context ladder. Not an official benchmark.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--model", default="nemotron-nano-bf16")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--tokenizer", default="nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16")
    parser.add_argument("--revision", default=None)
    parser.add_argument("--lengths", nargs="+", type=int, default=[4096, 8192, 16384])
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--max-model-len", type=int, default=None)
    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
    from hf_revision import cached_snapshot_hash  # noqa: E402

    revision = args.revision or cached_snapshot_hash(args.tokenizer)
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        args.tokenizer, revision=revision, local_files_only=True, trust_remote_code=False
    )

    out_dir = Path(args.output_dir) / "context-ladder"
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "label": "Engineering context ladder only",
        "timestamp_utc": utcnow(),
        "base_url": args.base_url,
        "model": args.model,
        "tokenizer": args.tokenizer,
        "revision": revision,
        "max_model_len": args.max_model_len,
        "head": HEAD,
        "tail": TAIL,
        "question": QUESTION,
        "notes": [
            "Not an official benchmark.",
            "Do not treat a single length PASS as 1M context.",
        ],
        "runs": [],
    }

    overall_fail = False
    for length in args.lengths:
        print(f"=== target_tokens={length} ===")
        row = {"target_tokens": length, "success": False}
        try:
            user_text, templated_tokens = build_user_text(tokenizer, length)
            row["templated_tokens"] = templated_tokens
            timeout = args.timeout
            if length >= 65536:
                timeout = max(timeout, 1800)
            elif length >= 32768:
                timeout = max(timeout, 900)
            result = chat_completion(args.base_url, args.model, user_text, args.max_tokens, timeout)
            row.update(result)
            if result.get("ok"):
                verdict = judge(result.get("text") or "")
                row["judge"] = verdict
                row["success"] = bool(verdict["pass"])
            else:
                overall_fail = True
                row["failure_layer"] = "MEMORY" if "oom" in (result.get("error") or "").lower() else "VLLM"
        except Exception as exc:  # noqa: BLE001
            overall_fail = True
            row.update(
                {
                    "ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc(),
                    "failure_layer": "OTHER",
                }
            )
        report["runs"].append(row)
        print(json.dumps({k: row[k] for k in row if k not in ("response", "traceback",)}, indent=2))
        if not row.get("success"):
            overall_fail = True
            print("stopping ladder after first unsuccessful length")
            break

    report["summary"] = {
        "success": (not overall_fail) and all(r.get("success") for r in report["runs"]),
        "lengths_attempted": [r["target_tokens"] for r in report["runs"]],
        "lengths_passed": [r["target_tokens"] for r in report["runs"] if r.get("success")],
    }
    write_json(out_dir / f"ladder-max{args.max_model_len or 'unknown'}.json", report)
    write_json(out_dir / "latest.json", report)
    print(f"result={'PASS' if report['summary']['success'] else 'FAIL'} passed={report['summary']['lengths_passed']}")
    return 0 if report["summary"]["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
