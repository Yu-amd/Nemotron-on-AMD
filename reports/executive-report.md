# Nemotron on AMD

For executives and customers who do not need kernel-level detail.  
Date: **16 August 2026**. This is an evidence report, **not** a product announcement.

## The one-page answer

**Can Nemotron run on AMD today?** One model can, on one kind of AMD GPU, in a limited way.

We took NVIDIA’s **Nemotron 3 Nano 30B** (the BF16 checkpoint — the ordinary high-precision weights) and ran it on a **single AMD Instinct MI300X** with about **192 GB** of GPU memory. It loaded, it answered a fixed set of test questions correctly, and we repeated that test against a pinned copy of the weights. In this project’s language that is **Validated** for “does it generate sensible answers,” not “is this a supported AMD product.”

We also stood up a local serving stack (an OpenAI-style API used by many apps). That server **works**. It is **not** yet as mature as NVIDIA’s own serving path. We call that **Runs**, not Validated serving and not Optimized.

**Do not say “Nemotron supports AMD.”** Say the sentence at the bottom of this note.

## What we tested, in plain words

| Question | Answer |
| --- | --- |
| Does the model load on this AMD GPU? | **Yes.** About 59 GB of GPU memory for the weights. |
| Does it produce reasonable answers? | **Yes**, on a small, fixed quiz (math, code, JSON, short writing). Repeated with a recorded weight snapshot. |
| Can an application talk to it like ChatGPT’s API? | **Yes**, on this machine, with AMD’s ROCm vLLM container. |
| Is it fast / production-ready? | **Not claimed.** We collected informal speed and memory numbers. They are engineering notes, not a benchmark. NVIDIA-class AMD kernels for this architecture are still missing. |
| Does the advertised 1 million token context work? | **Not tested.** We proved a filler “find the secrets at the start and end” test through **128 thousand** tokens. We did **not** try 256K or 1M. |
| Do bigger Nemotron models (Super, Ultra) fit this GPU? | Super BF16 needs **2×** MI300X; Ultra BF16 needs **8×**. This lab has **one** GPU, so we did not download them. |
| Does it run on this Ryzen AI laptop or on Radeon cards? | **Not tested.** The laptop is too small for this 30B BF16 model. No discrete Radeon was in the lab. |

## Status words (do not mix these)

| Word | What it means here |
| --- | --- |
| **Runs** | It loaded and produced tokens. We saved the log. That is all. |
| **Validated** | We repeated a recorded test and judged the answers reasonable. Still not “fast” or “supported.” |
| **Optimized** | Validated **plus** AMD performance work with a before/after measurement. **We are not here.** |
| **Production-ready** | Optimized **plus** operations, reliability, and a recipe someone else can run. **We are not here.** |

## Which Nemotron models, which AMD boxes

Hands-on work is **one MI300X**. Other Instinct SKUs, discrete Radeon, and this Ryzen AI laptop are fit/status on paper until we run them. Full grid: [`../docs/compatibility-matrix.md`](../docs/compatibility-matrix.md).

| Model | 1× MI300X (192 GB) | 1× MI325X (256 GB) | 1× MI350X / MI355X (288 GB) | 1× MI350P (144 GB) | Radeon (16–48 GB) | Ryzen AI laptop |
| --- | --- | --- | --- | --- | --- | --- |
| Nano 30B-A3B | BF16 answers **Validated**, vLLM **Runs** (Fit **1×**). Community Unsloth GGUF llama.cpp HIP **Validated**. FP8 **FAIL**. | Fit **1×**; **not tested** | Fit **1×**; **not tested** | Fit **1×**; **not tested** | BF16 **doesn't fit**; GGUF likely fits 24 GB+; **not tested** | BF16 **doesn't fit**. Unsloth GGUF CPU + Vulkan UMA **Validated**; dedicated 512 MB **doesn't fit**; NPU **not tested** |
| Nano 4B | BF16 Transformers **Validated**, vLLM **Runs**. Official GGUF llama.cpp HIP **Validated**. FP8 **Runs** (looping, not Validated). | Fit **1×**; **not tested** | Fit **1×**; **not tested** | Fit **1×**; **not tested** | Fit **1×**; **not tested** | GGUF CPU + Vulkan UMA **Validated**; dedicated 512 MB **doesn't fit**; NPU **not tested** |
| Lightning 30B-A3B | BF16 Transformers **Validated**, vLLM **Runs**. ggml-org GGUF llama.cpp HIP **Validated**. | Fit **1×**; **not tested** | Fit **1×**; **not tested** | Fit **1×**; **not tested** | BF16 **doesn't fit**; GGUF likely fits 24 GB+; **not tested** | BF16 **doesn't fit**. GGUF CPU + Vulkan UMA **Validated**; dedicated 512 MB **doesn't fit**; NPU **not tested** |
| Super 120B | BF16 Fit **2×**, not downloaded. FP8 Fit **1×**, Transformers **FAIL** `mamba-ssm`. | Fit **1×** (BF16 leftover tight); **not tested** | Fit **1×**; **not tested** | BF16 **doesn't fit**; FP8 leftover tight, never tried | **Doesn't fit** | **Doesn't fit** |
| Ultra 550B | BF16 Fit **8×**; NVFP4 Fit **2×**. Not downloaded. | Same story; **not tested** | BF16 Fit **4×** leftover tight; **not tested** | **Doesn't fit** | **Doesn't fit** | **Doesn't fit** |
| Other (Omni, Embed, parse, ASR, safety) | Mixed (see engineering report) | Not tested | Not tested | Not tested | Not tested | Not tested |

## Five things to remember

1. **Open weights ≠ AMD product.** NVIDIA publishes the files. NVIDIA also ships CUDA/NIM/TensorRT serving recipes. Those recipes are not AMD recipes.
2. **NVIDIA’s 4-bit format (NVFP4) is not an AMD checkbox.** Do not present it as portable.
3. **One GPU is not the whole Instinct line.** Super and Ultra need many NVIDIA GPUs even in NVIDIA’s own tables. They do not become single-MI300X products by wishing.
4. **Ryzen AI is three computers:** CPU, laptop graphics, and an NPU. Seeing the NPU in the OS is **not** “Nemotron on the NPU.”
5. **Informal speed numbers are easy to misuse.** If someone quotes tokens per second, they must also say the GPU, software, checkpoint, date, and test. This report does not publish a product speed.

## What AMD / partners can safely say

> We validated that NVIDIA Nemotron 3 Nano 30B (BF16) answers a recorded test set on one AMD Instinct MI300X. The same weights can be served on that GPU through AMD’s ROCm software. That is a first engineering result, not a supported product, not an official benchmark, and not proof that larger Nemotron models or laptops work.

What to avoid: “Nemotron supports AMD,” “production-ready on Instinct,” “runs on Ryzen AI NPU,” “1 million context on AMD,” “as fast as NVIDIA.”

## What is still open

- Treating the **server** path as Validated (needs a recorded repeat of the API tests)
- 256K / 1M context, other Nemotron sizes, NVIDIA 8-bit/4-bit formats on AMD
- Any **discrete Radeon** model run; any **NPU** path
- Performance work that would earn **Optimized**

The technical companion is [`engineering-bd-report.md`](engineering-bd-report.md). The evidence ledger is [`evidence-summary.md`](evidence-summary.md).
