# Nemotron 3 Ultra 550B-A55B

**Do not download this checkpoint onto the current 1× MI300X host.**

| | |
| --- | --- |
| Official BF16 ID | `nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16` |
| Official NVFP4 ID | `nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-NVFP4` |
| Parameters | 550B total / 55B active |
| Architecture | LatentMoE + Mamba-2 + attention + MTP; NVFP4 pretraining |
| Context | 1M |
| License | **OpenMDW 1.1** |
| NVIDIA min GPU | BF16: 8× B200-class or 16× H100. NVFP4: 4× B200-class or 8× H100 |
| vLLM (NVIDIA) | container `vllm/vllm-openai:v0.22.0`; `--mamba-backend flashinfer`; MTP speculative config |
| Release | 2026-06-04 |

## OAM GPU count (raw weights)

This lab has **one** VF. Counts below are memory math for a future multi-GPU OAM node, not a PASS.

| Precision | Raw memory | vs 192 GB | Fit on OAM MI300X | MI350P / Radeon / Ryzen AI |
| --- | --- | --- | --- | --- |
| BF16 | ~1100 GB / 1024 GiB | **8×** (4×192 = 768 GB is not enough) | **8×** | **doesn't fit** |
| FP8 (if produced) | ~550 GB | **4×** | **4×** | **doesn't fit** |
| NVFP4 payload | ~275 GB | **2×** | **2×**; NVIDIA-specific format | **doesn't fit** |

MI350X/MI355X BF16: **4× tight** (~13 GB leftover/GPU). MI325X BF16: **8×** (4×256 = 1024 GB < ~1100 GB).

Minimum plausible GPU count still needs ROCm vLLM LatentMoE + Mamba + MTP. **Unknown / requires validation** — not a current task.

NVIDIA BF16 notes ~1.5 TB aggregate HBM on 8× B200 for weights plus KV. That is a different class of machine than 1× MI300X.
