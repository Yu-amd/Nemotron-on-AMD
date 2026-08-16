# Tuned fused-MoE configs

JSON files here are produced by `scripts/mi300x/tune-moe.sh` on the **actual** MI300X (or VF) and model shape (`E=128,N=1856` for Nano 30B).

Do **not** copy NVIDIA H100/B200 config files into this directory. vLLM will look them up via `VLLM_TUNED_CONFIG_FOLDER`.
