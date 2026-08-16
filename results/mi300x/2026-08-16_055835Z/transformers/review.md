# Review: nemotron-colembed-vl-4b-v2 (retry FAIL)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=FAIL`)  
**Claim allowed:** none. Weights **did load** (~8.4 GiB). Revision `0ed152d91f8ad4c5d48296b51c220f686641a398`.  
**Error:** `ValueError: Image features and image tokens do not match, tokens: 0, features: 4`. Processor needs `process_documents` / chat template with an image slot, not raw `"a blue square"`.

Harness later retried with `process_documents`.
