# Troubleshooting

## Preserve first failure

If a command fails:

1. Save the exact command, `run-metadata.json`, environment directory, and full stdout/stderr.
2. Classify the likely layer (one label):

```text
MODEL ARCHITECTURE
TRANSFORMERS
PYTORCH
ROCM
VLLM
KERNEL
PRECISION
MEMORY
TOKENIZER
CHAT TEMPLATE
CUSTOM CODE
OTHER
```

3. Do **not** immediately `pip install` random versions. Investigate that layer.
4. Only then try a **single** justified change, in a new timestamped result directory.

## Layer hints

| Symptom | First layer to consider |
| --- | --- |
| `torch.cuda.is_available() == False` on a ROCm wheel | ROCM / PYTORCH |
| torch shows CUDA version, `torch.version.hip is None` | PYTORCH (wrong wheel) |
| `HIP out of memory` / `cuda OOM` | MEMORY |
| `import transformers` OK, `from_pretrained` architecture errors | MODEL ARCHITECTURE / TRANSFORMERS / CUSTOM CODE |
| tokenizer works, generate is garbage or empty | CHAT TEMPLATE / TOKENIZER / sampling |
| `ActorDiedError` during `benchmark_moe.py --tune` | KERNEL / VLLM — Ray worker died late in Nano MoE autotune (`2026-08-16_020625Z`); not a substitute NVIDIA JSON |
| `trust_remote_code` required error | CUSTOM CODE |
| vLLM starts, health fails | VLLM |
| vLLM cannot parse `<think>` | VLLM / CHAT TEMPLATE (missing nano_v3 plugin) |
| FP8 load mismatch / NaNs | PRECISION |
| kernel illegal instruction / missing hipblaslt op | KERNEL / ROCM |

## Known NVIDIA flags to drop on AMD

Do not add these “to match the cookbook” unless we have AMD docs saying they apply:

- `--mamba-backend flashinfer`
- `VLLM_USE_FLASHINFER_MOE_FP4`
- `VLLM_FLASHINFER_MOE_BACKEND=...`
- `--quantization modelopt_fp4`
- TensorRT-LLM `trtllm-serve`
- CUDA index URLs (`/whl/cu118`, `cu121`, `cu124`, `cu128`, `cu129`)

## Setup

- System Python is never the install target. Use `.venv-mi300x`.
- If `setup-python-env.sh --install` refuses because ROCm is unrecognized: collect `results/mi300x/<ts>/environment/` and map the wheel **manually**. That is a valid BLOCKED result.
