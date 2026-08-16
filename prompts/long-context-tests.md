# Long-context tests

Do **not** start here. Short-context Transformers and vLLM smoke tests must pass first.

Then increase context only after the previous length succeeds:

| Target context | Status | When to run |
| --- | --- | --- |
| 4K | **PASS WITH CAVEATS** (`024220Z`, ~3973 tokens) | Done |
| 8K | **PASS WITH CAVEATS** (`024220Z`, ~7991 tokens; prior short-prompt serve `223840Z`) | Done |
| 16K | **PASS WITH CAVEATS** (`024220Z`, ~15986 tokens, `max-model-len=16384`) | Done |
| 32K | **PASS WITH CAVEATS** (`024220Z`, ~31976 tokens) | Done |
| 64K | **PASS WITH CAVEATS** (`024220Z`, ~63956 tokens) | Done |
| 128K | **PASS WITH CAVEATS** (`024220Z`, ~127916 tokens, `max-model-len=131072`) | Done |
| 256K | NOT TESTED | After 128K. Hugging Face default config size; higher VRAM. Not run in this phase. |
| 1M | NOT TESTED | Official max. Requires `VLLM_ALLOW_LONG_MAX_MODEL_LEN=1` in NVIDIA examples. Do not attempt until 256K is characterized. |

For each length record:

- success / failure
- OOM yes/no
- startup time
- TTFT if measurable
- tokens/sec
- peak GPU memory
- configured `max_model_len`
- date, ROCm, PyTorch, vLLM/Transformers versions, checkpoint id

Prompt construction: repeat a short factual paragraph plus a question that can only be answered from the **first** and **last** markers (`HEAD_SECRET` color / `TAIL_SECRET` number). Script: `scripts/mi300x/context-ladder.py`. Evidence: `results/mi300x/2026-08-16_024220Z/`.

Nemotron 3 Nano official card (checked 2026-08-15):

- Maximum input size: 1M tokens
- Hugging Face default context in config: 256k because of higher VRAM
