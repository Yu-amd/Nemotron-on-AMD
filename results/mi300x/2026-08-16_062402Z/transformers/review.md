# Review: llama-nemotron-embed-vl-1b-v2 (retry3 PASS)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=PASS`)  
**Claim allowed after this review:** **Runs** for load + forward on `nvidia/llama-nemotron-embed-vl-1b-v2`, revision `582e3bf72aee355e3c59ed89de53543c5b0657ee`, Transformers 5.15.0, torch `2.12.0+rocm7.14.0`, 1× MI300X VF, `process_documents` dummy PNG.  
**Not claimed:** Validated retrieval, a usable embedding vector, Optimized.

`CausalLMOutputWithPast` had **no** embedding tensor (`embedding_shape=[]`). Weights loaded (~3.2 GiB reserved). That is a forward completion, not a cosine sanity like Embed 1B.

Preserve earlier FAILs: missing torchvision (`055228Z`), PIL zip (`055715Z`), harness IndexError (`061846Z`).
