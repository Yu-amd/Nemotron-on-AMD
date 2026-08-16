# Model inventory

Checked **2026-08-15** against NVIDIA Hugging Face model cards and related NVIDIA pages. Fields that could not be confirmed are marked **Unknown / requires validation**. This inventory is **not** AMD validation evidence.

This file is the **phase-1 card-level** set (Nano / Super / Ultra / Omni / Lightning / Embed / two safety models). The **whole Nemotron brand**, including Parse, ASR, Labs, Llama Nemotron, Nemotron 4, and 183 NVIDIA-org HF IDs, is [`nemotron-family.md`](nemotron-family.md).

Raw weight estimates use `scripts/common/estimate_weight_memory.py` (params × bytes/param; excludes KV cache, activations, overhead, scales). Decimal GB = params × bytes / 1e9. GiB = params × bytes / 1024³.

---

## Nemotron 3 Nano 30B-A3B

| Field | Value | Source |
| --- | --- | --- |
| Exact HF repo (BF16, **first AMD target**) | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16` | HF card |
| Other official checkpoints | `...-FP8`, `...-NVFP4` | HF |
| Family | Nemotron 3 Nano | HF |
| Architecture | Hybrid MoE: 23 Mamba-2 + MoE layers and 6 attention (GQA) layers; 128 routed experts + 1 shared; 6 experts/token | HF |
| Total parameters | 30B | HF |
| Active parameters | 3.5B | HF |
| BF16 availability | Yes (official) | HF |
| FP8 availability | Yes (official PTQ/quantized sibling) | HF |
| NVFP4 availability | Yes (official quantized sibling) | HF |
| GGUF availability | **No official NVIDIA 30B GGUF repo found.** Community: `unsloth/Nemotron-3-Nano-30B-A3B-GGUF`. NVIDIA DGX Spark playbook uses that Unsloth file. Official GGUF **does** exist for Nano **4B**. | HF / NVIDIA Spark playbook |
| Context length | Up to 1M tokens; HF config default 256k due to VRAM | HF |
| Transformers support | Integrated since Transformers **v5.3.0**. Official snippet does **not** set `trust_remote_code`. | HF |
| vLLM support | NVIDIA recipe: `vllm>=0.12.0`, `--trust-remote-code`, `--tool-call-parser qwen3_coder`, `--reasoning-parser nano_v3` plus `nano_v3_reasoning_parser.py` plugin | HF / vLLM recipes |
| SGLang support | NVIDIA snippet uses `--attention-backend flashinfer` and `--reasoning-parser nano_v3`. FlashInfer is CUDA-oriented. AMD SGLang: **Unknown / requires validation** | HF |
| llama.cpp support | Claimed as an engine on NVFP4 card; practical path shown by NVIDIA is CUDA llama.cpp + Unsloth GGUF. AMD: community Unsloth Q4_K_M **Validated** on llama.cpp CPU, Vulkan (laptop), and HIP gfx942 (MI300X). Still **no official NVIDIA 30B GGUF**. | HF / Spark playbook / this repo |
| License | NVIDIA Nemotron Open Model License | HF |
| Estimated raw weight memory | BF16 ~60 GB / 55.9 GiB; FP8 ~30 GB / 27.9 GiB; INT4/NVFP4 payload ~15 GB / 14.0 GiB | calculator |
| Custom code | Official Transformers example uses native `AutoModelForCausalLM`. vLLM still passes `--trust-remote-code`. **Requires validation** on ROCm whether remote code is needed. | HF |
| Chat template | `tokenizer.apply_chat_template(..., enable_thinking=True/False)`. Default thinking on. | HF |
| Reasoning mode | Configurable. Reasoning-on: temp 1.0, top_p 1.0. Reasoning-off: greedy in Transformers snippet. | HF |
| Tool calling | vLLM `--enable-auto-tool-choice --tool-call-parser qwen3_coder`. Tool-calling sampling 0.6 / 0.95. | HF |
| Known CUDA/NVIDIA-specific deps | Listed HW: H100-80GB, A100. TRT-LLM cookbook. NIM. FlashInfer appears in other-family recipes. NVFP4 sibling uses `VLLM_USE_FLASHINFER_MOE_FP4`. Runtime engine cited: NeMo 25.11.01. | HF |
| Release date | 2025-12-15 | HF |
| AMD status in this repo | Transformers greedy thinking-off **Validated** on pinned snapshot `2d59de1…` (`031205Z`). Thinking on/off and ROCm vLLM through 128K **Runs**. **PASS WITH CAVEATS**. Unsloth community Q4_K_M GGUF llama.cpp **Validated** on CPU/Vulkan/HIP (`225528Z`, `225631Z`, `231304Z`). Not Optimized. Not 256K/1M. Not official NVIDIA 30B GGUF | `results/mi300x/2026-08-16_031205Z/`; `results/mi300x/2026-08-16_231304Z/` |

---

## Nemotron 3 Nano 4B

| Field | Value | Source |
| --- | --- | --- |
| Exact HF repo (BF16) | `nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16` | HF |
| Other checkpoints | FP8 sibling exists (`NVIDIA-Nemotron-3-Nano-4B-FP8` per vLLM recipe). Official GGUF: `nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF`. NVFP4: **Unknown / requires validation** | HF / vLLM recipe |
| Family | Nemotron 3 Nano (edge SLM) | HF |
| Architecture | Hybrid Mamba-2 + MLP + 4 attention layers. **Not MoE.** Compressed from `nvidia/NVIDIA-Nemotron-Nano-9B-v2` via Nemotron Elastic. ~42 layers. | HF |
| Total / active parameters | ~3.97B (dense hybrid) | HF |
| Context length | RULER 128k reported; vLLM examples use `--max-model-len 262144`. 1M: **Unknown / requires validation** | HF / vLLM |
| Transformers / vLLM | vLLM recipe uses same `nano_v3` parser plugin pattern; `--mamba_ssm_cache_dtype float32` | HF |
| llama.cpp | Official NVIDIA GGUF repo `nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF`. AMD HIP/Vulkan execution: **Unknown / requires validation** | HF |
| License | NVIDIA Nemotron Open Model License | HF |
| Estimated raw weight memory | BF16 ~7.9 GB / 7.4 GiB; FP8 ~4.0 GB / 3.7 GiB; Q4 payload ~2.0 GB / 1.9 GiB | calculator |
| Release date | 2026-03-16 | HF |
| AMD status | **NOT TESTED**. Later local/Radeon candidate. |

---

## Nemotron 3 Super 120B-A12B

| Field | Value | Source |
| --- | --- | --- |
| Exact HF repo (BF16) | `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16` | HF |
| Other official checkpoints | FP8, NVFP4, Base BF16 (lab page) | HF / NVIDIA lab |
| Family | Nemotron 3 Super | HF |
| Architecture | **LatentMoE** hybrid: Mamba-2 + MoE + attention + **MTP**. Pretrained with NVFP4 recipe. Distinct from Nano. | HF |
| Total / active | 120B / 12B | HF |
| Context | Up to 1M | HF |
| Transformers | **Unknown / requires validation** as the practical AMD first path; NVIDIA quickstart emphasizes vLLM/SGLang/TRT-LLM | HF |
| vLLM | NVIDIA cookbook `vllm==0.18.1`; `--reasoning-parser nemotron_v3`; `--tool-call-parser qwen3_coder`; BF16 `--tensor-parallel-size 8` on H100, **2** on B200 | HF |
| SGLang | NVIDIA snippet `--tp 8 --ep 8 --reasoning-parser nemotron_3` | HF |
| llama.cpp / GGUF | **Unknown / requires validation** for official NVIDIA GGUF. Do not assume a GGUF exists just because Nano has a community conversion. | — |
| License | NVIDIA Nemotron Open Model License | HF |
| Min GPU (NVIDIA card) | BF16: **8× H100-80GB**; B200/B300 BF16: **2 GPUs**. FP8: **2× H100-80GB** | HF |
| Estimated raw weight memory | BF16 ~240 GB / 223.5 GiB; FP8 ~120 GB / 111.8 GiB; 4-bit payload ~60 GB / 55.9 GiB | calculator |
| OAM Instinct (192 GB) | BF16 Fit **2×**; FP8 Fit **1×** (~72 GB leftover) **NOT TESTED** (FNUZ risk); NVFP4 Fit **1×** but **R-NVFP4**. **Doesn't fit** MI350P / Radeon / Ryzen AI in BF16. | calc + AMD FP8 notes |
| Custom code | `super_v3_reasoning_parser.py` for serving | HF |
| Reasoning / tools | `enable_thinking`; Super sampling recipe: temp 1.0, top_p 0.95 for all tasks | HF |
| NVIDIA-specific | NVFP4 pretraining; TRT-LLM; NIM; `--max-cudagraph-capture-size`; FlashInfer in Ultra siblings | HF |
| Release date | 2026-03-11 | HF |
| AMD status | Feasibility only. **Do not download BF16 for 1× MI300X.** |

---

## Nemotron 3 Ultra 550B-A55B

| Field | Value | Source |
| --- | --- | --- |
| Exact HF repo (BF16) | `nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16` | HF |
| Other official checkpoints | NVFP4; Base BF16; GenRM (lab page) | HF / NVIDIA lab |
| Architecture | LatentMoE + Mamba-2 + attention + MTP; NVFP4 pretraining recipe | HF |
| Total / active | 550B / 55B | HF |
| Context | Up to 1M | HF |
| License | **OpenMDW License Agreement v1.1** (not the Nano/Super Nemotron Open Model License) | HF |
| Min GPU (NVIDIA card) | BF16: 8× GB200/B200/GB300/B300, **16× H100**, or 8× H200. NVFP4: 4× GB200/B200/GB300/B300 or 8× H100 | HF |
| vLLM | NVIDIA recommends `vllm/vllm-openai:v0.22.0`, `--mamba-backend flashinfer`, MTP speculative config, TP=8 | HF |
| Estimated raw weight memory | BF16 ~1100 GB / 1024 GiB; FP8 ~550 GB / 512 GiB; 4-bit payload ~275 GB / 256 GiB | calculator |
| OAM Instinct | BF16 Fit **8×** MI300X/MI325X, **4× tight** MI350X. FP8 (~550 GB) Fit **4×** MI300X. NVFP4 payload Fit **2×**. **Doesn't fit** one MI350P / Radeon / Ryzen AI. | calc |
| Release date | 2026-06-04 | HF |
| AMD status | Feasibility only. **Do not download** on the current single-GPU host. |

---

## Nemotron 3 Nano Omni

| Field | Value | Source |
| --- | --- | --- |
| Exact HF repos | `nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16`, `-FP8`, `-NVFP4` | HF Omni card |
| Family | Nemotron 3 Nano Omni (multimodal) | HF |
| Architecture | Hybrid Mamba2-Transformer MoE (text backbone similar class to Nano) plus video/audio/image | HF |
| Total / active | 31B / ~3B (card). **Slightly different from text Nano 30B/3.5B — do not conflate checkpoints.** | HF |
| Modalities | In: video, audio, image, text. Out: text | HF |
| Context | 256k listed on NVFP4 card (not 1M) | HF |
| Disk / listed sizes | BF16 62 GB, FP8 33 GB, NVFP4 21 GB | HF |
| vLLM | `--reasoning-parser nano_v3`, `--tool-call-parser qwen3_coder`, video kwargs; `--kv-cache-dtype fp8` for non-BF16 | HF |
| llama.cpp / Ollama | Listed as engines. AMD: **Unknown / requires validation** | HF |
| License | NVIDIA Open Model Agreement (distinct from Nano text-model Nemotron Open Model License) | Omni BF16 README |
| Release | 2026-04-28 | HF |
| AMD status | **NOT TESTED**. Multimodal extras are additional ROCm risk. |

---

## Nemotron Embed

### Nemotron-3-Embed-1B-BF16

| Field | Value | Source |
| --- | --- | --- |
| HF ID | `nvidia/Nemotron-3-Embed-1B-BF16` | HF |
| Architecture | Transformer **encoder**, bidirectional; pruned from Ministral-3-3B-Instruct-2512 | HF |
| Parameters | ~1.14B | HF |
| Embedding dim | 2048 (Matryoshka-style slicing mentioned) | HF |
| Context | 32768 | HF |
| BF16 / NVFP4 | BF16 official. NVFP4 official: `nvidia/Nemotron-3-Embed-1B-NVFP4` (ModelOpt 0.45.0). NVFP4 is NVIDIA-specific until proven on AMD. | HF |
| Transformers | `>=5.2.0` plus `sentence-transformers>=5.4.1`. NVIDIA examples default to `flash_attention_2` (often CUDA). Fallback: SDPA. | HF |
| vLLM | Card discusses vLLM online serving. ROCm: **Unknown / requires validation** | HF |
| License | OpenMDW 1.1; additional Apache-2.0 parent note | HF |
| Estimated BF16 weights | ~2.3 GB / 2.1 GiB | calculator |
| NVIDIA-specific | CUDA PyTorch examples; tested in `nvcr.io/nvidia/pytorch:26.06-py3` | HF |
| AMD status | **NOT TESTED**. Best **later** local candidate. |

### Nemotron-3-Embed-8B-BF16

| Field | Value | Source |
| --- | --- | --- |
| HF ID | `nvidia/Nemotron-3-Embed-8B-BF16` | HF |
| Architecture | Ministral-3-8B-Instruct-2512 based encoder | HF |
| Parameters | ~8B | HF |
| Embedding dim | 4096 | HF |
| Estimated BF16 weights | ~16 GB / 14.9 GiB | calculator |
| AMD status | **NOT TESTED** |

Older retrieval models exist (`nvidia/llama-embed-nemotron-8b`, `nvidia/llama-nemotron-embed-1b-v2`). They are Nemotron-branded but not Nemotron 3 hybrid MoE LMs. Treat separately.

---

## Safety / guard

### Nemotron-Content-Safety-Reasoning-4B (current Nemotron 3-class safety model)

| Field | Value | Source |
| --- | --- | --- |
| HF ID | `nvidia/Nemotron-Content-Safety-Reasoning-4B` | HF |
| Architecture | Gemma-3-4B-it finetuned classifier with reasoning traces. **Not** Mamba-MoE. | HF |
| Parameters | 4B | HF |
| Estimated BF16 weights | ~8 GB / 7.5 GiB | calculator (4e9 × 2) |
| AMD status | **NOT TESTED**. Later local candidate. Architecturally Gemma-3, not Nemotron hybrid LM. |

### Llama 3.1 Nemotron Safety Guard 8B v3

| Field | Value | Source |
| --- | --- | --- |
| HF ID | `nvidia/Llama-3.1-Nemotron-Safety-Guard-8B-v3` | HF |
| Architecture | Llama 3.1 8B Instruct + LoRA safety post-training. **Not** Mamba-MoE. | HF |
| Languages | Trained 9; claimed zero-shot >20 | HF |
| Estimated BF16 weights | ~16 GB / 14.9 GiB | calculator |
| AMD status | **NOT TESTED**. Architecturally closer to generic Llama-3.1 on ROCm than Nano. Still requires evidence. |

Do not treat a safety-model result as Nano evidence.

---

## Nemotron 3.5 Lightning 30B-A3B

Not in the original minimum list; added because NVIDIA's developer page (checked 2026-08-15) lists it as a current Nemotron model. **Not the first AMD target.**

| Field | Value | Source |
| --- | --- | --- |
| Exact HF repo (BF16) | `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16` | HF |
| Other official checkpoints | `...-NVFP4`; DFlash / DSpark speculative NVFP4 helpers | HF |
| Family | Nemotron 3.5 Lightning | HF |
| Architecture | Hybrid Mamba-2 + MoE + attention; speculative decoding (MTP / DFlash / DSpark) | HF |
| Total / active | 30B / **3B** (not Nano's 3.5B) | HF |
| Context | Up to 1M; NVIDIA single-H100 note 256K | HF |
| BF16 / NVFP4 | Both official | HF |
| GGUF | Card points to NVFP4 Local AI section. Exact official GGUF ID: **Unknown / requires validation** | HF |
| Transformers | **Unknown / requires validation** as the AMD-first path. NVIDIA BF16 card emphasizes vLLM customization/reference weights | HF |
| vLLM | NVIDIA BF16 snippet: `vllm/vllm-openai:v0.27.1` with `--mamba-backend flashinfer`. **Do not copy FlashInfer to ROCm.** ROCm: **Unknown / requires validation** | HF |
| License | OpenMDW 1.1 | HF |
| Estimated raw weight memory | BF16 ~60 GB / 55.9 GiB (same class as Nano 30B) | calculator |
| NVIDIA-specific | NVFP4 inference positioning; FlashInfer Mamba; DSpark/DFlash | HF |
| Release date | 2026-08-11 | HF |
| AMD status | **NOT TESTED**. Memory class similar to Nano; serving recipe is more NVIDIA-optimized. Do not reuse Nano results as Lightning evidence. |

---

## Inventory gaps (do not guess)

- Exact Nano 30B on-disk snapshot size and commit hash: need `huggingface_hub` download metadata from a real pull.
- Whether Transformers 5.3+ on ROCm can load Nano **without** `trust_remote_code`.
- Whether ROCm vLLM implements `nano_v3` / `nemotron_v3` parsers and Mamba-MoE kernels for gfx942.
- Official NVIDIA Super/Ultra/Lightning GGUF IDs: Lightning card alludes to Local AI GGUF; exact repo not confirmed in this pass.
- Whether Nano 4B `custom_code` tag means `trust_remote_code=True` is required (HF tags include `custom_code`; 30B official Transformers snippet does not).
- Brand-wide IDs (Parse, ASR, Labs, Llama Nemotron, Nemotron 4): listed in [`nemotron-family.md`](nemotron-family.md) from the NVIDIA org API; most cards were **not** opened in the 2026-08-15 pass. No `Nemotron-3-Rerank-*` ID found; text rerank is `llama-nemotron-rerank-1b-v2`.
