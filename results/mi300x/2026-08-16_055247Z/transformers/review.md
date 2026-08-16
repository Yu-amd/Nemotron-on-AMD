# Review: nemotron-colembed-vl-4b-v2 (first FAIL)

**Date:** 2026-08-16  
**Artifact:** no `result.json` (`result` UNKNOWN in the batch log).  
**Error (log):** custom code needs `datasets`. AutoConfig retry was not wrapped, so metadata was not written.

Retry `2026-08-16_055835Z` loaded the Qwen3 VL embedder then failed on image-token count.
