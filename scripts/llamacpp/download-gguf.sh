#!/usr/bin/env bash
# Download one GGUF file from the Hugging Face Hub. Pins revision. Records bytes.
# Does not print tokens. Does not download Super BF16, Ultra, or NVFP4.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPO=""
FILE=""
REVISION="main"
DEST_DIR="${REPO_ROOT}/tools/llamacpp/gguf"
REPORT=""

usage() {
  cat <<'EOF'
Download a single GGUF from Hugging Face.

  --repo ID           e.g. nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF
  --file NAME         filename inside the repo
  --revision HASH     git revision (preferred over floating main)
  --dest-dir DIR      default tools/llamacpp/gguf
  --report PATH       write JSON metadata
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --file) FILE="$2"; shift 2 ;;
    --revision) REVISION="$2"; shift 2 ;;
    --dest-dir) DEST_DIR="$2"; shift 2 ;;
    --report) REPORT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "${REPO}" || -z "${FILE}" ]]; then
  usage
  exit 2
fi

case "${REPO}${FILE}" in
  *NVFP4*|*nvfp4*)
    echo "Refusing NVFP4 download in the llama.cpp stack." >&2
    exit 2
    ;;
  *Ultra*|*ultra*)
    echo "Refusing Ultra download." >&2
    exit 2
    ;;
esac

mkdir -p "${DEST_DIR}"
OUT="${DEST_DIR}/${FILE}"
URL="https://huggingface.co/${REPO}/resolve/${REVISION}/${FILE}"
TOKEN_PRESENT=0
if [[ -n "${HF_TOKEN:-${HUGGING_FACE_HUB_TOKEN:-}}" ]]; then
  TOKEN_PRESENT=1
fi

echo "repo=${REPO}"
echo "file=${FILE}"
echo "revision=${REVISION}"
echo "url=${URL}"
echo "out=${OUT}"
echo "hf_token_present=${TOKEN_PRESENT}"

CURL_AUTH=()
if [[ -n "${HF_TOKEN:-}" ]]; then
  CURL_AUTH=(-H "Authorization: Bearer ${HF_TOKEN}")
elif [[ -n "${HUGGING_FACE_HUB_TOKEN:-}" ]]; then
  CURL_AUTH=(-H "Authorization: Bearer ${HUGGING_FACE_HUB_TOKEN}")
fi

STARTED="$(date +%s)"
curl -fL --retry 3 --retry-delay 2 "${CURL_AUTH[@]}" -o "${OUT}.partial" "${URL}"
mv "${OUT}.partial" "${OUT}"
ENDED="$(date +%s)"
BYTES="$(stat -c '%s' "${OUT}" 2>/dev/null || stat -f '%z' "${OUT}")"
SHA="$(sha256sum "${OUT}" | awk '{print $1}')"

echo "bytes=${BYTES}"
echo "sha256=${SHA}"
echo "elapsed_sec=$((ENDED - STARTED))"

if [[ -n "${REPORT}" ]]; then
  mkdir -p "$(dirname "${REPORT}")"
  python3 - "${REPORT}" "${REPO}" "${FILE}" "${REVISION}" "${OUT}" "${BYTES}" "${SHA}" "${TOKEN_PRESENT}" "$((ENDED - STARTED))" <<'PY'
import json, sys
path, repo, file, revision, out, bytes_, sha, token, elapsed = sys.argv[1:]
payload = {
    "timestamp_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    "repo": repo,
    "file": file,
    "revision": revision,
    "path": out,
    "bytes": int(bytes_),
    "sha256": sha,
    "hf_token_present": bool(int(token)),
    "elapsed_sec": int(elapsed),
    "result": "PASS",
}
with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
PY
  echo "report=${REPORT}"
fi
