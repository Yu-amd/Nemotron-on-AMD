#!/usr/bin/env python3
"""Resolve a Hugging Face snapshot hash from the local cache without guessing."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def cached_snapshot_hash(model_id: str, cache_dir: str | Path | None = None) -> str | None:
    """Return refs/main (or the sole snapshot dir) for a cached Hub repo."""
    cache = Path(cache_dir) if cache_dir else Path.home() / ".cache" / "huggingface" / "hub"
    repo_dir = cache / ("models--" + model_id.replace("/", "--"))
    main_ref = repo_dir / "refs" / "main"
    if main_ref.is_file():
        value = main_ref.read_text(encoding="utf-8").strip()
        if value:
            return value
    snapshots = repo_dir / "snapshots"
    if snapshots.is_dir():
        names = [p.name for p in snapshots.iterdir() if p.is_dir()]
        if len(names) == 1:
            return names[0]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Print a cached Hugging Face snapshot hash.")
    parser.add_argument("model_id")
    parser.add_argument("--cache-dir", default=None)
    args = parser.parse_args()
    digest = cached_snapshot_hash(args.model_id, args.cache_dir)
    if not digest:
        print(f"no cached snapshot for {args.model_id}", file=sys.stderr)
        return 1
    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
