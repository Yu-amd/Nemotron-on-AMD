# Review: llama-nemotron-embed-vl-1b-v2 (retry2 FAIL)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=FAIL`)  
**Claim allowed:** none. Weights loaded (~3.2 GiB). Processor `process_documents` succeeded. Forward completed.  
**Error:** harness `IndexError` extracting `out[0]` from an empty Transformers `ModelOutput`. That is a **harness** bug, not a ROCm kernel miss. Later retry uses `_extract_embedding_tensor`.
