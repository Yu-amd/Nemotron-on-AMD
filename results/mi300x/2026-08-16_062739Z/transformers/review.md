# Review: NVIDIA-Nemotron-Parse-2.0 (retry4)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=BLOCKED`, mislabel)  
**Claim allowed:** none. Weights **did download** (~3.61 GB, rev `635b84d9…`). `open_clip`/`timm`/`einops` are past.  
**Error:** `AutoModelForImageTextToText` does not know `NemotronParseConfig`. Custom class is `NemotronParseForConditionalGeneration` via `AutoModel`. The harness deleted a working `AutoModel` load. `"nemotron"` also tripped the BLOCKED substring.  

Next retry keeps `AutoModel.generate`.
