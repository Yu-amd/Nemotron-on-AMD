# Nemotron on AMD

For executives and customers who do not need kernel-level detail.  
Date: **16 August 2026**. This is an evidence report, **not** a product announcement.

## The one-page answer

**Can Nemotron run on AMD today?** Several NVIDIA Nemotron products **did run** on AMD hardware in this lab. That is **not** the same as “Nemotron supports AMD” or a finished product.

On a **single Instinct MI300X** (~192 GB GPU memory) we:

- **Validated** high-precision (BF16) generation for **Nano 30B**, **Nano 4B**, and **Lightning 30B** against a fixed quiz, using a pinned copy of each model’s weights.
- Stood up an OpenAI-style local server for those same three BF16 checkpoints. The server **works**. We call that **Runs**, not Validated serving and not Optimized. Only **Nano 30B** was pushed through a 128K “find the secrets in the filler text” test.
- **Failed** Nano Omni 30B (vision/reasoning) in BF16, and **failed** the NVIDIA 8-bit (FP8) checkpoints for Nano 30B, Omni 30B, and Super 120B. Those failures are recorded; they are not “unsupported until we try harder” marketing.
- **Ran** a set of smaller Nemotron tools on the same GPU: embeddings, rerankers, parse, speech, and safety models. Those loaded and produced output. They are **Runs**, not retrieval or safety benchmarks.

On a **Ryzen AI laptop** (CPU + laptop graphics) and again on the **MI300X**, three **GGUF** (compressed) files answered the same quiz: official **Nano 4B**, community **Nano 30B** (Unsloth, not NVIDIA’s official 30B GGUF), and **Lightning** Q4_0. Dedicated laptop graphics memory (512 MB) is too small; unified memory (Vulkan) did hold them. The laptop **NPU was not used**. No discrete **Radeon** card was in the lab.

**Do not say “Nemotron supports AMD.”** Say the sentence at the bottom of this note.

## What we tested, in plain words

| Question | Answer |
| --- | --- |
| Does a Nemotron language model load on Instinct MI300X? | **Yes** for Nano 30B, Nano 4B, and Lightning 30B in BF16 (~59 GB GPU memory for the 30B weights). |
| Does it produce reasonable answers? | **Yes** on a small, fixed quiz, repeated with pinned weights, for those three BF16 models. That is **Validated** for the quiz, not for every customer task. |
| Can an application talk to it like ChatGPT’s API? | **Yes**, on this MI300X, with AMD’s ROCm vLLM container, for Nano 30B, Nano 4B, and Lightning 30B at 8K context. Only Nano 30B was characterized further. |
| Do compressed GGUF files run? | **Yes** — official Nano 4B, Lightning Q4_0, and community Unsloth Nano 30B — on MI300X and on a Ryzen AI laptop (CPU and laptop graphics via Vulkan). Not the NPU. Not an official NVIDIA 30B GGUF. |
| Is it fast / production-ready? | **Not claimed.** Informal speed numbers are engineering notes, not a benchmark. NVIDIA-class AMD kernels for this architecture are still missing. |
| Does the advertised 1 million token context work? | **Not tested.** We proved a filler “find the secrets at the start and end” test through **128 thousand** tokens, **Nano 30B BF16 only**. We did **not** try 256K or 1M. |
| Do bigger Nemotron models (Super, Ultra) fit this GPU? | Super BF16 needs **2×** MI300X; Ultra BF16 needs **8×**. This lab has **one** GPU, so we did not download them. Super **FP8** fits one GPU but **failed** to import (`mamba-ssm`). |
| Did every Nemotron we tried succeed? | **No.** Omni 30B BF16 **failed** (vision pipeline). Nano 30B / Omni / Super **FP8 failed**. Nano 4B FP8 produced looping nonsense (not Validated). Two vision-embed FP8 files failed. |
| Discrete Radeon? | **Not tested.** No discrete Radeon was in the lab. |
| Ryzen AI NPU? | **Not tested.** Seeing the NPU in the OS is not “Nemotron on the NPU.” |

## Status words (do not mix these)

| Word | What it means here |
| --- | --- |
| **Runs** | It loaded and produced tokens. We saved the log. That is all. |
| **Validated** | We repeated a recorded test and judged the answers reasonable. Still not “fast” or “supported.” |
| **Optimized** | Validated **plus** AMD performance work with a before/after measurement. **We are not here.** |
| **Production-ready** | Optimized **plus** operations, reliability, and a recipe someone else can run. **We are not here.** |

## Which Nemotron models, which AMD boxes

Hands-on hardware is **Instinct MI300X** and a **Strix Point Ryzen AI laptop**. Other Instinct SKUs, discrete Radeon, and the laptop NPU are fit/status on paper until we run them. Full grid: [`../docs/compatibility-matrix.md`](../docs/compatibility-matrix.md).

Blank Model cells continue the product above. GGUF is another checkpoint of the same Nano / Lightning SKU, not a different product.

| Model | Checkpoint | Instinct MI300X (192 GB) | Ryzen AI laptop | Discrete Radeon (16–48 GB) | Other Instinct (MI325X / MI350X / MI355X / MI350P) |
| --- | --- | --- | --- | --- | --- |
| Nano 30B-A3B | BF16 | Answers **Validated**, vLLM **Runs** through 128K (Fit **1×**). Not Optimized. | **Doesn't fit** | **Doesn't fit** | Fit **1×**; **not tested** |
| | FP8 | **FAIL** | Weights fit CPU RAM; **not tested** | Likely fits larger cards; **not tested** | Fit **1×**; **not tested** |
| | GGUF (Unsloth, community) | llama.cpp HIP **Validated** | CPU + Vulkan **Validated**; dedicated 512 MB **doesn't fit**; NPU **not tested** | Likely fits 24 GB+; **not tested** | Fit **1×**; **not tested** |
| Nano 4B | BF16 | Transformers **Validated**, vLLM **Runs** at 8K | **Not tested** (BF16) | Fit **1×**; **not tested** | Fit **1×**; **not tested** |
| | FP8 | **Runs** looping `A` — not Validated | **Not tested** | **Not tested** | **Not tested** |
| | GGUF (official NVIDIA) | llama.cpp HIP **Validated** | CPU + Vulkan **Validated**; dedicated 512 MB **doesn't fit**; NPU **not tested** | Fit **1×**; **not tested** | Fit **1×**; **not tested** |
| Lightning 30B-A3B | BF16 | Transformers **Validated**, vLLM **Runs** at 8K (not the 128K ladder) | **Doesn't fit** | **Doesn't fit** | Fit **1×**; **not tested** |
| | GGUF Q4_0 (ggml-org) | llama.cpp HIP **Validated** | CPU + Vulkan **Validated**; dedicated 512 MB **doesn't fit**; NPU **not tested** | Likely fits 24 GB+; **not tested** | Fit **1×**; **not tested** |
| Super 120B | BF16 | Fit **2×**, not downloaded, **not tested** | **Doesn't fit** | **Doesn't fit** | Fit **1×** (tight on MI325X); **not tested**. **Doesn't fit** MI350P. |
| | FP8 | **FAIL** (`mamba-ssm`). Fit **1×**. | **Doesn't fit** | **Doesn't fit** | Fit **1×**; **not tested** |
| Ultra 550B | BF16 / NVFP4 | Fit **8×** / **2×**. Not downloaded. **Not tested** | **Doesn't fit** | **Doesn't fit** | BF16 Fit **4× tight** on MI350X/MI355X; **doesn't fit** MI350P. **Not tested** |
| Nano Omni 30B | BF16 / FP8 | BF16 **FAIL** (vision). FP8 **FAIL** | **Doesn't fit** (BF16) | **Doesn't fit** (BF16) | Fit **1×**; **not tested** |
| Embed 1B / 8B | BF16 | **Runs** (cosine smoke; not a retrieval benchmark) | **Not tested** | **Not tested** | **Not tested** |
| Rerank / VL embed / ColEmbed / omni-embed / Parse | BF16 | **Runs** (text or dummy image). VL rerank is **text** only | **Not tested** | **Not tested** | **Not tested** |
| VL embed / VL rerank | FP8 | **FAIL** | **Not tested** | **Not tested** | **Not tested** |
| ASR 3.5 0.6B | default | **Runs**. A test tone produced an empty transcript | **Not tested** | **Not tested** | **Not tested** |
| Content Safety 3.5 / Guard 8B v3 | BF16 | **Runs**. Not a red-team. Guard did not apply a Guard schema | **Not tested** | **Not tested** | **Not tested** |

NVIDIA’s 4-bit **NVFP4** files were **not downloaded**. They are not an AMD checkbox.

## Five things to remember

1. **Open weights ≠ AMD product.** NVIDIA publishes the files. NVIDIA also ships CUDA/NIM/TensorRT serving recipes. Those recipes are not AMD recipes.
2. **NVIDIA’s 4-bit format (NVFP4) is not an AMD checkbox.** Do not present it as portable. A GGUF file is a different 4-bit path.
3. **One GPU is not the whole Instinct line.** Super and Ultra need many NVIDIA GPUs even in NVIDIA’s own tables. They do not become single-MI300X products by wishing.
4. **Ryzen AI is three computers:** CPU, laptop graphics, and an NPU. GGUF on CPU and Vulkan is **not** “Nemotron on the NPU.”
5. **Informal speed numbers are easy to misuse.** If someone quotes tokens per second, they must also say the GPU, software, checkpoint, date, and test. This report does not publish a product speed.

## What AMD / partners can safely say

> We validated that NVIDIA Nemotron 3 Nano 30B, Nano 4B, and Nemotron 3.5 Lightning 30B (BF16) answer a recorded test set on one AMD Instinct MI300X. Those same weights can be served on that GPU through AMD’s ROCm software. Official Nano 4B GGUF, Lightning Q4_0, and a community Nano 30B GGUF also passed that test on MI300X and on a Ryzen AI laptop (CPU and laptop graphics). Several smaller Nemotron embed, parse, speech, and safety models loaded on MI300X. Nano Omni and several NVIDIA FP8 checkpoints failed. This is a first engineering result, not a supported product, not an official benchmark, and not proof that Super, Ultra, discrete Radeon, or the Ryzen AI NPU work.

What to avoid: “Nemotron supports AMD,” “production-ready on Instinct,” “runs on Ryzen AI NPU,” “1 million context on AMD,” “as fast as NVIDIA,” “official NVIDIA 30B GGUF.”

## What is still open

- Treating any **server** path as Validated (needs a recorded repeat of the API tests)
- 256K / 1M context; Nano 4B / Lightning context ladders
- Super BF16 and Ultra on multi-GPU Instinct; any **NVFP4** path on AMD
- Lightning Q8_0 / BF16 GGUF; Omni GGUF
- Any **discrete Radeon** model run; any **NPU** path
- Performance work that would earn **Optimized**

The technical companion is [`engineering-bd-report.md`](engineering-bd-report.md). The evidence ledger is [`evidence-summary.md`](evidence-summary.md).
