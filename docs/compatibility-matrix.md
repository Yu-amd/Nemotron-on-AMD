# Compatibility matrix

**Date:** 2026-08-16  
**Visual grid:** [`../canvases/compatibility-matrix.canvas.tsx`](../canvases/compatibility-matrix.canvas.tsx) (Cursor canvas: bold **VALIDATED** / **FAILED** / **NOT TESTED** / **DOESN'T FIT**).  
**Scope of this grid:** phase-1 AMD test subset (Nano / Super / Ultra / Omni / Lightning plus a few embed/safety rows). The **full NVIDIA Nemotron brand** (183 Hugging Face repos, including Parse, ASR, Labs, Llama Nemotron, Nemotron 4) is in [`nemotron-family.md`](nemotron-family.md).  
**Rule:** `THEORETICALLY FEASIBLE` is never a `PASS`. Every future `PASS` must cite `results/...`.  
**Memory:** raw weight estimates only (see [`precision-formats.md`](precision-formats.md)). Fit is **not** kernel support.  
**Hardware actually executed:** 1× Instinct **MI300X VF** (~191.7 GiB HBM). Every other SKU is spec-based **NOT YET VALIDATED** unless a cell says otherwise.

NVIDIA official software-integration lists name NVIDIA GPUs. Absence of an AMD row is **not** a FAIL; it is a lack of vendor claim.

Legend: [`terminology.md`](terminology.md). Platform notes: [`platforms/instinct/`](../platforms/instinct/), [`platforms/radeon/README.md`](../platforms/radeon/README.md), [`platforms/ryzen-ai/strix-point.md`](../platforms/ryzen-ai/strix-point.md).

## How to read a cell

Each hardware cell has two required fields:

| Field | Meaning |
| --- | --- |
| **Test** | What this repo has actually done on that SKU. |
| **Fit** | How many devices **raw weights** need. Fit is not kernel support. |

**Two device classes:**

| Class | SKUs | If weights exceed one GPU |
| --- | --- | --- |
| **OAM Instinct (scale-up)** | MI300X, MI325X, MI350X, MI355X | Do **not** write “doesn't fit.” Write the GPU count: **1×**, **2×**, **4×**, or **8×** (smallest of those where sharded weights fit). **1× tight** / **4× tight** = weights fit that count but leftover ≲ 32 GB/GPU. Infinity Fabric is assumed for the *count only* — not a PASS. |
| **Single PCIe / laptop** | **MI350P**, **Radeon**, **Ryzen AI** | PCIe GPU-to-GPU is **not** treated as an optimized scale-out path here. A Ryzen AI laptop is one machine. If it does not fit **one** card / a Ryzen AI laptop, Fit is **doesn't fit**. Never quote 2×/4×/8× for these columns. |

**Fit** values:

| Fit | Meaning |
| --- | --- |
| **1×** | Raw weights fit one GPU (leftover ≳ 32 GB). |
| **1× tight** | Weights fit one GPU; leftover ≲ 32 GB (poor for KV / SSM / MoE). |
| **2× / 4× / 8×** | OAM Instinct only. Smallest of 2/4/8 with leftover ≳ 32 GB/GPU after an even shard; append **tight** if leftover is below that but weights still fit. |
| **doesn't fit** | MI350P / Radeon / Ryzen AI only: does not fit one PCIe card or a Ryzen AI laptop. |
| **n/a** | Wrong device class, or there is no identified runtime for that precision on that target. |

Count math (OAM): leftover per GPU ≈ `HBM − weights/k`. Use vendor HBM 192 / 256 / 288 GB and calculator weights (~60 / 240 / 120 / 1100 / 275 GB). **8× MI300X** for Ultra BF16 because **4×** (768 GB) is less than ~1100 GB weights. **4× MI350X/MI355X** holds Ultra BF16 weights with ~13 GB leftover/GPU (**4× tight**).

If a configuration is **definitely not practical or not applicable**, the cell also has **Why**. Codes:

| Code | Why (not a PASS, and not “maybe later on that SKU”) |
| --- | --- |
| **R-PCIE** | Does not fit one PCIe card (MI350P 144 GB or Radeon 16–48 GB). This matrix does not count multi-GPU PCIe. |
| **R-LAPTOP** | Does not fit a Strix Point Ryzen AI laptop (93 GiB RAM / 512 MB dedicated iGPU). |
| **R-IGPU** | Strix Point iGPU reports **512 MB** dedicated VRAM (`amd-smi`). |
| **R-NPU** | No Hugging Face / vLLM / Transformers Nemotron-on-XDNA path identified (2026-08-15). Driver present ≠ model support. |
| **R-NVFP4** | Official `…-NVFP4` shards are NVIDIA E2M1 NVFP4 (ModelOpt / FlashInfer). CDNA4 **MXFP4 is a different format**. Native NVFP4 tensor execution is **not** an Instinct claim. vLLM NVFP4 *emulation* (dequant to BF16) is documented by AMD for **other** models on MI300/MI355 — **not** Nemotron evidence. |
| **R-FNUZ** | Not a hard “unsupported”: NVIDIA FP8 is typically OCP E4M3/E5M2; MI300/MI325 is **FP8 FNUZ**. Load may fail or be silently wrong. MI350-series FP8 is OCP — closer conceptually, still **untested**. |

Emulation / Quark MXFP4 from BF16 are **separate research items**, not implied by Fit: 1×.

## Platforms in this matrix

| Column | SKU / machine | Arch | Memory used for Fit | Hands-on Nemotron | Notes |
| --- | --- | --- | --- | --- | --- |
| **MI300X** | Instinct MI300X VF | CDNA3 `gfx942` | ~192 GB (VF ~191.7 GiB) | **Yes** — family queue on **1×** (Nano/Lightning Transformers **Val**; Llama.cpp HIP Nano 4B + Lightning Q4_0 **Val**; embed/tools **Runs**; Omni BF16 + three FP8 **FAIL**) | OAM-class scale-up. This lab has **one** VF. [`mi300x.md`](../platforms/instinct/mi300x.md). FP8 is **FNUZ**. No MXFP4. |
| **MI325X** | Instinct MI325X | CDNA3 `gfx942` | 256 GB HBM3E | **No** | OAM. Same ISA family as MI300X; **do not copy** MI300X results. [`mi325x.md`](../platforms/instinct/mi325x.md) |
| **MI350X** | Instinct MI350X OAM | CDNA4 `gfx950` | 288 GB HBM3E | **No** | OAM. OCP FP8 + MXFP. [`mi350x.md`](../platforms/instinct/mi350x.md) |
| **MI355X** | Instinct MI355X OAM | CDNA4 `gfx950` | 288 GB HBM3E | **No** | OAM. Same **memory** math as MI350X. [`mi355x.md`](../platforms/instinct/mi355x.md) |
| **MI350P** | Instinct MI350P **PCIe** | CDNA4 (LLVM **unconfirmed**) | **144 GB HBM3E** | **No** | **PCIe.** If it does not fit one card → **doesn't fit**. Not named on the ROCm Instinct GPU table fetched 2026-08-16. [`mi350p.md`](../platforms/instinct/mi350p.md) |
| **Radeon** | Discrete ROCm-listed **PCIe** cards | RDNA3/4 | **16–48 GB** GDDR (no discrete card in this project) | **No** | **PCIe.** Upper bound: PRO W7900 **48 GB**. [`radeon/README.md`](../platforms/radeon/README.md) |
| **Ryzen AI** | Strix Point **laptop** | CPU + `gfx1150` iGPU + XDNA NPU | iGPU dedicated **512 MB**; unified RAM **93 GiB** | **Yes** — Nano 4B / Lightning Q4_0 / Unsloth 30B Q4_K_M GGUF CPU + Vulkan iGPU | One machine. If it does not fit on that laptop → **doesn't fit**. Dedicated 512 MB **doesn't fit** 18–25 GB GGUFs; Vulkan UMA **did** hold them. NPU **R-NPU**. vLLM gfx1150 wants ROCm **7.0.2+**; that laptop is **6.4.3** (vLLM note, not llama.cpp). [`strix-point.md`](../platforms/ryzen-ai/strix-point.md) |

All Instinct columns except executed **MI300X** cells: **NOT YET VALIDATED**. Multi-GPU counts on OAM are memory math, not a node we have.

---

## Weight vs memory (Fit only)

**Fit: 1× / 2× / 4× / 8× does not mean Test: PASS.**

| Model | Precision | ~Weights | MI300X 192 | MI325X 256 | MI350X 288 | MI355X 288 | MI350P 144 (PCIe) | Radeon 16–48 (PCIe) | Ryzen AI laptop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Nano 30B-A3B | BF16 | ~60 GB / 56 GiB | **1×** | **1×** | **1×** | **1×** | **1×** | **doesn't fit** | **doesn't fit** |
| Nano 30B-A3B | FP8 | ~30 GB / 28 GiB | **1×** | **1×** | **1×** | **1×** | **1×** | **1× tight** on 32–48 GB; **doesn't fit** on 16–24 GB | **doesn't fit** iGPU; CPU **1×**; NPU **n/a** |
| Nano 30B-A3B | NVFP4 | ~15 GB payload (~21 GB Omni-class card) | **1×** | **1×** | **1×** | **1×** | **1×** | **1×** on 24–48 GB; **doesn't fit** on 16 GB | **doesn't fit** iGPU; CPU **1×**; NPU **n/a** |
| Nano 30B-A3B | GGUF Q4_K_M (Unsloth, community) | **24.57 GB** (22.88 GiB) | **1×** | **1×** | **1×** | **1×** | **1×** | **1×** on 24 GB+ | CPU **1×**; Vulkan UMA **1×** (~47 GiB visible); dedicated 512 MB **doesn't fit** (**R-IGPU**); NPU **n/a** |
| Lightning 30B-A3B | BF16 | ~60 GB / 56 GiB | **1×** | **1×** | **1×** | **1×** | **1×** | **doesn't fit** | **doesn't fit** |
| Lightning 30B-A3B | GGUF Q4_0 (ggml-org) | **18.90 GB** (17.60 GiB) | **1×** | **1×** | **1×** | **1×** | **1×** | **1×** on 24 GB+ | CPU **1×**; Vulkan UMA **1×** (~47 GiB visible); dedicated 512 MB **doesn't fit** (**R-IGPU**); NPU **n/a** |
| Lightning 30B-A3B | GGUF Q8_0 (ggml-org) | **33.59 GB** | **1×** | **1×** | **1×** | **1×** | **1×** | **1×** on 48 GB | CPU **1×**; iGPU **R-IGPU**; NPU **n/a** |
| Lightning 30B-A3B | NVFP4 | ~15 GB class | **1×** | **1×** | **1×** | **1×** | **1×** | **1×** on 24–48 GB | **doesn't fit** iGPU; CPU **1×**; NPU **n/a** |
| Nano 4B | BF16 | ~8 GB / 7.4 GiB | **1×** | **1×** | **1×** | **1×** | **1×** | **1×** on 16 GB+ | CPU **1×**; iGPU unknown for BF16; NPU **n/a** |
| Nano 4B | GGUF Q4_K_M (official) | **2.84 GB** (2.64 GiB) | **1×** | **1×** | **1×** | **1×** | **1×** | **1×** | CPU **1×**; Vulkan UMA **1×** (~47 GiB visible on this APU); dedicated 512 MB **doesn't fit**; NPU **n/a** |
| Super 120B-A12B | BF16 | ~240 GB / 224 GiB | **2×** | **1× tight** (~16 GB leftover) | **1×** (~48 GB leftover) | **1×** | **doesn't fit** | **doesn't fit** | **doesn't fit** |
| Super 120B-A12B | FP8 | ~120 GB / 112 GiB | **1×** | **1×** | **1×** | **1×** | **1× tight** (~24 GB leftover) | **doesn't fit** | **doesn't fit** |
| Super 120B-A12B | NVFP4 | ~60 GB payload | **1×** | **1×** | **1×** | **1×** | **1×** | **doesn't fit** (60 > 48) | **doesn't fit** |
| Ultra 550B-A55B | BF16 | ~1100 GB | **8×** | **8×** | **4× tight** (~13 GB/GPU leftover) | **4× tight** | **doesn't fit** | **doesn't fit** | **doesn't fit** |
| Ultra 550B-A55B | NVFP4 | ~275 GB payload | **2×** | **2×** | **1× tight** (~13 GB leftover) | **1× tight** | **doesn't fit** | **doesn't fit** | **doesn't fit** |
| Nano Omni 30B | BF16 | 62 GB listed | **1×** | **1×** | **1×** | **1×** | **1×** | **doesn't fit** | **doesn't fit** |
| Nano Omni 30B | FP8 | 33 GB listed | **1×** | **1×** | **1×** | **1×** | **1×** | **1× tight** on 48 GB; **doesn't fit** on 16–24 GB | **doesn't fit** iGPU; CPU **1×**; NPU **n/a** |
| Nano Omni 30B | NVFP4 | 21 GB listed | **1×** | **1×** | **1×** | **1×** | **1×** | **1×** on 24–48 GB | **doesn't fit** iGPU; CPU **1×**; NPU **n/a** |
| Embed 1B | BF16 | ~2.3 GB | **1×** | **1×** | **1×** | **1×** | **1×** | **1×** | CPU **1×**; iGPU unknown; NPU **n/a** |
| Embed 1B | NVFP4 | ~0.5 GiB naive | **1×** | **1×** | **1×** | **1×** | **1×** | **1×** | CPU **1×**; NPU **n/a** |
| Embed 8B | BF16 | ~16 GB | **1×** | **1×** | **1×** | **1×** | **1×** | **1×** on 24 GB+; **doesn't fit** on 16 GB | CPU **1×**; iGPU unknown; NPU **n/a** |
| Safety Reasoning 4B | BF16 (assumed) | ~8 GB | **1×** | **1×** | **1×** | **1×** | **1×** | **1×** | CPU **1×**; iGPU unknown; NPU **n/a** |
| Safety Guard 8B v3 | BF16 (assumed) | ~16 GB | **1×** | **1×** | **1×** | **1×** | **1×** | **1×** on 24 GB+ | CPU **1×**; iGPU unknown; NPU **n/a** |

---

## Test status + why not (if closed)

**Test** abbreviations: **Val** = Validated; **Runs** = Runs / PASS WITH CAVEATS; **NT** = NOT TESTED; **NYV** = NOT YET VALIDATED (spec only, no SKU in lab); **NP** = NOT PRACTICAL (single PCIe/laptop **doesn't fit**); **NA** = NOT APPLICABLE.

MI325X / MI350X / MI355X / MI350P share “NYV” even when Fit is **1×**: no card, no `results/`. OAM **2×/4×/8×** is also NYV — this project has not attached a multi-GPU node.

### Generative

| Model | Prec | MI300X | MI325X | MI350X | MI355X | MI350P (PCIe) | Radeon discrete | Ryzen AI laptop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Nano 30B-A3B | BF16 | **Test: Val + Runs** on **1×**. Transformers greedy thinking-off **Validated** (`031205Z`). Thinking probes + vLLM serve/characterization/128K **Runs**. Not Optimized; not 256K/1M. **Fit: 1×.** | **NYV.** Fit: **1×**. Same ISA family as MI300X reduces *some* kernel risk; still needs a run. | **NYV.** Fit: **1×**. New ISA (`gfx950`); do not copy MI300X PASS. | **NYV.** Fit: **1×**. Same memory class as MI350X. | **NYV.** Fit: **1×**. Less leftover than MI300X. SKU not on ROCm Instinct name list (fetched 2026-08-16). | **NP.** Fit: **doesn't fit**. **R-PCIE** (56 GiB > 48 GB). | **NP.** Fit: **doesn't fit**. **R-LAPTOP** (56 GiB weights + KV vs 93 GiB; iGPU **R-IGPU**). NPU **R-NPU**. ROCm 6.4.3 vs vLLM gfx1150 floor 7.0.2+ is a **possible BLOCKER** for iGPU vLLM. |
| Nano 30B-A3B | FP8 | **Test: FAIL** `mamba-ssm` import (`062923Z`). **R-FNUZ**. **Fit: 1×**. | **NYV.** Fit: **1×**. **R-FNUZ**. | **NYV.** Fit: **1×**. OCP FP8 is a closer *match* than MI300; still **not** a PASS. | **NYV.** Fit: **1×**. | **NYV.** Fit: **1×**. Family OCP **unconfirmed** on this SKU. | **NT.** Fit: **1× tight** on 32–48 GB; **doesn't fit** 16–24 GB. Format + hybrid MoE kernels unknown. | **NT.** Fit: **1×** on CPU RAM. Dedicated iGPU **doesn't fit** (**R-IGPU**); NPU **R-NPU**. |
| Nano 30B-A3B | NVFP4 | **NT.** Fit: **1×**. **R-NVFP4.** Emulation **not tested** (do not copy FlashInfer). | **NYV.** Fit: **1×**. **R-NVFP4** (no MXFP on CDNA3). | **NYV.** Fit: **1×**. MXFP4 **≠** NVFP4 (**R-NVFP4**). | **NYV.** Fit: **1×**. **R-NVFP4.** | **NYV.** Fit: **1×**. MXFP4 on the product page **≠** NVFP4 (**R-NVFP4**). | **NT.** Fit: **1×** on 24–48 GB. **R-NVFP4**. | **NT / NA** native. **R-NVFP4** + **R-NPU**. CPU GGUF is a different 4-bit. |
| Nano 30B-A3B | GGUF Q4_K_M (Unsloth, community) | **Test: Val** HIP `ROCm0` gfx942 (`231304Z`). 53/53 layers, model buffer ~23197 MiB. Community `unsloth/` file, not official NVIDIA 30B GGUF. **Fit: 1×.** | **NYV.** Fit: **1×**. | **NYV.** | **NYV.** | **NYV.** | **NT.** More realistic than BF16. Discrete HIP/Vulkan **unknown**. | **Test: Val** CPU (`225528Z`) and **Val** iGPU Vulkan RADV GFX1150 UMA (`225631Z`), 53/53 layers, model buffer ~23197 MiB. Dedicated 512 MB **doesn't fit**; NPU **R-NPU**. |
| Lightning 30B-A3B | BF16 | **Test: Val** greedy thinking-off on **1×** (`062756Z`). vLLM **Runs** `8192` (`170852Z`). Not Nano. **Fit: 1×.** | **NYV.** Fit: **1×**. | **NYV.** | **NYV.** | **NYV.** Fit: **1×**. | **NP.** Fit: **doesn't fit**. **R-PCIE**. | **NP.** Fit: **doesn't fit**. **R-LAPTOP**. |
| Lightning 30B-A3B | GGUF Q4_0 (ggml-org) | **Test: Val** HIP `ROCm0` gfx942 (`225542Z`). 53/53 layers, model buffer ~17658 MiB. File `NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q4_0.gguf`. **Fit: 1×.** | **NYV.** | **NYV.** | **NYV.** | **NYV.** | **NT.** | **Test: Val** CPU (`223932Z`) and **Val** iGPU Vulkan RADV GFX1150 UMA (`224120Z`), 53/53 layers. Dedicated 512 MB **doesn't fit**; NPU **R-NPU**. |
| Lightning 30B-A3B | NVFP4 | **NT.** Fit: **1×**. **R-NVFP4**. | **NYV.** **R-NVFP4.** | **NYV.** **R-NVFP4.** | **NYV.** **R-NVFP4.** | **NYV.** **R-NVFP4.** | **NT.** **R-NVFP4.** | **NT.** **R-NVFP4** / **R-NPU**. |
| Nano 4B | BF16 | **Test: Val** greedy thinking-off on **1×** (`054423Z`). vLLM **Runs** `8192` (`170637Z`). **Fit: 1×.** | **NYV.** Fit: **1×**. | **NYV.** | **NYV.** | **NYV.** | **NT.** Fit: **1×** on 16 GB+. Best later Radeon candidate after Embed. | **NT.** CPU Fit: **1×**. iGPU kernels **unknown**. NPU **R-NPU**. Later local candidate. |
| Nano 4B | FP8 | **Test: Runs** looping `A` (`170427Z`). **R-FNUZ**. **Fit: 1×**. Not Validated. | **NYV.** **R-FNUZ.** | **NYV.** | **NYV.** | **NYV.** | **NT.** | **NT.** |
| Nano 4B | GGUF Q4_K_M (official) | **Test: Val** HIP `ROCm0` gfx942 (`215228Z`). 43/43 layers. **Fit: 1×.** | **NYV.** | **NYV.** | **NYV.** | **NYV.** | **NT.** | **Test: Val** CPU (`214142Z`) and **Val** iGPU Vulkan RADV GFX1150 UMA (`214348Z`). Dedicated 512 MB **doesn't fit**; Vulkan reported ~47 GiB. NPU **R-NPU**. |
| Super 120B-A12B | BF16 | **NT.** Fit: **2×** (240 ≰ 192; 2× leftover ~72 GB/GPU). This lab is 1× VF — do not download here. LatentMoE + MTP unvalidated. | **NYV.** Fit: **1× tight** (~16 GB leftover). Long context not assumed. | **NYV.** Fit: **1×** (~48 GB leftover). Kernels unvalidated. | **NYV.** Fit: **1×**. | **NP.** Fit: **doesn't fit**. **R-PCIE** (224 > 144). | **NP.** Fit: **doesn't fit**. **R-PCIE**. | **NP.** Fit: **doesn't fit**. **R-LAPTOP**. |
| Super 120B-A12B | FP8 | **Test: FAIL** `mamba-ssm` import (`063022Z`). **Fit: 1×**. **R-FNUZ** + LatentMoE + MTP. | **NYV.** Fit: **1×**. **R-FNUZ.** | **NYV.** Fit: **1×**. OCP closer; still untested. | **NYV.** | **NYV.** Fit: **1× tight**. | **NP.** Fit: **doesn't fit**. **R-PCIE** (112 > 48). | **NP.** Fit: **doesn't fit**. **R-LAPTOP**. |
| Super 120B-A12B | NVFP4 | **NT.** Fit: **1×**. **R-NVFP4.** | **NYV.** **R-NVFP4.** | **NYV.** **R-NVFP4.** | **NYV.** **R-NVFP4.** | **NYV.** Fit: **1×**. **R-NVFP4.** | **NP.** Fit: **doesn't fit** (60 > 48) plus **R-NVFP4**. | **NP.** Fit: **doesn't fit**. **R-LAPTOP** / **R-NVFP4**. |
| Ultra 550B-A55B | BF16 | **NT.** Fit: **8×** (4×192 = 768 GB < ~1100 GB). No 8-GPU node here. Do not download to 1× VF. | **NT.** Fit: **8×** (4×256 = 1024 GB < ~1100 GB). | **NYV.** Fit: **4× tight** (~13 GB/GPU leftover). | **NYV.** Fit: **4× tight**. | **NP.** Fit: **doesn't fit**. **R-PCIE**. | **NP.** Fit: **doesn't fit**. **R-PCIE**. | **NP.** Fit: **doesn't fit**. **R-LAPTOP**. |
| Ultra 550B-A55B | NVFP4 | **NT.** Fit: **2×** plus **R-NVFP4**. Do not download to 1× VF. | **NT.** Fit: **2×** plus **R-NVFP4**. | **NYV.** Fit: **1× tight** (~13 GB leftover) plus **R-NVFP4**. | **NYV.** Fit: **1× tight** plus **R-NVFP4**. | **NP.** Fit: **doesn't fit**. **R-PCIE** (275 > 144) **and** **R-NVFP4**. | **NP.** Fit: **doesn't fit**. | **NP.** Fit: **doesn't fit**. |
| Nano Omni 30B | BF16 | **Test: FAIL** RADIO `min_resolution_step` after FA2/Tee workarounds (`063955Z`; earlier FA2 `062426Z`). **Fit: 1×**. | **NYV.** Fit: **1×**. | **NYV.** | **NYV.** | **NYV.** Fit: **1×**. | **NP.** Fit: **doesn't fit**. **R-PCIE**. | **NP.** Fit: **doesn't fit**. **R-LAPTOP**. |
| Nano Omni 30B | FP8 | **Test: FAIL** `mamba-ssm` import (`063016Z`). **Fit: 1×**. **R-FNUZ**. | **NYV.** **R-FNUZ.** | **NYV.** | **NYV.** | **NYV.** | **NT.** Fit **1× tight** on 48 GB; **doesn't fit** 16–24 GB. | **NT.** Fit: **1×** on CPU RAM. Dedicated iGPU **doesn't fit**; NPU **R-NPU**. |
| Nano Omni 30B | NVFP4 | **NT.** Fit: **1×**. **R-NVFP4.** | **NYV.** **R-NVFP4.** | **NYV.** **R-NVFP4.** | **NYV.** **R-NVFP4.** | **NYV.** **R-NVFP4.** | **NT.** **R-NVFP4.** | **NT.** **R-NVFP4** / **R-NPU**. |

### Embedding / safety

| Model | Prec | MI300X | MI325X | MI350X | MI355X | MI350P (PCIe) | Radeon discrete | Ryzen AI laptop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Embed 1B | BF16 | **Test: Runs** SDPA cosine (`054857Z`). Not MTEB. **Fit: 1×.** | **NYV.** Fit: **1×**. | **NYV.** | **NYV.** | **NYV.** | **NT.** Fit: **1×**. Strong later discrete-GPU candidate. | **NT.** CPU Fit: **1×**. Later local #1. iGPU **unknown**. NPU **R-NPU**. |
| Embed 1B | NVFP4 | **NT.** Fit: **1×**. **R-NVFP4** (ModelOpt). | **NYV.** **R-NVFP4.** | **NYV.** **R-NVFP4.** | **NYV.** | **NYV.** **R-NVFP4.** | **NT / NA** native. **R-NVFP4.** | **NA** native. **R-NVFP4** / **R-NPU**. |
| Embed 8B | BF16 | **Test: Runs** cosine (`055129Z`). **Fit: 1×.** | **NYV.** | **NYV.** | **NYV.** | **NYV.** | **NT.** Fit: **1×** on 24 GB+. | **NT.** CPU Fit: **1×**. NPU **R-NPU**. |
| Rerank 1B v2 | BF16 | **Test: Runs** text pair (`055206Z`). **Fit: 1×.** | **NYV.** | **NYV.** | **NYV.** | **NYV.** | **NT.** Fit: **1×**. | **NT.** CPU Fit: **1×**. NPU **R-NPU**. |
| VL embed 1B v2 | BF16 | **Test: Runs** dummy PNG; empty `CausalLMOutputWithPast` (`062402Z`). **Fit: 1×.** | **NYV.** | **NYV.** | **NYV.** | **NYV.** | **NT.** Fit: **1×**. | **NT.** CPU Fit: **1×**. NPU **R-NPU**. |
| VL embed 1B v2 | FP8 | **Test: FAIL** `create_bidirectional_mask` (`170519Z`). **R-FNUZ**. **Fit: 1×.** | **NYV.** | **NYV.** | **NYV.** | **NYV.** | **NT.** | **NT.** |
| VL rerank 1B v2 | BF16 | **Test: Runs** **text** path only (`055737Z`). **Fit: 1×.** | **NYV.** | **NYV.** | **NYV.** | **NYV.** | **NT.** Fit: **1×**. | **NT.** CPU Fit: **1×**. NPU **R-NPU**. |
| VL rerank 1B v2 | FP8 | **Test: FAIL** ranking relevant < irrelevant (`170557Z`). Loaded. **R-FNUZ**. **Fit: 1×.** | **NYV.** | **NYV.** | **NYV.** | **NYV.** | **NT.** | **NT.** |
| ColEmbed VL 3B/4B/8B | BF16 | **Test: Runs** dummy PNG (`055802Z`, `061905Z`, `061921Z`). **Fit: 1×.** | **NYV.** | **NYV.** | **NYV.** | **NYV.** | **NT.** 8B Fit: **1×** on 24 GB+. | **NT.** CPU Fit: **1×**. NPU **R-NPU**. |
| Omni embed 3B | BF16 | **Test: Runs** dummy image (`061940Z`). Not Omni 30B LM. **Fit: 1×.** | **NYV.** | **NYV.** | **NYV.** | **NYV.** | **NT.** Fit: **1×**. | **NT.** CPU Fit: **1×**. NPU **R-NPU**. |
| Parse 2.0 | BF16 | **Test: Runs** dummy PNG generate (`063558Z`). Not OCR eval. **Fit: 1×.** | **NYV.** | **NYV.** | **NYV.** | **NYV.** | **NT.** Fit: **1×**. | **NT.** CPU Fit: **1×**. NPU **R-NPU**. |
| ASR 3.5 0.6B | default | **Test: Runs** pipeline (`060037Z`). Tone → empty text. **Fit: 1×.** | **NYV.** | **NYV.** | **NYV.** | **NYV.** | **NT.** Fit: **1×**. | **NT.** CPU Fit: **1×**. NPU **R-NPU**. |
| Safety Reasoning 4B | BF16 (assumed) | **Test: Runs** Content Safety 3.5 Gemma-3 (`055324Z`). Not hybrid Nemotron LM. **Fit: 1×.** | **NYV.** | **NYV.** | **NYV.** | **NYV.** | **NT.** Fit: **1×**. | **NT.** CPU Fit: **1×**. NPU **R-NPU**. |
| Safety Guard 8B v3 | BF16 (assumed) | **Test: Runs** generate (`055356Z`). Guard schema not applied. **Fit: 1×.** | **NYV.** | **NYV.** | **NYV.** | **NYV.** | **NT.** Fit: **1×** on 24 GB+. | **NT.** CPU Fit: **1×**. Generic Llama GGUF maybe later. NPU **R-NPU**. |

---

## Runtime notes (not extra hardware columns)

These are stack questions. A Transformers PASS is not a vLLM PASS.

| Model / prec | Transformers (AMD) | vLLM (ROCm) | llama.cpp (HIP/Vulkan) |
| --- | --- | --- | --- |
| Nano 30B BF16 | **Validated** greedy thinking-off on 1× MI300X VF, Transformers 5.15.0, revision `2d59de1…`. Thinking on/off **Runs**. | **Runs** / PASS WITH CAVEATS on AMD Docker vLLM 0.23.1.dev1 through 128K needle/haystack. Missing default fused-MoE / Mamba SSU AMD configs; Triton paged-attn fallback. | Community Unsloth Q4_K_M **Validated** CPU/Vulkan/HIP (`225528Z`, `225631Z`, `231304Z`). Not this BF16 file |
| Nano 30B FP8 | **FAIL** `mamba-ssm` (`062923Z`). **R-FNUZ.** Do not install CUDA mamba-ssm. | **NT.** | N/A as official GGUF |
| Nano 30B NVFP4 | NVIDIA snippet is NVIDIA HW — **not** AMD evidence. **R-NVFP4.** | NVIDIA flags include `modelopt_fp4` / FlashInfer MoE FP4 — **do not copy**. AMD emulation **not tested** on Nemotron. | **NA** for NVFP4 shards |
| Nano 4B BF16 / official GGUF | **Validated** BF16 greedy (`054423Z`). | **Runs** (`170637Z`). | Official Q4_K_M **Validated** laptop CPU (`214142Z`), iGPU Vulkan (`214348Z`), 1× MI300X HIP (`215228Z`) |
| Lightning BF16 / ggml-org GGUF | **Validated** greedy thinking-off (`062756Z`). | **Runs** `8192` (`170852Z`). Do not copy `--mamba-backend flashinfer`. | Q4_0 **Validated** CPU/Vulkan/HIP (`223932Z`, `224120Z`, `225542Z`) |
| Super BF16 | **NT.** Fit **2×** MI300X / **1× tight** MI325X / **1×** MI350X. | NVIDIA TP recipes are CUDA-scale-out. AMD multi-GPU **NYV**. | Unknown |
| Ultra BF16 | **NT.** Fit **8×** MI300X/MI325X / **4× tight** MI350X/MI355X. | NVIDIA 8×B200 / 16×H100. AMD **NYV**. | Unknown |
| Embed / safety / ASR | Embed + safety **Runs** Transformers on MI300X. ASR pipeline **Runs**. vLLM **NT.** | **NT.** | Llama-family GGUF maybe; **NT.** |

---

## Evidence (MI300X Nano 30B BF16 only)

| What | Path |
| --- | --- |
| Env | `results/mi300x/2026-08-15_172057Z/environment/` |
| Transformers first FAIL (harness) | `results/mi300x/2026-08-15_172557Z/` |
| Transformers first PASS | `results/mi300x/2026-08-15_172810Z/transformers/result.json` |
| Transformers Validated pinned smoke | `results/mi300x/2026-08-16_031205Z/transformers/result.json` |
| vLLM OpenAI | `results/mi300x/2026-08-15_223840Z/vllm/openai-api/summary.json` |
| Characterization | `results/mi300x/2026-08-16_022238Z/benchmark/characterization.json` |
| Thinking probes | `results/mi300x/2026-08-16_024048Z/transformers/result.json` |
| 128K ladder | `results/mi300x/2026-08-16_024220Z/context-ladder/summary.json` |
| Ryzen AI Nano 4B GGUF CPU | `results/ryzen-ai/2026-08-16_214142Z/llamacpp/result.json` |
| MI300X Nano 4B GGUF HIP | `results/mi300x/2026-08-16_215228Z/llamacpp/` |

## How to update this file

After a run, change **only** the Test field (and Fit if measured memory disagrees with the calculator):

```text
MI325X / Nano 30B BF16:
Test: PASS WITH CAVEATS — …
Fit: 1×
Evidence: results/mi325x/<timestamp>/…
```

Do not promote Fit: 1×/2×/4×/8× or NYV to PASS. Do not write “doesn't fit” on OAM Instinct when a 2×/4×/8× count exists. Do not write 2×/4×/8× on MI350P, Radeon, or Ryzen AI. Do not rename NVFP4 as MXFP4.
