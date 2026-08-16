# MI300X next-test queue

**Platform:** 1× Instinct MI300X VF (~191.7 GiB HBM).  
**Status words:** queued rows are **NOT TESTED** until a `results/mi300x/<timestamp>/` tree exists. Fit is not a PASS.  
**Do not copy** `--mamba-backend flashinfer`, FlashInfer MoE, NVFP4, or NIM/TRT-LLM flags.  
**Do not download** Super **BF16**, any Ultra checkpoint, or NVFP4 in this queue.  
**Do not** treat a Nano 30B BF16 result as evidence for any other row.

Nano 30B-A3B BF16 is **already done** (Transformers **Validated**, vLLM **Runs**) and is not in this queue.

Lightning **FP8**: no official `…Lightning…-FP8` repo on the NVIDIA org list (2026-08-16). Do not substitute NVFP4.

Each run still pins a revision and uses a new timestamped results dir.

---

## A — small models (1× leftover large)

| # | Product | HF ID | Outcome (1× MI300X VF Transformers) | Evidence |
| --- | --- | --- | --- | --- |
| A1 | Nano 4B BF16 | `nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16` | **Validated** greedy thinking-off 5/5. Not MoE. Not vLLM. | `2026-08-16_054423Z` rev `dfaf35de…` |
| A2 | Embed 1B BF16 | `nvidia/Nemotron-3-Embed-1B-BF16` | **Runs** mean-pool cosine. Not MTEB. | `2026-08-16_054857Z` rev `9e0b2485…` |
| A3 | Embed 8B BF16 | `nvidia/Nemotron-3-Embed-8B-BF16` | **Runs** cosine. Yarn warning. | `2026-08-16_055129Z` rev `c44c20ab…` |
| A4 | text rerank 1B v2 | `nvidia/llama-nemotron-rerank-1b-v2` | **Runs** relevant>irrelevant scores. Custom `llama_bidirec`. | `2026-08-16_055206Z` rev `d896ceda…` |
| A5 | VL embed 1B v2 | `nvidia/llama-nemotron-embed-vl-1b-v2` | **Runs** load/forward dummy PNG. Empty `CausalLMOutputWithPast` (no embedding tensor). | `2026-08-16_062402Z` rev `582e3bf7…` |
| A6 | VL rerank 1B v2 | `nvidia/llama-nemotron-rerank-vl-1b-v2` | **Runs** **text** path. Images not passed. | `2026-08-16_055737Z` rev `9c20c4ae…` |
| A7a | ColEmbed VL 3B v2 | `nvidia/llama-nemotron-colembed-vl-3b-v2` | **Runs** dummy PNG, shape `[1, 3072]`. | `2026-08-16_055802Z` rev `9907f8fd…` |
| A7b | ColEmbed VL 4B v2 | `nvidia/nemotron-colembed-vl-4b-v2` | **Runs** after `process_documents`. Shape `[1, 2560]`. | `2026-08-16_061905Z` rev `0ed152d9…` |
| A7c | ColEmbed VL 8B v2 | `nvidia/nemotron-colembed-vl-8b-v2` | **Runs** after `process_documents`. | `2026-08-16_061921Z` rev `34b64061…` |
| A8 | Omni embed 3B | `nvidia/omni-embed-nemotron-3b` | **Runs** dummy image. Not Nano Omni LM. | `2026-08-16_061940Z` rev `865db1bb…` |
| A9 | Parse 2.0 | `nvidia/NVIDIA-Nemotron-Parse-2.0` | **Runs** dummy PNG generate. Not OCR eval. | `2026-08-16_063558Z` rev `635b84d9…` |
| A10 | ASR 3.5 0.6B | `nvidia/nemotron-3.5-asr-streaming-0.6b` | **Runs** Transformers ASR pipeline. Tone → empty text. First “BLOCKED” was librosa. | `2026-08-16_060037Z` rev `1c8deaec…` |
| A11 | Content Safety 3.5 | `nvidia/Nemotron-3.5-Content-Safety` | **Runs** `User Safety: safe` shape. Gemma-3. | `2026-08-16_055324Z` rev `35645ed3…` |
| A12 | Safety Guard 8B v3 | `nvidia/Llama-3.1-Nemotron-Safety-Guard-8B-v3` | **Runs**. First prompt was chat (“Paris”), not a Guard schema. | `2026-08-16_055356Z` rev `8fdc246b…` |

## B — 30B BF16, extra stack risk

| # | Product | HF ID | ~Weights | Runtime hint | Caveat |
| --- | --- | --- | --- | --- | --- |
| B1 | 3.5 Lightning 30B BF16 | `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16` | **Validated** greedy 5/5. Not Nano. No FlashInfer. | `2026-08-16_062756Z` rev `d468880b…` |
| B2 | Nano Omni 30B BF16 | `nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16` | **FAIL** RADIO resolution after FA2/Tee workarounds | `063955Z` (earlier FA2 `062426Z`) |

## C — FP8 (FNUZ research)

MI300X FP8 is **FNUZ**. NVIDIA checkpoints are typically **OCP**. Load may fail or be silently wrong. Record outputs even if they look plausible — do not call that Validated without a BF16 cross-check on the same prompts.

| # | Product | HF ID | ~Weights | Caveat |
| --- | --- | --- | --- | --- |
| C1 | Nano 30B FP8 | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8` | ~30 GB | **FAIL** `mamba-ssm` (`062923Z`). **R-FNUZ**. Do not install CUDA mamba-ssm. |
| C2 | Omni Reasoning FP8 | `nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-FP8` | ~33 GB listed | **FAIL** `mamba-ssm` (`063016Z`). **R-FNUZ**. |
| C3 | Super 120B FP8 | `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-FP8` | ~120 GB / 112 GiB | **FAIL** `mamba-ssm` (`063022Z`). Fit **1×** unchanged. **R-FNUZ**. |
| C4 | Lightning FP8 | — | — | **No official HF ID** in the 2026-08-16 org census. Skip. Not NVFP4. |

NVFP4 remains **out of this queue**. Super BF16 / Ultra were not downloaded (do not fit 1× VF).

## D — remaining 1×-fit Transformers (2026-08-16 afternoon)

| # | Product | HF ID | Outcome | Evidence |
| --- | --- | --- | --- | --- |
| D1 | Nano 4B FP8 | `nvidia/NVIDIA-Nemotron-3-Nano-4B-FP8` | **Runs** tokens, **not Validated**. All five prompts were looping `A`. **R-FNUZ**. | `2026-08-16_170427Z` rev `3fe6dab7…` |
| D2 | VL embed 1B v2 FP8 | `nvidia/llama-nemotron-embed-vl-1b-v2-fp8` | **FAIL** `create_bidirectional_mask` / `inputs_embeds`. **R-FNUZ**. | `2026-08-16_170519Z` |
| D3 | VL rerank 1B v2 FP8 | `nvidia/llama-nemotron-rerank-vl-1b-v2-fp8` | **FAIL** ranking (relevant < irrelevant). Loaded. **R-FNUZ**. | `2026-08-16_170557Z` |

## E — vLLM for already-Validated 1× BF16

| # | Product | Outcome | Evidence |
| --- | --- | --- | --- |
| E1 | Nano 4B BF16 | **Runs** OpenAI API `max-model-len=8192`. Not Validated for vLLM. TF remains Validated. | `2026-08-16_170637Z` |
| E2 | Lightning 30B BF16 | **Runs** OpenAI API `max-model-len=8192`. Not Nano. Not FlashInfer. TF remains Validated. | `2026-08-16_170852Z` |

---

## Still not queued on this 1× VF

| Checkpoint | Why |
| --- | --- |
| Super 120B **BF16** | Fit **2×**. Do not download. |
| Ultra 550B any precision | BF16 **8×**; NVFP4 **2×** + **R-NVFP4**. |
| Any NVFP4 | NVIDIA format, not AMD-native. |
| Nano 30B BF16 repeat | Already Validated / Runs. |

---

## Pass bar for a queued row

Same as [`methodology.md`](methodology.md): `run-metadata.json`, env snapshot, command, JSON generations **or** classified FAIL, review note, matrix cell update. New timestamped dir only.
