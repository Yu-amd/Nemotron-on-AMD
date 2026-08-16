# Review: VL rerank 1B v2 FP8

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=FAIL`)  
**Claim allowed:** none for ranking.

Model loaded (~3.4 GiB allocated) and produced pair scores, but relevant < irrelevant (`-0.845` vs `-0.557`). Ranking sanity failed. **R-FNUZ**. First FAIL dir kept. Not the BF16 VL rerank text-path **Runs**.
