# Review: Nano 30B FP8 (retry FAIL)

**Date:** 2026-08-16  
**Artifact:** `transformers/result.json` (`result=FAIL`)  
**Claim allowed:** none. **R-FNUZ** plus `ImportError: mamba-ssm is required by the Mamba model`. BF16 Nano 30B did **not** need `mamba-ssm`. Do not pip-install CUDA `mamba-ssm` into the ROCm venv.
