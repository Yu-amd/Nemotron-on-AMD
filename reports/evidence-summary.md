# Evidence summary

Ledger of claims. Confidence is not marketing language.

Checked **2026-08-16**.

## Environment and vendor cards

| Claim | Evidence | Confidence | Last validated |
| --- | --- | --- | --- |
| This Strix Point laptop is AMD Ryzen AI 9 HX 370 w/ Radeon 890M, Ubuntu 24.04.3, kernel 6.17.0-35-generic, 93 GiB RAM | `results/ryzen-ai/2026-08-15_171202Z/environment/{lscpu,os-release,uname,free}.txt` | High | 2026-08-15 |
| iGPU is gfx1150, driver amdgpu, PCI 1002:150e, dedicated VRAM 512 MB in amd-smi, idle VRAM ~90% | `{rocminfo,amd-smi-static,lspci-vga,rocm-smi}.txt` | High | 2026-08-15 |
| ROCm 6.4.3 is installed at `/opt/rocm-6.4.3` | `rocm-version.txt` | High | 2026-08-15 |
| XDNA NPU present (`amdxdna`, `/dev/accel/accel0`, rocminfo `aie2`) | `{ls-accel,rocminfo,ryzen-ai-extra}.txt` | High (hardware only) | 2026-08-15 |
| Host Python 3.12.12 has no torch | `python-version.txt`, `torch-probe.txt` | High | 2026-08-15 |
| MI300X VF env snapshot (Ubuntu 24.04, gfx942, ~191.7 GiB, HIP 7.14 vs `/opt/rocm` 7.0.2) | `results/mi300x/2026-08-15_172057Z/environment/` | High | 2026-08-15 |
| Nemotron 3 Nano 30B-A3B BF16 official ID is `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16`; 30B/3.5B; hybrid Mamba-2 MoE; Transformers ≥5.3.0; no `trust_remote_code` in official snippet | https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 | High for vendor text | 2026-08-15 |
| NVIDIA lists Nano software-integration HW as H100-80GB and A100 only | same card, Software Integration | High | 2026-08-15 |
| Nano vLLM NVIDIA recipe: `vllm>=0.12.0`, `nano_v3` plugin, `qwen3_coder`, `--trust-remote-code` | same card | High | 2026-08-15 |
| Nano 4B official BF16 ID `nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16`; ~3.97B; official GGUF `nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF` | Hugging Face | High | 2026-08-15 |
| Super BF16 raw weights ~240 GB / 223.5 GiB exceed 192 GB MI300X HBM | calculator + Super card min 8×H100 BF16 | High (feasibility) | 2026-08-15 |
| Ultra BF16 ~1.1 TB and NVFP4 payload ~256 GiB exceed 192 GB | calculator + Ultra min GPU table | High (feasibility) | 2026-08-15 |
| Omni BF16 listed 62 GB; license NVIDIA Open Model Agreement; 31B/~3B | Omni BF16 README | High for vendor text | 2026-08-15 |
| Lightning 3.5 BF16 `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16`; 30B/3B; OpenMDW 1.1; released 2026-08-11; NVIDIA BF16 vLLM uses `--mamba-backend flashinfer` | Lightning BF16 card | High for vendor text | 2026-08-15 |
| Lightning FP8: no official NVIDIA-org HF ID in the 2026-08-16 census | org list / inventory | High for that census | 2026-08-16 |
| Embed 1B NVFP4 ID `nvidia/Nemotron-3-Embed-1B-NVFP4` exists | Hugging Face | High | 2026-08-15 |
| MI300X FP8 is FNUZ; MI350 FP8 is OCP | AMD ROCm inference workload notes | High for vendor text | 2026-08-15 |
| vLLM lists gfx942 and gfx1150; gfx1150 needs ROCm 7.0.2+ | https://docs.vllm.cc/en/latest/getting_started/installation/gpu/ | High for vendor text | 2026-08-15 |

## Nano 30B-A3B

| Claim | Evidence | Confidence | Last validated |
| --- | --- | --- | --- |
| **Nemotron 3 Nano 30B BF16 loads on one MI300X VF** | `results/mi300x/2026-08-15_172810Z/transformers/result.json` load.memory_after_load (~58.9 GiB allocated) | High for this stack | 2026-08-15 |
| **Nano 30B generates reasonable greedy smoke-test output on that MI300X VF (thinking off)** | `results/mi300x/2026-08-15_172810Z/` (revision unset) and pinned `results/mi300x/2026-08-16_031205Z/transformers/result.json` + `review.md`; 5/5 | High for this prompt set and stack | 2026-08-16 |
| Transformers greedy thinking-off Nano 30B BF16 is **Validated** on this VF | `031205Z` (revision `2d59de1cbd51c0adf384eb906b766d1aee0e0517`); host env `172057Z` | High for this pair only | 2026-08-16 |
| First Transformers attempt failed before generation (`encoded.shape`) | `results/mi300x/2026-08-15_172557Z/` | High (TOKENIZER/harness) | 2026-08-15 |
| Transformers thinking-on vs thinking-off on this VF | `results/mi300x/2026-08-16_024048Z/transformers/result.json` (5/5, pinned revision) | High for this prompt set | 2026-08-16 |
| **vLLM serves Nano 30B BF16 OpenAI-compatibly at max-model-len=8192 on that MI300X VF** | `results/mi300x/2026-08-15_223840Z/vllm/openai-api/summary.json` | High for this Docker stack | 2026-08-15 |
| Short-context vLLM characterization on this VF (memory + conc 1/2/4) | `results/mi300x/2026-08-16_022238Z/benchmark/` (`characterization.json`, `memory-summary.json`, `review.md`) — **not a benchmark**, not Optimized | High for this stack, prompt, and date | 2026-08-16 |
| vLLM recovers HEAD/TAIL secrets through 128K on this VF | `results/mi300x/2026-08-16_024220Z/context-ladder/summary.json` — filler haystack, not 256K/1M, not Optimized | High for this stack and prompt | 2026-08-16 |
| **vLLM fused-MoE autotune produces a Nano MI300X JSON** | FAIL: `results/mi300x/2026-08-16_020625Z/moe-tune/summary.json` (`ActorDiedError`, no JSON) | High for this attempt | 2026-08-16 |
| Nano 30B FP8 Transformers on this VF | **FAIL** `mamba-ssm`: `results/mi300x/2026-08-16_062923Z/` | High for this stack | 2026-08-16 |
| Unsloth Nano 30B Q4_K_M llama.cpp greedy thinking-off (community, not official NVIDIA 30B GGUF) | CPU `225528Z`, Vulkan UMA `225631Z`, MI300X HIP `231304Z` | High for this file/revision/prompt set | 2026-08-16 |

## Nano 4B

| Claim | Evidence | Confidence | Last validated |
| --- | --- | --- | --- |
| Nano 4B BF16 Transformers greedy thinking-off is **Validated** on this VF | `results/mi300x/2026-08-16_054423Z/` rev `dfaf35de…`; 5/5 | High for this prompt set and stack | 2026-08-16 |
| vLLM serves Nano 4B BF16 OpenAI-compatibly at `max-model-len=8192` | `results/mi300x/2026-08-16_170637Z/vllm/openai-api/summary.json` + `review.md`. **Runs**, not Validated serving. Not 128K. | High for this Docker stack | 2026-08-16 |
| Nano 4B FP8 Transformers produces tokens but is not Validated | `results/mi300x/2026-08-16_170427Z/` — all five prompts looping `A`. **R-FNUZ**. | High for this prompt set | 2026-08-16 |
| Official Nano 4B GGUF llama.cpp greedy thinking-off | CPU `214142Z`, Vulkan UMA `214348Z`, MI300X HIP `215228Z`. First harness FAIL `214028Z-cpu`. | High for this file/revision/prompt set | 2026-08-16 |

## Lightning 30B-A3B

| Claim | Evidence | Confidence | Last validated |
| --- | --- | --- | --- |
| Lightning 30B BF16 Transformers greedy thinking-off is **Validated** on this VF | `results/mi300x/2026-08-16_062756Z/` rev `d468880b…`; 5/5. No FlashInfer. | High for this prompt set and stack | 2026-08-16 |
| vLLM serves Lightning 30B BF16 OpenAI-compatibly at `max-model-len=8192` | `results/mi300x/2026-08-16_170852Z/vllm/openai-api/summary.json` + `review.md`. **Runs**. Not Nano. Not 128K. | High for this Docker stack | 2026-08-16 |
| Lightning ggml-org Q4_0 llama.cpp greedy thinking-off | CPU `223932Z`, Vulkan UMA `224120Z`, MI300X HIP `225542Z` | High for this file/revision/prompt set | 2026-08-16 |
| Lightning Q8_0 / BF16 GGUF on AMD | none | N/A | not tested |

## Super / Ultra / Omni

| Claim | Evidence | Confidence | Last validated |
| --- | --- | --- | --- |
| Super 120B BF16 on this 1× VF | not downloaded (Fit **2×**) | N/A | not tested |
| Super 120B FP8 Transformers on this VF | **FAIL** `mamba-ssm`: `results/mi300x/2026-08-16_063022Z/`. Fit **1×**. | High for this stack | 2026-08-16 |
| Ultra any precision on this 1× VF | not downloaded (BF16 Fit **8×**; NVFP4 Fit **2×** + **R-NVFP4**) | N/A | not tested |
| Nano Omni 30B BF16 Transformers on this VF | **FAIL** RADIO `min_resolution_step`: `063955Z` (earlier FA2 `062426Z`) | High for this stack | 2026-08-16 |
| Nano Omni 30B FP8 Transformers on this VF | **FAIL** `mamba-ssm`: `results/mi300x/2026-08-16_063016Z/` | High for this stack | 2026-08-16 |
| Any NVFP4 Nemotron checkpoint executes natively on AMD | none (not downloaded) | N/A | not tested |

## Embed / parse / ASR / safety (1× MI300X Transformers)

| Claim | Evidence | Confidence | Last validated |
| --- | --- | --- | --- |
| Embed 1B BF16 mean-pool cosine **Runs** | `results/mi300x/2026-08-16_054857Z/` — not MTEB | High for this smoke | 2026-08-16 |
| Embed 8B BF16 cosine **Runs** | `results/mi300x/2026-08-16_055129Z/` | High for this smoke | 2026-08-16 |
| text rerank 1B v2 **Runs** (relevant > irrelevant) | `results/mi300x/2026-08-16_055206Z/` | High for this pair | 2026-08-16 |
| VL embed 1B v2 BF16 **Runs** dummy PNG; empty `CausalLMOutputWithPast` | `results/mi300x/2026-08-16_062402Z/` | High for this dummy | 2026-08-16 |
| VL embed 1B v2 FP8 | **FAIL** `create_bidirectional_mask`: `results/mi300x/2026-08-16_170519Z/` | High for this stack | 2026-08-16 |
| VL rerank 1B v2 BF16 **Runs** **text** path only | `results/mi300x/2026-08-16_055737Z/` | High for text pairs | 2026-08-16 |
| VL rerank 1B v2 FP8 | **FAIL** ranking relevant < irrelevant: `results/mi300x/2026-08-16_170557Z/` | High for this pair | 2026-08-16 |
| ColEmbed VL 3B / 4B / 8B v2 **Runs** dummy PNG | `055802Z`, `061905Z`, `061921Z` | High for these dummies | 2026-08-16 |
| Omni embed 3B **Runs** dummy image (not Omni 30B LM) | `results/mi300x/2026-08-16_061940Z/` | High for this dummy | 2026-08-16 |
| Parse 2.0 **Runs** dummy PNG generate | `results/mi300x/2026-08-16_063558Z/` — not OCR eval | High for this dummy | 2026-08-16 |
| ASR 3.5 0.6B pipeline **Runs**; tone → empty text | `results/mi300x/2026-08-16_060037Z/` | High for this stack / tone | 2026-08-16 |
| Content Safety 3.5 **Runs** (`User Safety: safe` shape) | `results/mi300x/2026-08-16_055324Z/` — Gemma-3; not a red-team | High for this prompt | 2026-08-16 |
| Safety Guard 8B v3 **Runs** generate; no Guard schema applied | `results/mi300x/2026-08-16_055356Z/` | High for this prompt | 2026-08-16 |

## Platforms not claimed

| Claim | Evidence | Confidence | Last validated |
| --- | --- | --- | --- |
| **Any Nemotron model runs on discrete Radeon** | none | N/A | not tested |
| **Nemotron generates on Ryzen AI iGPU via llama.cpp Vulkan UMA** | `214348Z`, `224120Z`, `225631Z` | High for these three GGUFs | 2026-08-16 |
| **Nemotron generates on Ryzen AI CPU via llama.cpp** | `214142Z`, `223932Z`, `225528Z` | High for these three GGUFs | 2026-08-16 |
| **Any Nemotron model runs on Ryzen AI NPU** | none; no path identified | N/A | not tested |
| Embed / parse / ASR / safety on the Ryzen AI laptop | none | N/A | not tested |
| Nano 4B / Lightning vLLM context ladder or characterization | none (only Nano 30B BF16) | N/A | not tested |
