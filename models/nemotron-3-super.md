# Nemotron 3 Super 120B-A12B

**Do not download the BF16 checkpoint onto the current 1× MI300X host.**

| | |
| --- | --- |
| Official BF16 ID | `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16` |
| Official FP8 ID | `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8` |
| NVFP4 | Sibling repo on NVIDIA lab page / HF naming `...-NVFP4` |
| Parameters | 120B total / 12B active |
| Architecture | LatentMoE + Mamba-2 + attention + MTP; NVFP4 pretraining recipe |
| Context | 1M |
| License | NVIDIA Nemotron Open Model License |
| NVIDIA min GPU | BF16: 8× H100-80GB (2× B200). FP8: 2× H100-80GB |
| vLLM (NVIDIA) | `vllm==0.18.1`; `--reasoning-parser nemotron_v3`; `--tool-call-parser qwen3_coder` |
| Release | 2026-03-11 |

Card: https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16 (checked 2026-08-15).

## OAM MI300X GPU count (raw weights)

This lab has **one** VF. Counts below are memory math for a future multi-GPU OAM node, not a PASS.

| Precision | Raw memory | vs 192 GB HBM | Fit |
| --- | --- | --- | --- |
| BF16 | ~240 GB / 223.5 GiB | Needs 2× (leftover ~72 GB/GPU) | **2×** |
| FP8 | ~120 GB / 111.8 GiB | ~72 GB leftover on 1× | **1×**; FP8 FNUZ risk; LatentMoE/MTP **unvalidated** |
| NVFP4 | ~60 GB payload | Would fit 1× if kernels existed | **1×**; **NVIDIA-specific** until proven |

On **MI350P / Radeon / Ryzen AI**, Super BF16 **doesn't fit** (PCIe/laptop: no 2×). Extra runtime overhead and KV/SSM state are **unknown**. Do not treat FP8 “fits on paper” as a PASS.

NVIDIA says B200 BF16 fits in **2 GPUs**. Two 192 GB devices is a different program than this repo’s 1 GPU.

## Next

Leave Super until Nano BF16 is Validated or a multi-GPU Instinct node is in scope.
