# Review: Nemotron 3 Embed 8B BF16

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=PASS`)  
**Claim allowed after this review:** **Runs** for Embed 8B BF16, revision `c44c20ab3f6b430336706847a6372de4b2eb3dbd`, Transformers 5.15.0, torch `2.12.0+rocm7.14.0`, 1× MI300X VF, SDPA, mean-pool cosine sanity.  
**Not claimed:** Validated retrieval quality, NVFP4, Nano LM, sentence-transformers serving, Radeon, Ryzen AI.

Encoder (`Ministral3Model`). Load ~15.0 GiB allocated. Same Yarn `apply_yarn_scaling` warning as Embed 1B.

## What ran

Paraphrase cosine **0.6304** > unrelated **0.1175**. Load+forward sanity, not MTEB.

## Caveats

- Informal, not a benchmark.
- Do not cite as Nano 30B evidence.

Logs: `logs/family-smoke.log`.
