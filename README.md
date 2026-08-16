# Nemotron on AMD

Evidence-based technical validation: which NVIDIA Nemotron models can run on AMD Instinct, Radeon, and Ryzen AI hardware, through which software stacks, at which precision, with what caveats.

This repository does **not** assume that a model is supported because it is open source, because a CUDA cookbook exists, or because the weights appear to fit in memory.

## Status (2026-08-16)

Nemotron 3 Nano 30B BF16 **loaded, generated, and served** on 1× Instinct MI300X VF. Transformers greedy thinking-off smoke is **Validated** on the pinned snapshot. vLLM serving, characterization, and 128K ladder remain **Runs** / **PASS WITH CAVEATS**. Official Nano 4B GGUF is **Validated** on this Strix Point laptop (CPU and Vulkan iGPU) and on MI300X HIP. Not Optimized or Production-ready. Discrete Radeon remains untested. Ryzen AI **NPU** remains untested.

| Model | Checkpoint | Platform | Runtime | Status |
| --- | --- | --- | --- | --- |
| Nemotron 3 Nano 30B-A3B | BF16 | Instinct MI300X VF (1 GPU) | Transformers / ROCm PyTorch | **PASS WITH CAVEATS** / **Validated** — greedy smoke, thinking off, pinned revision (`results/mi300x/2026-08-16_031205Z/`); first FAIL preserved (`172557Z`); thinking on/off probes (`024048Z`) |
| Nemotron 3 Nano 30B-A3B | BF16 | Instinct MI300X VF (1 GPU) | vLLM (ROCm Docker) | **PASS WITH CAVEATS** / **Runs** — OpenAI API, thinking off/on, `max-model-len=8192` (`results/mi300x/2026-08-15_223840Z/`) |
| Nemotron 3 Nano 30B-A3B | BF16 | Instinct MI300X VF (1 GPU) | vLLM engineering characterization | **PASS WITH CAVEATS** — memory + conc 1/2/4, **not a benchmark** (`results/mi300x/2026-08-16_022238Z/`) |
| Nemotron 3 Nano 30B-A3B | BF16 | Instinct MI300X VF (1 GPU) | vLLM context ladder | **PASS WITH CAVEATS** — needle/haystack 4K→128K; **not** 256K/1M (`results/mi300x/2026-08-16_024220Z/`) |
| Nemotron 3 Nano 30B-A3B | FP8 | Instinct MI300X | Transformers | **FAIL** `mamba-ssm` import (`062923Z`). **R-FNUZ**. Do not install CUDA mamba-ssm |
| Nemotron 3.5 Lightning 30B-A3B | BF16 | Instinct MI300X VF (1 GPU) | Transformers | **Validated** greedy thinking-off (`results/mi300x/2026-08-16_062756Z/`). Not Nano. No FlashInfer |
| Nemotron 3.5 Lightning 30B-A3B | BF16 | Instinct MI300X VF (1 GPU) | vLLM (ROCm Docker) | **Runs** OpenAI API `max-model-len=8192` (`results/mi300x/2026-08-16_170852Z/`). Not Validated for vLLM |
| Nemotron 3 Super 120B-A12B | BF16 | Instinct MI300X | any | Fit **2×**; this lab is **1×** VF so **not** downloaded. **NOT TESTED** |
| Nemotron 3 Super 120B-A12B | FP8 | 1× MI300X | Transformers | **FAIL** `mamba-ssm` import (`063022Z`). Fit **1×** still. **R-FNUZ**. Not a PASS |
| Nemotron 3 Ultra 550B-A55B | BF16 | Instinct MI300X | any | Fit **8×**; this lab is **1×** VF so not downloaded. **NOT TESTED** |
| Nemotron 3 Ultra 550B-A55B | NVFP4 | Instinct MI300X | any | Fit **2×** plus NVIDIA-specific format. **NOT TESTED** — not in queue |
| Nemotron 3 Nano Omni | BF16 | MI300X | Transformers | **FAIL** after FA2/Tee workarounds: RADIO vision `min_resolution_step` (`063955Z`). FP8 **FAIL** `mamba-ssm` |
| Nemotron 3 Nano 4B | BF16 | Instinct MI300X VF (1 GPU) | Transformers | **Validated** greedy thinking-off (`results/mi300x/2026-08-16_054423Z/`). Not Nano 30B |
| Nemotron 3 Nano 4B | BF16 | Instinct MI300X VF (1 GPU) | vLLM (ROCm Docker) | **Runs** OpenAI API `max-model-len=8192` (`results/mi300x/2026-08-16_170637Z/`). Not Validated for vLLM |
| Nemotron 3 Nano 4B | FP8 | Instinct MI300X VF | Transformers | **Runs** looping `A` (`170427Z`). **R-FNUZ**. Not Validated |
| Embed 1B / 8B | BF16 | Instinct MI300X VF | Transformers SDPA | **Runs** cosine sanity (`054857Z`, `055129Z`). Not a retrieval benchmark |
| llama-nemotron-rerank-1b-v2 | BF16 | Instinct MI300X VF | Transformers | **Runs** text pair (`055206Z`) |
| VL embed / ColEmbed / omni-embed 3B / Parse 2.0 | BF16 | Instinct MI300X VF | Transformers + ROCm torchvision 0.27 | **Runs** dummy image / parse (`055802Z`, `061905Z`, `061921Z`, `061940Z`, `062402Z`, `063558Z`) |
| llama-nemotron-rerank-vl-1b-v2 | BF16 | Instinct MI300X VF | Transformers | **Runs** **text** path only (`055737Z`). Images not ranked |
| llama-nemotron-embed-vl-1b-v2-fp8 / rerank-vl FP8 | FP8 | Instinct MI300X VF | Transformers | **FAIL** (`170519Z` mask API; `170557Z` ranking). **R-FNUZ** |
| ASR Streaming 3.5 0.6B | default | Instinct MI300X VF | Transformers pipeline | **Runs** (`060037Z`). Synthetic tone → empty transcript. First librosa miss preserved |
| Content Safety 3.5 | BF16 | Instinct MI300X VF | Transformers Gemma-3 | **Runs** label shape (`055324Z`). Not a red-team |
| Safety Guard 8B v3 | BF16 | Instinct MI300X VF | Transformers Llama 3.1 | **Runs** (`055356Z`). First prompt behaved like chat, not a Guard schema |
| Any Nemotron model | any | Radeon discrete | any | **NOT TESTED** |
| Nemotron 3 Nano 4B | official GGUF Q4_K_M | Instinct MI300X VF (1 GPU) | llama.cpp HIP gfx942 (b10453 source) | **Validated** greedy thinking-off (`results/mi300x/2026-08-16_215228Z/`). 43/43 layers on ROCm0 |
| Nemotron 3 Nano 4B | official GGUF Q4_K_M | Ryzen AI laptop CPU | llama.cpp b10453 | **Validated** greedy thinking-off (`results/ryzen-ai/2026-08-16_214142Z/`) |
| Nemotron 3 Nano 4B | official GGUF Q4_K_M | Ryzen AI iGPU (RADV GFX1150 Vulkan UMA) | llama.cpp b10453 | **Validated** 43/43 layers on Vulkan0 (`results/ryzen-ai/2026-08-16_214348Z/`). Not NPU. Not HIP. |
| Nemotron 3.5 Lightning 30B-A3B | ggml-org GGUF Q4_0 | Instinct MI300X VF (1 GPU) | llama.cpp HIP gfx942 (b10453 source) | **Validated** greedy thinking-off (`results/mi300x/2026-08-16_225542Z/`). 53/53 layers on ROCm0 |
| Nemotron 3.5 Lightning 30B-A3B | ggml-org GGUF Q4_0 | Ryzen AI laptop CPU | llama.cpp b10453 | **Validated** greedy thinking-off (`results/ryzen-ai/2026-08-16_223932Z/`) |
| Nemotron 3.5 Lightning 30B-A3B | ggml-org GGUF Q4_0 | Ryzen AI iGPU (RADV GFX1150 Vulkan UMA) | llama.cpp b10453 | **Validated** 53/53 layers on Vulkan0 (`results/ryzen-ai/2026-08-16_224120Z/`). Not NPU. Not HIP. |
| Nemotron 3 Nano 30B-A3B | Unsloth GGUF Q4_K_M (community) | Instinct MI300X VF (1 GPU) | llama.cpp HIP gfx942 (b10453 source) | **Validated** greedy thinking-off (`results/mi300x/2026-08-16_231304Z/`). 53/53 layers on ROCm0. Not official NVIDIA 30B GGUF |
| Nemotron 3 Nano 30B-A3B | Unsloth GGUF Q4_K_M (community) | Ryzen AI laptop CPU | llama.cpp b10453 | **Validated** greedy thinking-off (`results/ryzen-ai/2026-08-16_225528Z/`). Not official NVIDIA 30B GGUF |
| Nemotron 3 Nano 30B-A3B | Unsloth GGUF Q4_K_M (community) | Ryzen AI iGPU (RADV GFX1150 Vulkan UMA) | llama.cpp b10453 | **Validated** 53/53 layers on Vulkan0 (`results/ryzen-ai/2026-08-16_225631Z/`). Not NPU. Not HIP |
| Any Nemotron model | any | Ryzen AI NPU (XDNA) | any | **NOT TESTED** — no Nemotron NPU path identified |

Do not read **THEORETICALLY FEASIBLE** as **PASS**.

## Purpose

Answer, with recorded evidence:

> Which NVIDIA Nemotron models can run on AMD Instinct, Radeon, and Ryzen AI hardware, through which software stack, with what precision, memory requirements, performance characteristics, and caveats?

The first hands-on target is:

```text
Nemotron 3 Nano 30B-A3B
BF16
AMD Instinct MI300X
1 GPU
```

The first goal is **not** performance optimization. The first goal is:

```text
MODEL LOADS → MODEL GENERATES → OUTPUT IS REASONABLE → SERVER WORKS → RESULTS ARE REPRODUCIBLE
```

## Runs / Validated / Optimized / Production-ready

These words are not interchangeable. Definitions: [`docs/terminology.md`](docs/terminology.md).

| Term | Meaning in this repo |
| --- | --- |
| **Runs** | The model loaded on the stated AMD device and produced tokens through the stated runtime. Output was captured. Failures and caveats are recorded. |
| **Validated** | Repeated, reproducible Runs with environment snapshot, prompts, logs, and a written review that the output is reasonable for the smoke-test set. |
| **Optimized** | A Validated configuration **plus** evidence of AMD-relevant performance work (kernels, quantization that actually executes, serving flags) compared against a baseline. |
| **Production-ready** | Optimized **plus** operational evidence: reliability, tool calling, long context as claimed, license/compliance notes, and a supportable operator recipe. We are not here yet. |

A CUDA cookbook, a Hugging Face model card, or a memory estimate cannot by itself produce any of these labels.

## Scope

- **Models:** Full NVIDIA Nemotron brand catalog: [`docs/nemotron-family.md`](docs/nemotron-family.md). Next 1× MI300X queue: [`docs/mi300x-next-tests.md`](docs/mi300x-next-tests.md). Hands-on on this VF: Nano/Lightning **Validated**; family embed/tools **Runs**; Omni BF16 and Nano/Omni/Super FP8 **FAIL**. Nano 30B is the only **vLLM** result.
- **Hardware:** Instinct MI300X (execute), MI325X / MI350X / MI355X / MI350P (theoretical until we have hardware), Radeon workstation/consumer GPUs that AMD currently lists as ROCm-supported, and this Strix Point Ryzen AI laptop. Fit vs test vs “not supported” is in [`docs/compatibility-matrix.md`](docs/compatibility-matrix.md).
- **Software:** ROCm, HIP-enabled PyTorch, Transformers, vLLM (ROCm), llama.cpp where relevant. TensorRT-LLM, NIM, and NVFP4 kernels are treated as NVIDIA-specific unless an AMD path is demonstrated.
- **Out of scope for phase 1:** 1M-context runs, Super **BF16** and Ultra downloads, NVFP4 on AMD, NPU claims, production SLAs. Super **FP8** is queued as FNUZ research only.

Project charter: [`docs/project-scope.md`](docs/project-scope.md). Methodology: [`docs/methodology.md`](docs/methodology.md).

## Platforms

| Platform | Role now |
| --- | --- |
| **Instinct MI300X (1× 192 GB HBM)** | Primary validation machine. Transformers greedy smoke **Validated** (`031205Z`); thinking probes **Runs** (`024048Z`); vLLM serve/characterization/128K ladder **Runs**. Nano 4B, Lightning Q4_0, and Unsloth Nano 30B Q4_K_M llama.cpp HIP **Validated**. Not Optimized. |
| **Instinct MI325X / MI350X / MI355X / MI350P** | Spec-based fit only. **NOT YET VALIDATED**. MI350P is 144 GB PCIe CDNA4; Super BF16 does not fit. |
| **Radeon** | Compatibility research from current AMD ROCm docs. **NOT TESTED**. No discrete card in lab. 30B BF16 **NOT PRACTICAL** on 16–48 GB. |
| **Ryzen AI Strix Point** | Local laptop. Official Nano 4B, Lightning Q4_0, and Unsloth Nano 30B Q4_K_M GGUF **Validated** on **CPU** and **iGPU** Vulkan UMA. Dedicated 512 MB still **doesn't fit**. NPU **NOT TESTED**. |

## Models (current official IDs)

Checked against NVIDIA Hugging Face model cards on **2026-08-15**. Sources: [`docs/sources.md`](docs/sources.md).

| Family | Hugging Face ID (primary) | Params | First AMD hypothesis |
| --- | --- | --- | --- |
| Nano | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` | 30B total / 3.5B active | BF16 Transformers greedy smoke **Validated** on 1× MI300X VF; vLLM **Runs** through 128K needle/haystack; not Optimized; not 1M |
| Nano 4B | `nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16` | ~3.97B | More plausible later on Radeon / Ryzen AI than 30B BF16. Official GGUF: `nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF` |
| Super | `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16` | 120B / 12B | BF16 Fit **2×** MI300X / **1×** MI350X; **doesn't fit** MI350P / Radeon / Ryzen AI |
| Ultra | `nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16` | 550B / 55B | BF16 Fit **8×** MI300X / **4× tight** MI350X; **doesn't fit** PCIe or laptop |
| Nano Omni | `nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16` | ~31B / ~3B | Unvalidated; multimodal stack adds risk |
| Lightning 3.5 | `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16` | 30B / 3B | Queued B1 on 1× MI300X. Do not copy FlashInfer. No official FP8 ID |
| Embed 1B | `nvidia/Nemotron-3-Embed-1B-BF16` | ~1.14B | Later local candidate |

## How validation works

1. Record the machine (`scripts/*/collect-env.sh`). Never overwrite previous `results/` trees.
2. Use an isolated venv. Do not modify system Python or system ROCm.
3. Install **ROCm** PyTorch, never CUDA wheels.
4. Run Transformers smoke tests with deterministic prompts.
5. Only then serve with ROCm vLLM and hit the OpenAI-compatible API.
6. Only then characterize memory and engineering performance.
7. A **PASS** in [`docs/compatibility-matrix.md`](docs/compatibility-matrix.md) must link to a `results/...` artifact.

Failures are first-class results. Preserve the original log, classify the likely layer, then investigate. See [`docs/troubleshooting.md`](docs/troubleshooting.md).

## How to run the MI300X test

These commands are for the **MI300X host**, which this laptop is not. Replace placeholders. Do not commit tokens.

```bash
# On your workstation: copy this repo to the MI300X host over SSH.
# Host/user are operator-specific. This repo never invents them.
scp -r . <MI300X_USER>@<MI300X_HOST>:~/Nemotron-on-AMD

ssh <MI300X_USER>@<MI300X_HOST>
cd ~/Nemotron-on-AMD

# 1) Discover the actual software stack (required before any install)
bash scripts/mi300x/collect-env.sh

# 2) Create an isolated venv and inspect ROCm (installs nothing)
bash scripts/mi300x/setup-python-env.sh

# 3) Only after reviewing the collected ROCm version, install ROCm PyTorch + Transformers
bash scripts/mi300x/setup-python-env.sh --install
source .venv-mi300x/bin/activate

# 4) Optional: if the Nano card is gated, export a token in the shell only
# export HF_TOKEN=<HF_TOKEN>

# 5) Transformers smoke test (first actual validation)
RUN_ID="$(date -u +%Y-%m-%d_%H%M%S)Z"
python scripts/mi300x/transformers-smoke-test.py \
  --model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
  --output-dir "results/mi300x/${RUN_ID}"

# 6) Transformers smoke succeeded 2026-08-15 (PASS WITH CAVEATS).
# 7) vLLM serve succeeded 2026-08-15 via AMD ROCm 7.14 CDNA Docker (PASS WITH CAVEATS).
# Host Python 3.12 has no AMD 7.14 vLLM wheel (image is Python 3.14). Do not copy NVIDIA FlashInfer/NVFP4 flags.
# bash scripts/mi300x/launch-vllm.sh --docker \
#   --model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
#   --output-dir "results/mi300x/${RUN_ID}/vllm"
```

Exact next-step commands are also in [`docs/project-status.md`](docs/project-status.md). Copy the `results/mi300x/<timestamp>/` tree back into this repo after the run.

## How to contribute results

1. Run the scripts; do not hand-edit numbers into the matrix.
2. Store JSON, logs, the command, and `run-metadata.json` under a **new** timestamped directory.
3. Link the evidence path in the compatibility matrix.
4. Use only the status vocabulary in [`docs/terminology.md`](docs/terminology.md).
5. Never commit `.env`, tokens, SSH keys, or model weight files.

## Repository layout

```text
docs/           methodology, inventory, matrix, caveats
platforms/      Instinct / Radeon / Ryzen AI notes
models/         per-model cards as used in this project
scripts/        discovery, setup, Transformers, vLLM, benchmark
prompts/        deterministic smoke / reasoning / tool tests
results/        timestamped evidence (never overwrite)
reports/        executive, engineering/BD, evidence ledger
```

## Reports

- [`reports/executive-report.md`](reports/executive-report.md) — plain-language brief (no kernel jargon)
- [`reports/engineering-bd-report.md`](reports/engineering-bd-report.md) — technical validation: stacks, versions, memory, characterization, 128K ladder, caveats
- [`reports/evidence-summary.md`](reports/evidence-summary.md) — claim → `results/` path ledger

Those reports now include a **Validated** Transformers greedy smoke and vLLM **Runs** through 128K. They still do **not** claim Optimized, Production-ready, or AMD product support.

## License notes

Model weights are NVIDIA-licensed (Nemotron Open Model License or OpenMDW, depending on the repo). This engineering repository does not relicense those weights. See [`LICENSE-NOTES.md`](LICENSE-NOTES.md).
