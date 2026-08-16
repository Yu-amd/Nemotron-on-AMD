#!/usr/bin/env python3
"""Estimate *raw weight storage* for a given parameter count and precision.

This is NOT a runtime memory predictor. It excludes KV cache, activations,
workspace, framework overhead, MoE routing structures, temporary buffers,
and quantization metadata/scales.

Usage:
  python scripts/common/estimate_weight_memory.py --params 30e9
  python scripts/common/estimate_weight_memory.py --params 120e9 --json
"""

from __future__ import annotations

import argparse
import json

# Bytes per parameter for *raw* dense weight storage.
BYTES_PER_PARAM = {
    "fp32": 4.0,
    "bf16": 2.0,
    "fp16": 2.0,
    "fp8": 1.0,
    "int8": 1.0,
    "int4": 0.5,
    "nvfp4": 0.5,  # 4-bit payload only; NVIDIA packing/scales are extra and uncounted
    "q8": 1.0,
    "q6": 0.75,
    "q5": 0.625,
    "q4": 0.5,
}


def bytes_to_gib(num_bytes: float) -> float:
    return num_bytes / (1024 ** 3)


def bytes_to_decimal_gb(num_bytes: float) -> float:
    return num_bytes / 1e9


def estimate(params: float) -> dict:
    rows = []
    for name, bpp in BYTES_PER_PARAM.items():
        raw_bytes = params * bpp
        rows.append(
            {
                "precision": name,
                "bytes_per_parameter": bpp,
                "raw_weight_bytes": raw_bytes,
                "raw_weight_gb": bytes_to_decimal_gb(raw_bytes),
                "raw_weight_gib": bytes_to_gib(raw_bytes),
            }
        )
    return {
        "parameter_count": params,
        "note": (
            "Raw weight storage only. Excludes KV cache, activations, workspace, "
            "framework overhead, MoE routing, temporary buffers, and quantization "
            "metadata/scales. NVFP4 is counted as 4-bit payload only; it is an "
            "NVIDIA-specific format and is not assumed portable to AMD."
        ),
        "estimates": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate raw model-weight storage.")
    parser.add_argument("--params", required=True, type=float, help="Parameter count, e.g. 30e9 or 3.5e9")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a table")
    parser.add_argument("--label", default="", help="Optional model label")
    args = parser.parse_args()

    report = estimate(args.params)
    if args.label:
        report["label"] = args.label

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    header = f"{args.label} " if args.label else ""
    print(f"{header}parameter_count={args.params:.4g}")
    print(report["note"])
    print()
    print(f"{'precision':<10} {'B/param':>8} {'raw GB':>12} {'raw GiB':>12}")
    for row in report["estimates"]:
        print(
            f"{row['precision']:<10} {row['bytes_per_parameter']:>8.3f} "
            f"{row['raw_weight_gb']:>12.2f} {row['raw_weight_gib']:>12.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
