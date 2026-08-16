# Nemotron 3.5 Lightning 30B-A3B

Added to inventory because NVIDIA's current developer page lists it alongside Nano / Super / Ultra. BF16 Transformers on 1× MI300X is **Validated** (`062756Z`). ggml-org GGUF Q4_0 llama.cpp is **Validated** on laptop CPU/Vulkan and MI300X HIP. Not Optimized. NVFP4 **NOT TESTED**.

Checked **2026-08-16**.

| | |
| --- | --- |
| Official BF16 ID | `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16` |
| Official NVFP4 ID | `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4` |
| Speculative helpers | `...-NVFP4-DFlash`, `...-NVFP4-DSpark` |
| Parameters | 30B total / **3B** active (card; do not conflate with Nano **3.5B** active) |
| Architecture | Hybrid Mamba-2 + MoE + attention; speculative decoding (MTP / DFlash / DSpark) |
| Context | Up to 1M; NVIDIA single-H100 note uses 256K |
| NVIDIA single-GPU | 1× H100 80GB or 1× A100 80GB (BF16 card) |
| License | OpenMDW License Agreement v1.1 |
| Release | 2026-08-11 |
| NVIDIA vLLM BF16 snippet | `vllm/vllm-openai:v0.27.1` with `--mamba-backend flashinfer` — **CUDA-oriented; do not copy to MI300X** |
| GGUF | Community `ggml-org/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF` Q4_0 **Validated** llama.cpp (`223932Z`, `224120Z`, `225542Z`). Exact official NVIDIA GGUF repo ID still **Unknown**. |
| Raw BF16 weights | Same class as Nano 30B (~60 GB / 55.9 GiB). Fitting is not support. |

Card: https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16

## Why this is not the first MI300X test

1. Nano 30B BF16 is older, has a documented Transformers ≥5.3 path **without** FlashInfer in the official snippet, and is the operator's stated first target.
2. Lightning's published serving recipe leans on NVIDIA-optimized NVFP4 + FlashInfer Mamba.
3. Active-parameter and speculative-decoding details differ from Nano; do not reuse Nano results as Lightning evidence.

If Nano Transformers on MI300X **FAILS** due to architecture, Lightning is unlikely to be an easier BF16 port. If Nano **PASS**, Lightning BF16 can be queued as a separate row.
