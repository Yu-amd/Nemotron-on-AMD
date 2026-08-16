#!/usr/bin/env python3
"""Download a Hugging Face model snapshot without guessing cache behaviour.

Does not print or store tokens. Supply HF_TOKEN via the environment if required.

Usage:
  python scripts/mi300x/download-model.py \
    --model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
    --output-dir /path/to/local/weights \
    --report results/mi300x/<run-id>/model-download.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone


def main() -> int:
    parser = argparse.ArgumentParser(description="Download a Hugging Face model snapshot.")
    parser.add_argument("--model", required=True, help="Hugging Face repo id")
    parser.add_argument("--revision", default=None, help="Git revision / commit (optional)")
    parser.add_argument("--output-dir", required=True, help="Local directory for the snapshot")
    parser.add_argument("--report", default=None, help="Write JSON metadata to this path")
    parser.add_argument(
        "--allow-patterns",
        nargs="*",
        default=None,
        help="Optional huggingface_hub allow_patterns",
    )
    args = parser.parse_args()

    token_present = bool(os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN"))
    started = time.perf_counter()
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        from huggingface_hub import snapshot_download
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: huggingface_hub is required: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    print(f"model={args.model}")
    print(f"revision={args.revision or 'default'}")
    print(f"output_dir={args.output_dir}")
    print(f"hf_token_present={token_present}")
    print("starting snapshot_download...")

    try:
        local_dir = snapshot_download(
            repo_id=args.model,
            revision=args.revision,
            local_dir=args.output_dir,
            allow_patterns=args.allow_patterns,
        )
    except Exception as exc:  # noqa: BLE001
        elapsed = time.perf_counter() - started
        report = {
            "timestamp_utc": timestamp,
            "model": args.model,
            "revision": args.revision,
            "output_dir": args.output_dir,
            "hf_token_present": token_present,
            "result": "FAIL",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "elapsed_sec": elapsed,
        }
        _write_report(args.report, report)
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    elapsed = time.perf_counter() - started
    report = {
        "timestamp_utc": timestamp,
        "model": args.model,
        "revision": args.revision,
        "output_dir": args.output_dir,
        "local_dir": local_dir,
        "hf_token_present": token_present,
        "result": "PASS",
        "elapsed_sec": elapsed,
        "notes": "Snapshot download completed. This is not a model-load validation.",
    }
    _write_report(args.report, report)
    print(json.dumps(report, indent=2))
    return 0


def _write_report(path: str | None, report: dict) -> None:
    if not path:
        return
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
