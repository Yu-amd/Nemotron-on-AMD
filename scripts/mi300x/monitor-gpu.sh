#!/usr/bin/env bash
# Sample GPU telemetry while a test is running. Does not modify clocks.
#
# Usage:
#   bash scripts/mi300x/monitor-gpu.sh [interval-seconds] [output-file]
#
# Example:
#   bash scripts/mi300x/monitor-gpu.sh 2 results/mi300x/<run-id>/logs/gpu-monitor.tsv

set -u

INTERVAL="${1:-2}"
OUT="${2:-}"

header() {
  printf 'timestamp_utc\ttool\traw\n'
}

sample() {
  local ts
  ts="$(date -u -Iseconds)"
  if command -v rocm-smi >/dev/null 2>&1; then
    # Keep this as one line so TSV stays simple.
    local raw
    raw="$(rocm-smi --showuse --showmeminfo vram --showtemp --showpower 2>/dev/null | tr '\n' '|' | tr '\t' ' ')"
    printf '%s\trocm-smi\t%s\n' "${ts}" "${raw}"
  elif command -v amd-smi >/dev/null 2>&1; then
    local raw
    raw="$(amd-smi monitor --csv 2>/dev/null | tr '\n' '|')"
    printf '%s\tamd-smi\t%s\n' "${ts}" "${raw}"
  else
    printf '%s\tnone\tno rocm-smi or amd-smi\n' "${ts}"
  fi
}

if [[ -n "${OUT}" ]]; then
  mkdir -p "$(dirname "${OUT}")"
  header > "${OUT}"
  echo "[monitor-gpu] writing ${OUT} every ${INTERVAL}s (Ctrl-C to stop)"
  while true; do
    sample >> "${OUT}"
    sleep "${INTERVAL}"
  done
else
  header
  while true; do
    sample
    sleep "${INTERVAL}"
  done
fi
