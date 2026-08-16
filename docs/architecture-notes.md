# Architecture notes

Nemotron 3 is not “just another Llama.” AMD bring-up has to track **which** hybrid pieces the runtime implements.

## Nano 30B-A3B (first target)

Official HF card (2026-08-15):

- 23 Mamba-2 **and** MoE layers, plus **6** grouped-query attention layers
- Each MoE: 128 routed experts + 1 shared; **6** experts activated per token
- 30B total / **3.5B** active
- Reasoning on/off via chat template `enable_thinking`
- Context up to 1M (config default 256k)

Implications for AMD:

- Need a Mamba-2 / SSM cache implementation in Transformers **and** in vLLM on ROCm
- Need sparse MoE routing, not dense 30B matmuls
- Attention is a small fraction of layers; correctness of those few GQA layers still matters
- Active-parameter FLOPs ≠ weight memory. You still store all experts.

## Nano 4B

Hybrid **Mamba-2 + MLP + 4 attention**, **no MoE**, distilled/pruned from Nemotron Nano 9B v2. Fewer moving parts than 30B-A3B, but still not a vanilla Transformer. Better later candidate for Radeon / Ryzen AI if HIP/Vulkan kernels exist.

## Super / Ultra

Additional pieces **not** in Nano:

- **LatentMoE** (tokens projected to a smaller latent dim for expert compute)
- **Multi-Token Prediction (MTP)** (speculative decoding / extra heads)
- **NVFP4-aware pretraining** (weights may still be published in BF16, but recipes and kernels assume NVIDIA precisions)

NVIDIA Super vLLM BF16 recipe uses TP=8 on H100 and TP=2 on B200. Ultra BF16 uses 8×B200-class memory.

Instinct takeaway: Super/Ultra are multi-GPU problems on current MI300X, **plus** extra kernel surface beyond Nano.

## Nano Omni

Same hybrid-MoE class plus **video / audio / image** towers. ROCm risk is the multimodal preprocessing stack, not only the LLM backbone. Do not treat Omni BF16 as a drop-in Nano text run.

## Lightning 3.5

Same 30B hybrid MoE size class as Nano, with **3B** active (vs Nano 3.5B) and published speculative-decoding paths. NVIDIA BF16 vLLM example uses `--mamba-backend flashinfer`. Treat as a **separate** architecture/serving problem. Do not copy Nano results onto Lightning.

## Embed / safety

Embed models are **bidirectional encoders** (Ministral-derived), not Nemotron hybrid MoE LMs. Content Safety Reasoning 4B is **Gemma-3-4B**. Safety Guard v3 is **Llama 3.1 8B**. Compatibility conclusions for Nano **must not** be copied onto Embed/safety, or vice versa.

## Chat templates

Do not assume Llama-3 or ChatML. Use the tokenizer `chat_template` from the checkpoint. Record `enable_thinking` behavior as a first-class test (`prompts/reasoning-tests.json`).

NVIDIA vLLM parsers:

| Model | Reasoning parser | Tool parser |
| --- | --- | --- |
| Nano | `nano_v3` (+ `nano_v3_reasoning_parser.py` plugin) | `qwen3_coder` |
| Super | `nemotron_v3` (vLLM) / `nemotron_3` (SGLang) | `qwen3_coder` |
| Ultra | `nemotron_v3` | `qwen3_coder` |
| Lightning 3.5 | **Unknown / requires validation** (NVIDIA BF16 snippet uses FlashInfer Mamba, not `nano_v3`) | **Unknown / requires validation** |

Whether ROCm vLLM ships these parsers is **Unknown / requires validation**.
