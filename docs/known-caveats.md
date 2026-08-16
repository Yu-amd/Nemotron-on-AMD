# Known caveats

Dated entries from tests go at the bottom. A Transformers **Runs** result is not a vLLM result; a vLLM **Runs** result is not Optimized.

## Product / language caveats

- NVIDIA model cards list **NVIDIA GPUs** under software integration. That is not an AMD incompatibility proof, but it is also not AMD support.
- “Open weights” ≠ “portable optimized runtime.”
- Super/Ultra BF16 **fitting on B200** does not transfer automatically to MI300X even at the same 192 GB, because kernels and precision differ.

## Precision

- **NVFP4 is NVIDIA-specific** until demonstrated otherwise. MI350 MXFP4 is not NVFP4.
- **MI300X FP8 is FNUZ**; NVIDIA FP8 checkpoints are typically OCP. Loading FP8 Nemotron on MI300X is a research item, not a recipe.
- Casting BF16 → FP16 locally is not an “AMD optimization.”

## Memory

- Calculator numbers omit KV cache, Mamba/SSM state, MoE routing tables, CUDA/HIP graphs, and fragmentation.
- Super BF16 ~240 GB needs **2×** MI300X → **do not download** to the current 1× MI300X host.
- Ultra BF16 ~1.1 TB needs **8×** MI300X; NVFP4 payload ~275 GB needs **2×** → **do not download** to 1× MI300X.
- This Strix Point laptop reports **512 MB** dedicated VRAM in `amd-smi` and ~47 GiB in a rocminfo GPU pool, with **VRAM% already 90%** at idle. Treat iGPU free memory as **Unknown / requires validation**. Do not load Nano 30B BF16 here.

## Software

- Official Nano Transformers path wants **Transformers ≥ 5.3.0**.
- Official vLLM Nano path wants **vLLM ≥ 0.12.0** on NVIDIA, a **custom reasoning parser file**, `qwen3_coder`, and `--trust-remote-code`.
- Nano Omni NVIDIA pin: **vLLM 0.20.0**.
- Lightning NVIDIA BF16 pin: `vllm/vllm-openai:v0.27.1` plus `--mamba-backend flashinfer`.
- Super NVIDIA pin: **vLLM 0.18.1**. Ultra NVIDIA container: **v0.22.0**. ROCm wheels may not match those exact CUDA versions.
- Default `pip install vllm` is CUDA. Use `vllm/vllm-openai-rocm` or https://wheels.vllm.ai/rocm/ (checked 2026-08-15). AMD `rocm/vllm` images are **deprecated** per vLLM docs.
- SGLang NVIDIA Nano example sets `--attention-backend flashinfer` — CUDA-oriented.
- Embed examples default to **FlashAttention-2**.

## Local laptop

- CPU, Radeon 890M iGPU, and XDNA NPU are **three targets**.
- `rocminfo` shows GPU `gfx1150` **and** DSP `aie2`. ROCm GPU success ≠ NPU success.
- User is already in `video` and `render` groups; `/dev/kfd`, `/dev/dri`, `/dev/accel/accel0` exist.
- Host Python 3.12.12 currently has **no torch / transformers / vllm**. That is acceptable; we are not installing large stacks locally in this phase.

## Process

- Never mark README or the matrix **PASS** without `results/` evidence.
- Never upgrade OS/ROCm/kernel to “make it work” without stopping and documenting a blocker.

## MI300X (2026-08-15)

- The execution node is a **KVM/QEMU guest with an SR-IOV MI300X VF**, not a proven equivalent of a full OAM card.
- `/opt/rocm/.info/version` is **7.0.2**; HIP / amd-smi / torch report **7.14**. Wheel selection must follow HIP, not the wrapper file.
- Transformers **5.15.0** `apply_chat_template(..., return_tensors="pt")` returned a `BatchEncoding`, not a Tensor. First Nano smoke **FAIL**: `results/mi300x/2026-08-15_172557Z/` (layer: TOKENIZER/harness). Load had already succeeded (~58.9 GiB).
- After one harness unwrap, greedy thinking-off smoke **PASS** 5/5: `results/mi300x/2026-08-15_172810Z/`. That first PASS left `model_revision` unset (**Runs**).
- Pinned reproduction **PASS** 5/5: `results/mi300x/2026-08-16_031205Z/`. Revision `2d59de1cbd51c0adf384eb906b766d1aee0e0517`. **Validated** for Transformers greedy thinking-off on this VF stack only.
- Cached `config.json`: `model_type=nemotron_h`, `auto_map` present (`configuration_nemotron_h.py` / `modeling_nemotron_h.py`). The modeling `.py` is **not** in the snapshot; Transformers 5.15.0 loaded without `trust_remote_code`. `max_position_embeddings=262144`.
- HF snapshot on the node is `refs/main` = that same hash. Unauthenticated Hub download still worked for the original cache fill.
- vLLM OpenAI serve **PASS WITH CAVEATS** (`2026-08-15_223840Z`): AMD CDNA Docker Python 3.14 / torch 2.11.0+rocm7.14.0, vLLM 0.23.1.dev1, `max-model-len=8192`. Host Python 3.12 had no matching AMD 7.14 wheel. Default fused-MoE and Mamba SSU configs missing for `AMD_Instinct_MI300X`; ROCm custom paged attention fell back to Triton. Thinking-on returned a populated reasoning field. Not Optimized; do not quote engine tok/s.
- Fused-MoE autotune sanity run **FAIL** (`2026-08-16_020625Z`): `benchmark_moe.py --tune` for Nano on this VF, ~2h17m. Completed `batch_size=8` and three config-count passes (608 / 1.22k / 2.78k). Ray `ActorDiedError` at ~99% of a 4.48k pass. No JSON written. Docker `OOMKilled=false`. No GPU reset in dmesg during this window. Layer: **KERNEL**. Do not copy NVIDIA H100/B200 MoE JSON as a substitute.
- Engineering characterization (`2026-08-16_022238Z`): pinned revision `2d59de1cbd51c0adf384eb906b766d1aee0e0517`, same Docker image. Weights 58.91 GiB; idle VRAM after load ~154.7 GiB at `gpu-memory-utilization=0.80`; short generate barely moves used VRAM because KV is pre-reserved. Streaming conc 1/2/4 all 100% success on a ~42+61 token greedy factorial prompt. Same missing MoE/Mamba configs and Triton paged-attn fallback. **Not a benchmark. Not Optimized.** Immediate `docker rm` VRAM snapshot was still ~144 GiB; a later host check returned to 0.279 GiB baseline.
- Transformers thinking probes **PASS** (`2026-08-16_024048Z`): same pinned revision, `prompts/reasoning-tests.json`, 5/5. Thinking-on prefills `<think>` in the template and leaves `</think>` in decoded text (no `nano_v3` split). Thinking-off math has no `</think>` and still answers 1536. Does not by itself earn **Validated** for the earlier smoke set.
- vLLM context ladder **PASS WITH CAVEATS** (`2026-08-16_024220Z`): serve restarted at 16K/32K/64K/128K. Needle/haystack (HEAD indigo / TAIL 4172) passed at ~4K/8K/16K/32K/64K/128K prompt tokens, thinking off, greedy. 128K prompt_tokens=127916, e2e ~19.2 s. **Not** 256K or 1M. Same missing MoE/Mamba configs. Not a document-QA benchmark. Not Optimized.

## MI300X family queue (2026-08-16)

- Isolated venv extras (do **not** install CUDA torchvision): `requests`, `librosa`, `soundfile`, `datasets==3.6.0`, `timm==1.0.15 --no-deps` (pip resolver RecursionError otherwise), `einops`, `open-clip-torch --no-deps`. ROCm `torchvision==0.27.0+rocm7.14.0` from `https://repo.amd.com/rocm/whl-multi-arch/` `--no-deps`. torchvision **0.28.0+rocm7.14.0** imported with `operator torchvision::nms does not exist` against torch 2.12.0.
- Embed Yarn warning: unrecognized `apply_yarn_scaling` on Transformers 5.15.0 (warning only).
- VL processors: lone PIL Image is not iterable (`zip(images, text)`). Qwen3/Omni need `process_documents` / chat template or `tokens: 0, features: 4`.
- ASR first `BLOCKED` (`055308Z`) was missing `librosa`; harness matched `"nemo"` inside `NemotronAsr…`. Not a CUDA/NeMo proof.
- First FAILs kept; retries use new timestamps. Overnight remainder: A5/A9 then Lightning/Omni BF16 then FP8.
