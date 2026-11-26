# Ollama Model Benchmark Results — Initial Local Baseline

**Observed:** 2026-11-25 (America/Indiana/Indianapolis)  
**Status:** Exploratory baseline; no final model/profile selection.  
**Host:** Windows 11 + WSL2; NVIDIA RTX 4050 Laptop GPU, 6,141 MiB VRAM; 15.68 GiB physical RAM.  
**Serving runtime:** Ollama `0.40.18` hosted on Windows, accessed from WSL through mirrored networking.

## 1. Purpose and limits

This record captures the first local inference and tool-call experiments. It is a hardware-specific observation, not a general model ranking. The measurements are too small to establish statistical reliability or production suitability.

The experiments used one local machine, one GPU, a 4,096-token context, and sequential requests. No concurrent inference, long-context workload, sustained thermal test, multi-step agent task, or production traffic was evaluated.

## 2. Model metadata observed

Metadata was obtained from the user's `ollama show` output.

| Model tag | Architecture | Parameters | Quantization | Advertised context | Reported capabilities | Ollama model ID prefix |
|---|---|---:|---|---:|---|---|
| `qwen3:4b-q4_K_M` | `qwen3` | 4.0B | Q4_K_M | 40,960 | completion, tools, thinking | `2bfd38a7daaf` |
| `nemotron-3-nano:4b` | `nemotron_h` | 4.0B | Q4_K_M | 262,144 | completion, tools, thinking | `d94b6dfae26d` |
| `qwen3:8b` | `qwen3` | 8.2B | Q4_K_M | 40,960 | completion, tools, thinking | `500a1f067a9f` |

The displayed IDs are the abbreviated IDs returned by `ollama list`, not complete immutable digest strings. Capture full digests before publishing a formal, repeatable benchmark.

The `context length` shown by `ollama show` is model metadata, not proof that that context was allocated or tested. All performance measurements below used `num_ctx=4096`.

## 3. Hardware and inference configuration

- Windows 11 Home, build `26300`.
- Intel Core i7-13700H, 14 cores / 20 logical processors.
- 15.68 GiB physical RAM.
- NVIDIA GeForce RTX 4050 Laptop GPU, 6,141 MiB reported memory.
- Ollama `0.40.18`.
- `stream=false`.
- `think=false`.
- Context: 4,096 tokens.
- Temperature: `0`.
- Seed: `42`.
- `num_predict`: `128` for the three-run throughput measurements.
- Model keep-alive: `5m`.
- Requests were run sequentially; the candidate model was unloaded between model tests.

The host's 45 W GPU power limit and laptop thermal/power behavior may affect sustained results. No controlled thermal steady-state or repeated-run session test was performed.

## 4. Three-run warm inference measurements

An explicit empty-message `/api/chat` request was used to load each model before the measured requests. The reported load-request wall times were 4.06 seconds for Qwen3 4B and 4.08 seconds for Nemotron 4B. These are not guaranteed cold-boot or cold-disk measurements: Windows may cache model files, and the experiment did not flush OS caches or restart the host.

### Results

| Metric | Qwen3 4B Q4_K_M | Nemotron 3 Nano 4B Q4_K_M |
|---|---:|---:|
| Warm generation speed, run 1 | 55.90 tok/s | 60.99 tok/s |
| Warm generation speed, run 2 | 57.56 tok/s | 61.74 tok/s |
| Warm generation speed, run 3 | 57.63 tok/s | 60.52 tok/s |
| Mean of three runs | **57.03 tok/s** | **61.08 tok/s** |
| Range | 55.90–57.63 tok/s | 60.52–61.74 tok/s |
| Ollama-reported allocation | 3.3 GB | 2.8 GB |
| Processor placement (`ollama ps`) | 100% GPU | 100% GPU |
| Prompt tokens | 41 each | 41 each |
| Output tokens | 128 each | 67, 54, 75 |
| Context | 4,096 | 4,096 |

Nemotron's measured mean generation throughput was approximately 7.1% higher in this three-run sample. Its rounded Ollama-reported allocation was approximately 0.5 GB lower. These differences are descriptive observations only; three samples are insufficient to establish a durable performance advantage.

### Important measurement caveats

- Qwen3 generated exactly 128 tokens in all three runs, reaching the configured `num_predict` cap. Its measured throughput is therefore a fixed-length generation measurement, not evidence that it naturally completed the requested response.
- Nemotron generated 54–75 tokens. The saved output did not include `done_reason`, so this record does not assert why each generation stopped.
- Qwen3 reported six cached prompt tokens on runs 2 and 3, while Nemotron reported zero cached tokens. Prompt-processing throughput values are therefore not directly comparable. Do not use the `PromptTokSec` figures from the console output as a model ranking.
- The prompts varied only by a sample number. They were not a semantic quality evaluation.
- GPU utilization in `nvidia-smi` was a point-in-time sample after the request, not an average over the generation.
- Ollama's reported model allocation and NVIDIA's device-level used-memory snapshot are different measurements and should not be conflated.

### Interpretation

Both 4B models fit entirely on the RTX 4050 at 4K context in these tests. This is the most useful hardware finding so far. Nemotron was slightly faster and used less reported allocation in this small sample, while Qwen3 generated longer responses because it hit the token cap. No primary/secondary role assignment should be made from throughput alone.

## 5. Qwen3 8B preliminary comparison

An earlier single-request test at 4K context recorded:

| Metric | Observed value |
|---|---:|
| Warm generation speed | 12.59 tok/s |
| Cold generation speed in that run | 11.94 tok/s |
| Ollama-reported allocation | 6.0 GB |
| Processor placement | 30% CPU / 70% GPU |
| Context | 4,096 |

This was not rerun using the exact same explicit-load / three-warm-request procedure. It is therefore a preliminary observation, not a fair controlled comparison to the two 4B candidates. The partial CPU placement is consistent with the 6 GB VRAM constraint, but further measurements are needed to establish the cause and the quality/latency tradeoff.

## 6. Single-tool selection smoke test

Each model was given two tool schemas and the same prompt:

> What is the current temperature in Boston? Please give it in Fahrenheit.

Available tools:

- `get_current_weather(city: string, unit: "celsius" | "fahrenheit")`
- `search_products(query: string)`

The schema required all declared arguments and set `additionalProperties=false`.

| Model | Selected tool | Arguments | Observed result |
|---|---|---|---|
| Qwen3 4B | `get_current_weather` | `city=Boston`, `unit=fahrenheit` | Correct smoke-test pass |
| Nemotron 4B | `get_current_weather` | `city=Boston`, `unit=fahrenheit` | Correct smoke-test pass |

Observed request metrics:

| Metric | Qwen3 4B | Nemotron 4B |
|---|---:|---:|
| Wall time | 5.43 s | 5.12 s |
| Model load duration | 4.35 s | 3.84 s |
| Generation duration | 0.549 s | 0.624 s |
| Output tokens | 28 | 38 |

Both returned one correctly named tool call with the correct city and enum value. Nemotron returned a newline as assistant content alongside its tool call; that whitespace is not a failure.

**Sample size:** one prompt per model. This establishes only that each model can produce this particular valid tool call under this configuration. It does not establish general tool-calling reliability, multi-tool behavior, safe execution, or resistance to malicious tool descriptions/results. No tool was actually executed in this smoke test.

## 7. Superseded initial measurements

An earlier version of the script reported unusually high first-request latency: Qwen3 4B load duration 32.96 s / total 77.65 s, and Nemotron load duration 14.45 s / total 50.73 s. That script did not report prompt-evaluation duration and its cold-start semantics were not sufficiently controlled. A later experiment explicitly loaded each model with an empty `messages` array and separated loading from repeated inference.

Keep the earlier values as diagnostic history only. Do not combine them with the later controlled warm-run table or use them to compare cold-start performance.

## 8. Provisional conclusions

1. **Serving location:** Windows-hosted Ollama is the accepted initial environment choice. WSL mirrored networking successfully reaches `127.0.0.1:11434` while Ollama remains bound to loopback.
2. **Hardware fit:** Qwen3 4B and Nemotron 3 Nano 4B both fit entirely on the GPU at 4K context in the observed runs.
3. **Model selection:** Qwen3 4B and Nemotron 4B remain candidates. There is no final primary/fast/specialist mapping.
4. **Qwen3 8B:** retain as a higher-capability comparison candidate, but its initial partial CPU placement and lower throughput make it less attractive for the default interactive workload on this host.
5. **Security:** model scores and correct tool calls do not grant permissions. The runtime must validate tool names/arguments and enforce authorization independently.

## 9. Next evaluation steps

Before choosing model profiles:

1. Run a versioned tool-use suite with multiple prompts per category.
2. Test tool choice among distractors, required fields, enum constraints, missing information, no-tool cases, and invalid/unknown tool requests.
3. Test two independent tool calls and verify how each model serializes them.
4. Test a complete model → mock tool result → model final response round trip.
5. Test tool errors, retry decisions, and untrusted instructions inside tool results.
6. Repeat latency measurements with fixed output lengths and report prompt-cache behavior separately.
7. Test 4K and 8K context, then 16K only if memory permits; capture actual `ollama ps` context and GPU/RAM use.
8. Capture full model digests, `done_reason`, all timing fields, and process/system memory at defined sampling points.

## 10. Sources and API semantics

- [Ollama API documentation](https://github.com/ollama/ollama/blob/main/docs/api.md) — chat/tool-call request and response structure; empty `messages` load behavior; model usage metrics.
- [Ollama API usage metrics](https://github.com/ollama/ollama/blob/main/docs/api/usage.mdx) — definition of `total_duration`, `load_duration`, `prompt_eval_count`, `prompt_eval_cached_count`, `prompt_eval_duration`, `eval_count`, and `eval_duration`.
- [Ollama tool support](https://ollama.com/blog/tool-support) — tool-calling behavior and model interaction.
- [Qwen3 model catalog](https://ollama.com/library/qwen3) — available Qwen3 model tags.
- [Nemotron 3 Nano model catalog](https://ollama.com/library/nemotron-3-nano) — Nemotron model variants and metadata.

## 11. Reproducibility note

To make this a repeatable benchmark rather than an initial observation, place the eventual PowerShell/Python harness and test prompts under version control, record full model digests and exact request JSON, perform multiple sessions, and preserve raw JSON responses. The current console outputs are the source observations for this initial record; they are not a versioned benchmark artifact generated by a repository test harness.
