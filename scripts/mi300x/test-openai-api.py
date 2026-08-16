#!/usr/bin/env python3
"""Hit a local OpenAI-compatible vLLM server. No commercial OpenAI API.

Usage:
  python scripts/mi300x/test-openai-api.py \
    --base-url http://127.0.0.1:8000/v1 \
    --model nemotron-nano-bf16 \
    --output-dir results/mi300x/<run-id>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)
        handle.write("\n")


def http_json(method: str, url: str, body: dict | None = None, timeout: int = 120) -> dict:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            elapsed = time.perf_counter() - started
            parsed = json.loads(raw.decode("utf-8")) if raw else None
            return {
                "ok": True,
                "status": resp.status,
                "url": url,
                "method": method,
                "request": body,
                "response": parsed,
                "elapsed_sec": elapsed,
            }
    except urllib.error.HTTPError as err:
        raw = err.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw
        return {
            "ok": False,
            "status": err.code,
            "url": url,
            "method": method,
            "request": body,
            "response": parsed,
            "elapsed_sec": time.perf_counter() - started,
            "error": str(err),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "url": url,
            "method": method,
            "request": body,
            "elapsed_sec": time.perf_counter() - started,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Test a local OpenAI-compatible server.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--model", default="nemotron-nano-bf16")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()

    out_dir = Path(args.output_dir) / "vllm"
    out_dir.mkdir(parents=True, exist_ok=True)
    api_dir = out_dir / "openai-api"
    api_dir.mkdir(parents=True, exist_ok=True)

    base = args.base_url.rstrip("/")
    health_urls = [
        base.replace("/v1", "/health"),
        base + "/health",
        base.rsplit("/v1", 1)[0] + "/health",
    ]

    results = {
        "timestamp_utc": utcnow(),
        "base_url": args.base_url,
        "model": args.model,
        "tests": [],
    }

    health = None
    for url in dict.fromkeys(health_urls):
        health = http_json("GET", url, timeout=min(args.timeout, 30))
        results["tests"].append({"name": "health", **health})
        write_json(api_dir / "health.json", health)
        if health.get("ok"):
            break

    models = http_json("GET", f"{base}/models", timeout=min(args.timeout, 30))
    results["tests"].append({"name": "list_models", **models})
    write_json(api_dir / "models.json", models)

    warmup_ok = True
    warmup_items = []
    for i in range(2):
        body = {
            "model": args.model,
            "messages": [{"role": "user", "content": "Reply with the single word ready."}],
            "max_tokens": 8,
            "temperature": 0,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        item = http_json("POST", f"{base}/chat/completions", body, timeout=args.timeout)
        warmup_items.append(item)
        warmup_ok = warmup_ok and bool(item.get("ok"))
    results["tests"].append({"name": "warmup", "ok": warmup_ok, "items": warmup_items})
    write_json(api_dir / "warmup.json", warmup_items)

    basic_body = {
        "model": args.model,
        "messages": [
            {"role": "user", "content": "Explain the difference between RAM and storage in three sentences."}
        ],
        "max_tokens": 128,
        "temperature": 0,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    basic = http_json("POST", f"{base}/chat/completions", basic_body, timeout=args.timeout)
    results["tests"].append({"name": "chat_completion_reasoning_off", **basic})
    write_json(api_dir / "chat_reasoning_off.json", basic)

    reasoning_body = {
        "model": args.model,
        "messages": [{"role": "user", "content": "A server has 8 GPUs with 192 GB of memory each. What is the total aggregate GPU memory?"}],
        "max_tokens": 256,
        "temperature": 1.0,
        "top_p": 1.0,
        "chat_template_kwargs": {"enable_thinking": True},
    }
    reasoning = http_json("POST", f"{base}/chat/completions", reasoning_body, timeout=args.timeout)
    results["tests"].append({"name": "chat_completion_reasoning_on", **reasoning})
    write_json(api_dir / "chat_reasoning_on.json", reasoning)

    sequential = []
    seq_ok = True
    for i in range(3):
        body = {
            "model": args.model,
            "messages": [{"role": "user", "content": f"Reply with the single integer {i+1}."}],
            "max_tokens": 16,
            "temperature": 0,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        item = http_json("POST", f"{base}/chat/completions", body, timeout=args.timeout)
        sequential.append(item)
        seq_ok = seq_ok and bool(item.get("ok"))
    results["tests"].append({"name": "sequential_requests", "ok": seq_ok, "items": sequential})
    write_json(api_dir / "sequential.json", sequential)

    named = {t["name"]: t for t in results["tests"]}
    overall = all(
        [
            named.get("health", {}).get("ok") or named.get("list_models", {}).get("ok"),
            named.get("chat_completion_reasoning_off", {}).get("ok"),
            named.get("sequential_requests", {}).get("ok"),
        ]
    )
    results["result"] = "PASS" if overall else "FAIL"
    write_json(api_dir / "summary.json", results)
    print(json.dumps({"result": results["result"], "tests": {k: v.get("ok") for k, v in named.items()}}, indent=2))
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
