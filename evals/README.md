# Evaluation harness

Experiments that produce numbers for the docs. They run from WSL, use only the Python standard library, and save raw JSONL under `evals/results/`. Results quoted in `docs/research/` should point at a file here.

Needs Ollama reachable at `OLLAMA_BASE_URL` (default `http://127.0.0.1:11434`).

## context_scaling.py

Measures how each model behaves as `num_ctx` grows: Ollama's reported allocation, the GPU/CPU split, `nvidia-smi` memory, prompt and generation speed, and whether a code word placed at the start of a long prompt is still recalled at the end.

```bash
python3 evals/context_scaling.py                      # both 4B models at 4K, 8K, 16K, 32K
python3 evals/context_scaling.py --think --num-predict 512   # thinking on; give it room to finish
python3 evals/context_scaling.py --models qwen3:8b --ctx 4096 8192
```

Each configuration unloads the model, reloads it at the target `num_ctx`, and sends one prompt filled to 60% of the context (`--fill`). Settings: temperature 0, seed 42, `num_predict` 64 (change with `--num-predict`), `stream=false`.

**Reading the output**

- `GB` and `GPU`: Ollama's reported allocation and the share of it on the GPU. Anything under 100% means CPU offload and a speed cliff.
- `smi MiB`: device-level GPU memory used, from `nvidia-smi`. A different measurement from `GB`.
- `pp t/s` and `tg t/s`: prompt processing and token generation speed. Each model is reloaded per row, so the prompt cache is cold.
- `out`: output tokens. Generation speed from fewer than about 30 tokens is noisy; one stalled request can swing it by 50x.
- `needle`: `yes` if the code word is in the final answer, `think` if it only appears in the reasoning (the model ran out of `num_predict` before answering), `NO` if absent. `TRUNC` means the prompt reached the context limit and Ollama may have dropped the start of it, so a `NO` on that row isn't a model failure.
- An `ERROR` row usually means the context didn't fit in memory. That is a result, so keep it.

**Limits**

- Results files from before 2026-11-26 (`20261126T053811Z*`, `20261126T054844Z*`) used the old definition of `needle_recalled`, which counted reasoning text as a recall. Recompute from the saved `response` if you need to compare.
- One generation per configuration. At temperature 0 with a fixed seed, repeats mostly return the same answer, so more repeats add little. Add prompt variants instead.
- The filler is plain prose, and the needle is a single easy fact. This checks that the context works at all, not long-context reasoning.
- Token counts come from Ollama's `prompt_eval_count`. The script estimates the filler length from characters and doesn't tokenise.
- Run it with nothing else using the GPU, and note anything that was (browser, games, another Ollama model).
