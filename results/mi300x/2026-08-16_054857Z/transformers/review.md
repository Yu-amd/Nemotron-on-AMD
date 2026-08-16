# Review: Nemotron 3 Embed 1B BF16

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=PASS`)  
**Claim allowed after this review:** **Runs** for Embed 1B BF16, revision `9e0b24858b1195815ecb1188ffa1b73bcea7b30a`, Transformers 5.15.0, torch `2.12.0+rocm7.14.0`, 1× MI300X VF, SDPA, mean-pool cosine sanity.  
**Not claimed:** Validated as a retrieval benchmark, NVFP4, Nano LM, sentence-transformers serving, Radeon, Ryzen AI.

This is an encoder (`Ministral3Model`), not a hybrid Nemotron LM.

## What ran

Two MI300X-related sentences vs a banana sentence. Cosine paraphrase **0.6808** > unrelated **0.4270**. That is a load+forward sanity check, not MTEB.

`rope_parameters` yarn key `apply_yarn_scaling` was unrecognized by Transformers 5.15.0 (warning only).

## Caveats

- FlashAttention-2 was not used (`attn_implementation=sdpa`).
- Informal, not a benchmark.
- Do not cite as Nano 30B evidence.

Logs: `logs/family-smoke.log`.
