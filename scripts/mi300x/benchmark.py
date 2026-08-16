#!/usr/bin/env python3
"""Engineering characterization of a local OpenAI-compatible server.

This is NOT an official performance benchmark.

Usage:
  python scripts/mi300x/benchmark.py \
    --base-url http://127.0.0.1:8000/v1 \
    --model nemotron-nano-bf16 \
    --output-dir results/mi300x/<run-id> \
    --concurrency 1 2 4
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import traceback
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

PROMPT = (
    "Write a Python function that returns the factorial of a non-negative integer. "
    "Include a short comment. Do not explain after the code."
)


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def chat_completion(base_url: str, model: str, max_tokens: int, timeout: int) -> dict:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
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
    ttft = None
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            finished = time.perf_counter()
            payload = json.loads(raw.decode("utf-8"))
            usage = payload.get("usage") or {}
            # Non-streaming TTFT is not available; record end-to-end as a fallback
            # and document the limitation.
            completion_tokens = usage.get("completion_tokens")
            e2e = finished - started
            return {
                "ok": True,
                "end_to_end_sec": e2e,
                "ttft_sec": ttft,
                "ttft_method": "unavailable_without_streaming",
                "completion_tokens": completion_tokens,
                "prompt_tokens": usage.get("prompt_tokens"),
                "output_tokens_per_sec": (completion_tokens / e2e) if completion_tokens and e2e else None,
                "response": payload,
            }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "end_to_end_sec": time.perf_counter() - started,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }


def stream_completion(base_url: str, model: str, max_tokens: int, timeout: int) -> dict:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": max_tokens,
        "temperature": 0,
        "chat_template_kwargs": {"enable_thinking": False},
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=data,
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
        method="POST",
    )
    started = time.perf_counter()
    ttft = None
    usage = {}
    chunks = 0
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    event = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                chunks += 1
                if ttft is None:
                    ttft = time.perf_counter() - started
                if event.get("usage"):
                    usage = event["usage"]
        finished = time.perf_counter()
        e2e = finished - started
        completion_tokens = usage.get("completion_tokens")
        return {
            "ok": True,
            "end_to_end_sec": e2e,
            "ttft_sec": ttft,
            "ttft_method": "first_sse_chunk",
            "completion_tokens": completion_tokens,
            "prompt_tokens": usage.get("prompt_tokens"),
            "output_tokens_per_sec": (completion_tokens / e2e) if completion_tokens and e2e else None,
            "chunks": chunks,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "end_to_end_sec": time.perf_counter() - started,
            "ttft_sec": ttft,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }


def summarize(rows: list[dict]) -> dict:
    ok = [r for r in rows if r.get("ok")]
    def col(name):
        vals = [r[name] for r in ok if r.get(name) is not None]
        if not vals:
            return None
        return {
            "n": len(vals),
            "mean": statistics.mean(vals),
            "p50": statistics.median(vals),
            "min": min(vals),
            "max": max(vals),
        }

    return {
        "requests": len(rows),
        "successes": len(ok),
        "success_rate": (len(ok) / len(rows)) if rows else 0.0,
        "ttft_sec": col("ttft_sec"),
        "end_to_end_sec": col("end_to_end_sec"),
        "output_tokens_per_sec": col("output_tokens_per_sec"),
        "completion_tokens": col("completion_tokens"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Engineering characterization only. Not an official benchmark."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--model", default="nemotron-nano-bf16")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--concurrency", nargs="+", type=int, default=[1, 2, 4])
    parser.add_argument("--requests-per-conc", type=int, default=4)
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--no-stream", action="store_true")
    args = parser.parse_args()

    out_dir = Path(args.output_dir) / "benchmark"
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "label": "Engineering characterization only",
        "timestamp_utc": utcnow(),
        "base_url": args.base_url,
        "model": args.model,
        "max_tokens": args.max_tokens,
        "prompt": PROMPT,
        "streaming": not args.no_stream,
        "runs": [],
        "notes": [
            "Not an official performance benchmark.",
            "Do not quote a naked tokens/sec number without hardware, software, checkpoint, precision, context, concurrency, and date.",
        ],
    }

    worker = stream_completion if not args.no_stream else chat_completion
    for conc in args.concurrency:
        n = args.requests_per_conc * conc
        print(f"concurrency={conc} requests={n}")
        rows = []
        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=conc) as pool:
            futs = [
                pool.submit(worker, args.base_url, args.model, args.max_tokens, args.timeout)
                for _ in range(n)
            ]
            for fut in as_completed(futs):
                rows.append(fut.result())
        elapsed = time.perf_counter() - started
        entry = {
            "concurrency": conc,
            "wall_sec": elapsed,
            "summary": summarize(rows),
            "requests": rows,
        }
        report["runs"].append(entry)
        print(json.dumps({"concurrency": conc, "summary": entry["summary"]}, indent=2))

    path = out_dir / "characterization.json"
    with path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, default=str)
        handle.write("\n")
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
