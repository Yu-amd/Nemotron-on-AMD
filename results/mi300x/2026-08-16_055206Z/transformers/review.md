# Review: llama-nemotron-rerank-1b-v2 (text)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=PASS`)  
**Claim allowed after this review:** **Runs** for `nvidia/llama-nemotron-rerank-1b-v2`, revision `d896ceda696c5c6fe0abf65f63a77c691bbf4548`, Transformers 5.15.0, torch `2.12.0+rocm7.14.0`, 1× MI300X VF. Custom code `llama_bidirec` / `LlamaBidirectionalForSequenceClassification`.  
**Not claimed:** Validated retrieval ranking, VL rerank, vLLM, Optimized.

Load ~2.38 GiB. `trust_remote_code` required.

## What ran

Query/document score: relevant **7.531** > banana sentence **-17.875**. Concatenated query+[SEP]+doc, not a published rerank protocol.

## Caveats

- Informal pair only.
- Not VL. Not Nano 30B evidence.

Logs: `logs/family-smoke.log`.
