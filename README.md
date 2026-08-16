# Nemotron on AMD

Evidence-based technical validation: which NVIDIA Nemotron models can run on AMD Instinct, Radeon, and Ryzen AI hardware, through which software stacks, at which precision, with what caveats.

This repository does **not** assume that a model is supported because it is open source, because a CUDA cookbook exists, or because the weights appear to fit in memory.

## Status (2026-08-16)

Nemotron 3 Nano 30B BF16 **loaded, generated, and served** on 1× Instinct MI300X VF. Transformers greedy thinking-off smoke is **Validated** on the pinned snapshot. vLLM serving, characterization, and 128K ladder remain **Runs** / **PASS WITH CAVEATS**. Official Nano 4B GGUF is **Validated** on a Strix Point Ryzen AI laptop (CPU and Vulkan iGPU) and on MI300X HIP. Not Optimized or Production-ready. Discrete Radeon remains untested. Ryzen AI **NPU** remains untested.

Rows are **products**, not extra models. Blank Model cells continue the product above. GGUF is another checkpoint of the same Nano / Lightning SKU.

| Model | Checkpoint | Where / stack | Status |
| --- | --- | --- | --- |
| Nano 30B-A3B | BF16 | 1× MI300X Transformers | **Validated** greedy thinking-off (`031205Z`); first FAIL kept (`172557Z`); thinking on/off **Runs** (`024048Z`) |
| | BF16 | 1× MI300X vLLM | **Runs** OpenAI serve (`223840Z`); characterization conc 1/2/4 (`022238Z`); 128K needle/haystack (`024220Z`). Not 256K/1M. Not Optimized |
| | FP8 | 1× MI300X Transformers | **FAIL** `mamba-ssm` (`062923Z`). **R-FNUZ** |
| | GGUF Q4_K_M (Unsloth, community) | llama.cpp: MI300X HIP + Ryzen AI laptop CPU + iGPU Vulkan UMA | **Validated** on all three (`231304Z`, `225528Z`, `225631Z`). Not official NVIDIA 30B GGUF. Dedicated 512 MB **doesn't fit**. NPU **NOT TESTED** |
| Nano 4B | BF16 | 1× MI300X Transformers / vLLM | Transformers **Validated** (`054423Z`); vLLM **Runs** `8192` (`170637Z`) |
| | FP8 | 1× MI300X Transformers | **Runs** looping `A` (`170427Z`). **R-FNUZ**. Not Validated |
| | GGUF Q4_K_M (official) | llama.cpp: MI300X HIP + Ryzen AI laptop CPU + iGPU Vulkan UMA | **Validated** on all three (`215228Z`, `214142Z`, `214348Z`). Dedicated 512 MB **doesn't fit**. NPU **NOT TESTED** |
| Lightning 30B-A3B | BF16 | 1× MI300X Transformers / vLLM | Transformers **Validated** (`062756Z`); vLLM **Runs** `8192` (`170852Z`). No FlashInfer |
| | GGUF Q4_0 (ggml-org) | llama.cpp: MI300X HIP + Ryzen AI laptop CPU + iGPU Vulkan UMA | **Validated** on all three (`225542Z`, `223932Z`, `224120Z`). Dedicated 512 MB **doesn't fit**. NPU **NOT TESTED** |
| Super 120B-A12B | BF16 | 1× MI300X | Fit **2×**; lab is 1× VF — **not downloaded**. **NOT TESTED** |
| | FP8 | 1× MI300X Transformers | **FAIL** `mamba-ssm` (`063022Z`). Fit **1×**. **R-FNUZ**. Not a PASS |
| Ultra 550B-A55B | BF16 | 1× MI300X | Fit **8×** — **not downloaded**. **NOT TESTED** |
| | NVFP4 | 1× MI300X | Fit **2×** plus NVIDIA-specific format. **NOT TESTED** |
| Nano Omni 30B | BF16 / FP8 | 1× MI300X Transformers | BF16 **FAIL** RADIO `min_resolution_step` (`063955Z`). FP8 **FAIL** `mamba-ssm` |
| Embed 1B / 8B | BF16 | 1× MI300X Transformers | **Runs** cosine (`054857Z`, `055129Z`). Not a retrieval benchmark |
| Rerank / VL embed / ColEmbed / omni-embed / Parse 2.0 | BF16 | 1× MI300X Transformers | **Runs** text or dummy image (`055206Z`, `055737Z`, `055802Z`, `061905Z`, `061921Z`, `061940Z`, `062402Z`, `063558Z`). VL rerank is **text** only |
| | FP8 (VL embed / VL rerank) | 1× MI300X Transformers | **FAIL** (`170519Z` mask API; `170557Z` ranking). **R-FNUZ** |
| ASR 3.5 0.6B | default | 1× MI300X Transformers | **Runs** (`060037Z`). Tone → empty transcript |
| Content Safety 3.5 / Guard 8B v3 | BF16 | 1× MI300X Transformers | **Runs** (`055324Z`, `055356Z`). Not a red-team; Guard did not apply a Guard schema |

Discrete **Radeon**: every Nemotron SKU **NOT TESTED**. Ryzen AI **NPU**: **NOT TESTED** (no path identified).

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
- **Hardware:** Instinct MI300X (execute), MI325X / MI350X / MI355X / MI350P (theoretical until hardware is available), Radeon workstation/consumer GPUs that AMD currently lists as ROCm-supported, and a Strix Point Ryzen AI laptop. Fit vs test vs “not supported” is in [`docs/compatibility-matrix.md`](docs/compatibility-matrix.md).
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

These commands are for the **MI300X host**, not a Ryzen AI laptop. Replace placeholders. Do not commit tokens.

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
canvases/       Cursor visual matrix (`compatibility-matrix.canvas.tsx`)
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
