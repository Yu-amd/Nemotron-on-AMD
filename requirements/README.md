# Requirements files

These files are **documentation of intended packages**, not a command to install on this laptop.

Do **not**:

- `pip install -r requirements/mi300x.txt` on the Strix Point laptop
- install CUDA wheels on AMD
- modify system Python
- treat unpinned or range pins as proof of a working stack

Install on the **MI300X host** only after `scripts/mi300x/collect-env.sh` and inspect-only `scripts/mi300x/setup-python-env.sh` have recorded the actual ROCm version. The setup script maps ROCm → a PyTorch ROCm index and refuses CUDA indexes.

vLLM is intentionally absent from the Transformers-first MI300X file. Add it only after Nano BF16 Transformers smoke tests are reviewed, and only from a ROCm extra index or `vllm/vllm-openai-rocm`.
