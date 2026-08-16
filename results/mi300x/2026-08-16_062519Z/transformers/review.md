# Review: Omni Reasoning FP8 (first FAIL)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=FAIL`)  
**Error:** `mamba-ssm is required by the Mamba model but cannot be imported`. Do **not** pip install CUDA `mamba-ssm` into the ROCm venv. **R-FNUZ** plus this import. Retry with SDPA still may hard-require mamba-ssm.
