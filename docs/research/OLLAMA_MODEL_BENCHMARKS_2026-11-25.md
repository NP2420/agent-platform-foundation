# Ollama Model Benchmarks: Initial Screen

**Observed:** 2026-11-25 · **Status:** Exploratory; no model selected.

One laptop, one GPU, 4K context, sequential requests. No concurrency, long context, thermal steady state, or multi-step tasks yet. Treat these as hardware-specific observations, not a model ranking.

## Setup

- Windows 11 Home (build 26300), i7-13700H, 15.68 GiB RAM, RTX 4050 Laptop GPU (6,141 MiB, 45 W limit).
- Ollama 0.40.18 on Windows, called from WSL over mirrored networking.
- `stream=false`, `think=false`, `num_ctx=4096`, temperature 0, seed 42, keep-alive 5m.
- `num_predict=128` for the throughput runs.
- The candidate model was unloaded between models.

## Models

| Tag | Arch | Params | Quant | Advertised context | Capabilities | ID prefix |
|---|---|---:|---|---:|---|---|
| `qwen3:4b-q4_K_M` | `qwen3` | 4.0B | Q4_K_M | 40,960 | completion, tools, thinking | `2bfd38a7daaf` |
| `nemotron-3-nano:4b` | `nemotron_h` | 4.0B | Q4_K_M | 262,144 | completion, tools, thinking | `d94b6dfae26d` |
| `qwen3:8b` | `qwen3` | 8.2B | Q4_K_M | 40,960 | completion, tools, thinking | `500a1f067a9f` |

The IDs are the short prefixes from `ollama list`; capture full digests for repeatable runs. The advertised context is metadata only. Every run here used 4K.

`nemotron_h` indicates a hybrid Mamba–Transformer architecture, which usually needs less extra memory per added token of context than a pure Transformer. That could matter on a 6 GB card at 16K–32K. It is a hypothesis to measure.

## Warm throughput (three runs)

Each model was loaded first with an empty-messages `/api/chat` request (about 4.1 s wall time each). OS file caches were not flushed, so these are not true cold starts.

| Metric | Qwen3 4B | Nemotron 4B |
|---|---:|---:|
| Run 1 | 55.90 tok/s | 60.99 tok/s |
| Run 2 | 57.56 tok/s | 61.74 tok/s |
| Run 3 | 57.63 tok/s | 60.52 tok/s |
| **Mean** | **57.03 tok/s** | **61.08 tok/s** |
| Ollama-reported allocation | 3.3 GB | 2.8 GB |
| Placement (`ollama ps`) | 100% GPU | 100% GPU |
| Prompt tokens | 41 | 41 |
| Output tokens | 128, 128, 128 | 67, 54, 75 |

Caveats:

- Qwen3 hit the 128-token cap every time. Its figure is fixed-length throughput, not natural completion.
- `done_reason` wasn't saved, so Nemotron's stop reason isn't known.
- Qwen3 had 6 cached prompt tokens on runs 2 and 3, and Nemotron had none, so prompt-processing rates aren't comparable.
- The prompts differed only by a sample number. This was not a quality test.
- `nvidia-smi` readings were point-in-time samples taken after the request.

**Reading:** both 4B models fit fully on the GPU at 4K. Nemotron was about 7% faster and about 0.5 GB smaller in this tiny sample. That is not enough to assign roles.

## Qwen3 8B (preliminary)

A single earlier request at 4K: 12.59 tok/s warm (11.94 in the first request), 6.0 GB allocation, 30% CPU / 70% GPU. It was not run under the protocol above, so it isn't directly comparable. The partial CPU offload fits the 6 GB VRAM limit.

## Tool-call scenarios

Two tools: `get_current_weather(city, unit: celsius|fahrenheit)` and `search_products(query)`. All arguments required, `additionalProperties=false`. Tools were not executed.

| Scenario | Qwen3 4B | Nemotron 4B |
|---|---|---|
| T1 Weather: "current temperature in Boston, in Fahrenheit" | Pass | Pass |
| T2 Product search: "wireless mechanical keyboards under $100" | Pass (rerun) | Pass (rerun) |
| T3 Two independent tools in one request | Pass | Pass |
| T4 Weather request with no city | Pass | Pass |

- **T1:** both picked `get_current_weather` with `city=Boston`, `unit=fahrenheit`. Qwen3: 5.43 s wall, 4.35 s of it model load, 0.549 s generation, 28 output tokens. Nemotron: 5.12 s wall, 3.84 s load, 0.624 s generation, 38 output tokens. Nemotron also returned a newline as message content alongside the call, which is harmless.
- **T2:** the first attempt was invalid because of a harness bug. PowerShell interpolated `$100` in a double-quoted prompt as an empty variable, so the models received "under ." Rerun on 2026-11-26 with single quotes, so `$100` was preserved. Both selected `search_products` with the price in the query, and both stopped with `done_reason=stop`.
  - Qwen3: `"wireless mechanical keyboards under $100"`; 226 prompt tokens, 28 output tokens, 6.24 s wall (5.03 s load, 0.56 s generation).
  - Nemotron: `"wireless mechanical keyboard under $100"`; 472 prompt tokens, 34 output tokens, 6.61 s wall (5.14 s load, 0.74 s generation).
- **T3:** both returned two tool calls in one response, with correct arguments. This shows the models can *propose* parallel calls; our validation and scheduling of them is untested.
- **T4:** both asked for the city instead of inventing one.
- **Prompt size:** the same tool definitions came to about 220–230 prompt tokens with Qwen3 and 467–477 with Nemotron. That probably reflects each model's chat template and tokenizer rather than real input size. It still matters, because it comes out of the context budget.

T1, T3, and T4 are summarised from the session log, and the T2 rerun from console output; none of the raw output is in the repository yet. One prompt per scenario per model. This shows each behaviour can happen, not how reliably it happens.

## Superseded measurements

An earlier script reported first-request load times of 32.96 s for Qwen3 and 14.45 s for Nemotron (totals 77.65 s and 50.73 s). Cold-start conditions weren't controlled and prompt-evaluation time wasn't separated out. Kept as history only; don't compare against the table above.

## Conclusions so far

1. Windows-hosted Ollama over mirrored networking works ([ADR 0010](../adr/0010-windows-hosted-ollama-initial-deployment.md)).
2. Both 4B models fit fully on the GPU at 4K.
3. Both handle basic tool selection, parallel proposals, and asking for missing information in single examples.
4. Qwen3 8B is a quality reference, not a default, because of the CPU offload on this card.
5. Correct tool calls grant nothing. The runtime still validates and authorises every call.

## Next

The order is set by the roadmap status table: context scaling (8K/16K/32K), then thinking on, then the full round trip, error and injection cases, and multiple prompt variants per scenario. All of it through a versioned harness that saves raw JSON, full digests, `done_reason`, and all timing fields.

## Sources

[Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md) · [Ollama usage metrics](https://github.com/ollama/ollama/blob/main/docs/api/usage.mdx) · [Ollama tool support](https://ollama.com/blog/tool-support) · [Qwen3 on Ollama](https://ollama.com/library/qwen3) · [Nemotron 3 Nano on Ollama](https://ollama.com/library/nemotron-3-nano)
