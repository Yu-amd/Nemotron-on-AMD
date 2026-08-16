# Local Strix Point laptop

**Discovery date:** 2026-08-15  
**Latest evidence:** [`results/ryzen-ai/2026-08-15_171202Z/environment/`](../../results/ryzen-ai/2026-08-15_171202Z/environment/)  
**Earlier same-day snapshot:** [`results/ryzen-ai/2026-08-15_162031Z/environment/`](../../results/ryzen-ai/2026-08-15_162031Z/environment/)  
**Nemotron execution:** official Nano 4B Q4_K_M, Lightning ggml-org Q4_0, and Unsloth Nano 30B Q4_K_M GGUF are **Validated** on CPU and on iGPU Vulkan UMA. Dedicated 512 MB still **doesn't fit**. NPU still **NOT TESTED**.

## Detected configuration

| Item | Observed value |
| --- | --- |
| Hostname | `yu-framework00` |
| Product line | Framework laptop (PCI subsystem `f111:000b`) |
| OS | Ubuntu 24.04.3 LTS (noble) |
| Kernel | `6.17.0-35-generic` |
| CPU | **AMD Ryzen AI 9 HX 370 w/ Radeon 890M** (AuthenticAMD, family 26, model 36) |
| Cores / threads | 12 cores / 24 threads |
| CPU max MHz | ~5158 |
| System RAM | **93 GiB** total; ~83 GiB available at snapshot |
| Swap | 8.0 GiB |
| User groups (relevant) | `video`, `render`, `docker`, `ollama` |
| Python on PATH | 3.12.12 (`/home/yw/.local/bin/python3`) |
| torch / transformers / vllm | **not installed** in that interpreter |

## Compute target 1 — CPU

`rocminfo` Agent 1 is the CPU with ~93 GiB fine-grained HSA pools. Official Nano 4B GGUF Q4_K_M **Validated** on CPU: `results/ryzen-ai/2026-08-16_214142Z/`. Lightning ggml-org Q4_0 **Validated** on CPU: `results/ryzen-ai/2026-08-16_223932Z/`. Unsloth Nano 30B Q4_K_M **Validated** on CPU: `results/ryzen-ai/2026-08-16_225528Z/` (community file).

## Compute target 2 — Radeon iGPU

| Item | Observed value |
| --- | --- |
| rocminfo name | `gfx1150` |
| Marketing name | AMD Radeon Graphics (Radeon 890M per CPU string) |
| Device type | GPU, memory properties **APU** |
| Compute units (rocminfo / amd-smi) | **16** |
| ISA | `amdgcn-amd-amdhsa--gfx1150` and `gfx11-generic` |
| PCI | `1002:150e` rev c1, driver **amdgpu** |
| VBIOS | `STRIX_B0_GENERIC` |
| HIP | 6.4.43484 (`hipconfig`) |
| ROCm | **6.4.3** (`/opt/rocm/.info/version`, `/opt/rocm-6.4.3`) |
| Devices | `/dev/kfd`, `/dev/dri/card1`, `/dev/dri/renderD128` |
| amd-smi VRAM SIZE | **512 MB** |
| rocminfo GPU coarse pool | **49067304 KB (~46.8 GiB)** |
| rocm-smi at idle | **VRAM% 90%**, GPU% 7%, edge 63 °C |
| OpenCL | AMD APP platform; GPU; `clinfo` max alloc ~39.8 GB; **clinfo CU count 8** (disagrees with rocminfo 16 — do not guess which to trust for kernels) |
| vulkaninfo | **not installed** |

**Interpretation (conservative):**

- There is a working ROCm/HIP stack for gfx1150.
- Dedicated VRAM window is tiny (512 MB) and already reported ~90% used (display).
- A ~47 GiB HSA coarse pool does **not** mean “47 GiB free for Nemotron.”
- vLLM’s ROCm hardware list (checked 2026-08-15) includes Ryzen AI 300 / gfx1150, requiring **ROCm 7.0.2+**. This laptop is on **ROCm 6.4.3**. That is a **possible BLOCKER** for vLLM-on-iGPU, not a Nemotron result.
- Nano 30B BF16 (~56 GiB weights) is **NOT PRACTICAL** as a first local iGPU experiment.
- Nano 4B BF16 (~7.4 GiB) and Embed 1B (~2.3 GiB) are **THEORETICALLY FEASIBLE** against 93 GiB RAM. **NOT TESTED.**

If Nemotron later generates via HIP on `gfx1150`, document it as **iGPU**, never as “Ryzen AI NPU.” llama.cpp **Vulkan** on this iGPU generated Nano 4B Q4_K_M (43/43 layers, `214348Z`), Lightning Q4_0 (53/53 layers, `224120Z`), and Unsloth Nano 30B Q4_K_M (53/53 layers, model buffer ~23197 MiB, `225631Z`) on `Vulkan0` (`RADV GFX1150`, ~47 GiB UMA reported). That is **not** HIP and **not** NPU. Dedicated amd-smi VRAM remains **512 MB**.

## Compute target 3 — XDNA NPU

| Item | Observed value |
| --- | --- |
| Kernel module | `amdxdna` loaded |
| Device node | `/dev/accel/accel0` |
| sysfs | `/sys/class/accel/accel0` |
| rocminfo Agent 3 | Name **`aie2`**, marketing **`AIE-ML`**, device type **DSP** |

This proves the **hardware and driver** are present. It does **not** prove any Nemotron model runs on the NPU.

No Hugging Face / vLLM / Transformers Nemotron-on-XDNA path was found in the 2026-08-15 research pass. Status: **NOT TESTED** and currently **no identified execution path**.

## Local Nemotron strategy (remaining)

Priority remaining on this laptop:

1. NPU: still no Nemotron path (**R-NPU**)
2. HIP on gfx1150: **NOT TESTED** (Vulkan is not HIP)
3. Discrete Radeon: none in this machine

CPU vs iGPU vs NPU must be logged separately.

Estimated Nano 30B **payload** vs 93 GiB RAM (not including KV/runtime):

| Precision | Raw GiB |
| --- | --- |
| BF16 / FP16 | 55.9 |
| FP8 / INT8 / Q8 | 27.9 |
| Q6 | 21.0 |
| Q5 | 17.5 |
| Q4 / INT4 payload | 14.0 |

BF16 30B would consume a majority of RAM before context. Skip it locally. This table is **calculator-only**, not a local PASS.
