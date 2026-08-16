# Review: llama-nemotron-embed-vl-1b-v2 (first FAIL)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=FAIL`)  
**Claim allowed:** none. Keep this dir.  
**Failure layer:** missing venv extras `requests` and `torchvision` (PyPI/CUDA torchvision was **not** installed; later retry used AMD `torchvision==0.27.0+rocm7.14.0`).

Revision was not captured. Sibling retry: `2026-08-16_055715Z`.
