# Project status

Last updated: **2026-08-16** (family queue A mostly **Runs**/one **Validated** Nano 4B; Lightning/Omni/FP8 overnight; Nano 30B still the only vLLM **Runs**)

## Research

- [x] Inspect existing repository (prior skeleton kept; missing reports/requirements/LICENSE added)
- [x] Re-check authoritative Nemotron HF IDs on 2026-08-15 (Nano, Super, Ultra, Omni, Embed, safety, Lightning)
- [x] Record sources and check dates (`docs/sources.md`)
- [x] Model inventory with Unknowns explicit
- [x] Compatibility matrix (no PASS without evidence); expanded 2026-08-16 with MI325X / MI350X / MI355X / MI350P / Radeon / Ryzen AI Strix Point, Fit vs Test vs Why-not codes
- [x] Precision analysis (NVFP4 non-portable by default)
- [x] Super BF16 vs 192 GB math
- [x] Ultra vs 192 GB math
- [x] Add Nemotron 3.5 Lightning (released 2026-08-11) as inventoried; **queued** for MI300X BF16 after small models
- [x] Confirm official Nano 4B GGUF and Embed 1B NVFP4 IDs
- [x] Re-check HF `config.json` / `auto_map` from the cached snapshot (`results/mi300x/2026-08-16_031205Z/transformers/config-excerpt.json`)

## MI300X environment

- [x] Write `scripts/mi300x/collect-env.sh`
- [x] Write isolated `setup-python-env.sh` (inspect-first, ROCm wheels only)
- [x] Run `collect-env.sh` on the MI300X host (`results/mi300x/2026-08-15_172057Z/`)
- [x] Record OS, kernel, ROCm/HIP split, driver, Python, GPU visibility
- [x] Install `python3.12-venv` only (ensurepip missing; not a ROCm/kernel change)
- [x] Create `.venv-mi300x` and install `torch[device-gfx942]==2.12.0+rocm7.14.0` + Transformers 5.15.0
- [x] Record torch HIP 7.14.60850 and device `AMD Instinct MI300X VF`
- [x] Download BF16 Nano and run Transformers smoke test

## Nano Transformers

- [x] Official BF16 ID: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16`
- [x] Smoke prompts (`prompts/smoke-tests.json`)
- [x] Reasoning probes (`prompts/reasoning-tests.json`)
- [x] `transformers-smoke-test.py`
- [x] Download BF16 on MI300X (HF cache; unauthenticated Hub still worked)
- [x] Load + generate (greedy, thinking off)
- [x] Review output reasonableness (`172810Z`; pinned reproduction `031205Z` → **Validated**)
- [x] Reasoning-on / thinking-off comparison (`results/mi300x/2026-08-16_024048Z/`)
- [x] Mark matrix PASS or FAIL from artifacts (**PASS WITH CAVEATS** / **Runs**; first FAIL preserved at `2026-08-15_172557Z`)

## Nano vLLM

- [x] Conservative `launch-vllm.sh` (no FlashInfer/NVFP4 flags)
- [x] `test-openai-api.py`
- [x] Install ROCm vLLM **only after** Transformers succeeds (AMD CDNA Docker; host py3.12 has no 7.14 wheel)
- [x] Fetch `nano_v3_reasoning_parser.py` from the official Nano repo
- [x] Serve `max-model-len=8192`, 1 GPU
- [x] Health + chat completion + sequential requests

## Nano performance

- [x] `benchmark.py` labeled engineering characterization only
- [x] `monitor-gpu.sh`
- [x] MoE autotune sanity (`benchmark_moe.py --tune`) — **FAIL**, no JSON (`results/mi300x/2026-08-16_020625Z/`)
- [x] Memory: load / idle / short generate / peak (`results/mi300x/2026-08-16_022238Z/`)
- [x] Context ladder 4K → 8K → 16K → 32K → 64K → 128K (`results/mi300x/2026-08-16_024220Z/`; filler needle/haystack)
- [x] Concurrency 1 / 2 / 4 characterization (`results/mi300x/2026-08-16_022238Z/`)
- [x] Do **not** call results official benchmarks (labeled engineering characterization only)
- [x] 128K characterized; 256K **NOT TESTED**; **do not** jump to 1M

## Super feasibility

- [x] BF16 raw weights ~240 GB / 223.5 GiB → Fit **2×** MI300X; **1× tight** MI325X; **1×** MI350X; **doesn't fit** MI350P / Radeon / Ryzen AI. Do not download on the current 1× VF
- [x] FP8 raw weights ~120 GB / 111.8 GiB → Fit **1×** MI300X, THEORETICALLY FEASIBLE, unvalidated, FP8 format risk. **Queued** as C3 ([`mi300x-next-tests.md`](mi300x-next-tests.md)); still not a PASS
- [ ] Decide later whether a multi-GPU Instinct node is in scope
- [ ] Do not download Super BF16 on the current host

## Ultra feasibility

- [x] BF16 ~1100 GB / 1024 GiB → Fit **8×** MI300X/MI325X, **4× tight** MI350X/MI355X; **doesn't fit** MI350P / Radeon / Ryzen AI
- [x] NVFP4 payload ~275 GB → Fit **2×** MI300X/MI325X, **1× tight** MI350X; **doesn't fit** PCIe/laptop; format **R-NVFP4**
- [ ] Do not download Ultra

## Radeon

- [x] Pull current ROCm supported Radeon list (W7900 48 GB, 7900 XTX, AI PRO R9700, …)
- [ ] Hands-on on any discrete Radeon — **not available in this phase**

## Ryzen AI

- [x] Write and run local discovery (repeat snapshot `2026-08-15_171202Z`; reboot session `2026-08-16_214028Z`)
- [x] Document Strix Point: Ryzen AI 9 HX 370, gfx1150, aie2 NPU, 93 GiB RAM, ROCm 6.4.3
- [x] Official Nano 4B GGUF Q4_K_M: llama.cpp **CPU Validated** (`214142Z`) and **iGPU Vulkan Validated** (`214348Z`); MI300X HIP **Validated** (`215228Z`)
- [x] Lightning ggml-org Q4_0: CPU (`223932Z`), Vulkan UMA (`224120Z`), MI300X HIP (`225542Z`) **Validated**
- [x] Unsloth Nano 30B Q4_K_M: CPU (`225528Z`), Vulkan UMA (`225631Z`), MI300X HIP (`231304Z`) **Validated** (community file)
- [ ] NPU: no Nemotron path identified; keep **NOT TESTED** / **R-NPU**

## Executive / BD reports

- [x] First drafts (planning/feasibility language only)
- [x] Update after MI300X Transformers result
- [x] Update after vLLM result
- [x] Update after engineering characterization
- [x] Update after thinking probes + 128K ladder
- [x] Update after pinned Transformers smoke (**Validated**)

- [x] Immediate operator action: family A queue executed 2026-08-16 (see [`mi300x-next-tests.md`](mi300x-next-tests.md))
- [x] Overnight remainder on the MI300X host: family A documented; Lightning **Validated**; Omni BF16 **FAIL** RADIO; FP8 **FAIL** mamba-ssm

**Next MI300X work** is queued in [`mi300x-next-tests.md`](mi300x-next-tests.md) (small models A1–A12, then Lightning/Omni BF16, then FP8 FNUZ). Do **not** copy NVIDIA FlashInfer / NVFP4 flags. Copy any new `results/mi300x/<timestamp>/` tree back before changing matrix cells.

Do **not** download Super BF16 or Ultra.

## MI300X next-test queue

- [ ] A — Nano 4B, Embed 1B/8B, retriever v2, Parse 2.0, ASR 3.5, Content Safety 3.5, Safety Guard 8B v3 ([`mi300x-next-tests.md`](mi300x-next-tests.md))
- [ ] B — Lightning 30B BF16 (no FlashInfer); Nano Omni 30B BF16 (text first)
- [ ] C — Nano FP8, Omni FP8, Super FP8 only (**R-FNUZ**). Lightning FP8: no official ID, skip. No NVFP4.
