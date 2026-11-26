# Research Note: Local Model Baseline

**Decision:** Ollama is the agreed initial serving runtime. Model names, quantization, and profile mappings remain open until measured on the actual host.

## 1. Why benchmark locally

Tool calling and structured output vary by model, prompt, quantization, runtime version, context length, and serving configuration. Public benchmark rankings do not establish suitability for this particular tool set or hardware. Measure actual task performance and resource use.

## 2. Model profiles to evaluate

| Profile | Candidate tasks | Main failure to watch |
|---|---|---|
| Primary | planning, multi-step reasoning, tool use, final synthesis | incorrect decomposition/tool decisions |
| Fast | request classification, extraction, small transformations | confident but invalid structured output |
| Summarizer | conversation/tool-result summarization | dropping constraints, caveats, or provenance |
| Specialist | bounded code/vision/domain task | over-specialization or poor integration |
| Evaluator | checking answer/tool result against rubric | judge bias and poor calibration |

Start with one model mapped to multiple profiles. Add different models only if measured quality/latency/resource trade-offs justify the additional operational complexity.

## 3. Benchmark cases

Build a small versioned set covering:

1. Plain response with no tool.
2. Correct single-tool choice among distractor tools.
3. Valid tool arguments, including required/optional fields and enum/number bounds.
4. Invalid/malformed arguments and unknown tool names.
5. Multi-step tool then final response.
6. Independent tool calls where parallelism is permitted.
7. Dependent calls where order matters.
8. Tool error and recovery.
9. Prompt injection inside tool output/web/retrieved text.
10. Refusal/policy-required approval behavior.
11. Long context with preservation of critical instructions.
12. Summarization with reference facts and provenance.

For each case, define expected tool/policy behavior, not merely a preferred natural-language answer.

## 4. Metrics

- task success against explicit criteria;
- tool selection accuracy;
- schema-valid arguments;
- semantic argument correctness;
- unsupported tool/permission attempts;
- prompt-injection resistance in defined tests;
- final answer correctness/faithfulness;
- calls/tokens per task where available;
- time-to-first-token and end-to-end latency;
- peak RAM/VRAM and model load time;
- concurrent throughput and tail latency;
- crashes, hangs, and tool-call parser failures.

Record exact model tag/digest, Ollama version, quantization, prompt/agent version, generation parameters, hardware, OS, context length, test dataset version, and run date.

## 5. Experiment procedure

- Warm up model and define cold-start versus warm-request measurements separately.
- Repeat cases; report sample counts and variability.
- Use identical prompts/tool schemas and comparable generation settings.
- Separate deterministic format/contract checks from probabilistic semantic grading.
- Review failures manually; do not hide a failure inside an aggregate score.
- Compare one-model and tiered routing on the same task set later; include router overhead and total task success/cost.

## 6. Selection rule

Select the smallest/fastest model that meets the task's measured quality/safety requirement, not the smallest model that merely returns syntactically valid output. Use a stronger model/escalation path for difficult or high-impact tasks only when it measurably improves outcomes. Evaluator models require calibration and must not be the sole authority for security decisions.


## 7. Observed local environment and candidate results (2026-11-25)

The initial development host is Windows 11 Home + Ubuntu 26.04.1 under WSL2, with an NVIDIA RTX 4050 Laptop GPU (6,141 MiB) and 15.68 GiB physical RAM. Windows-hosted Ollama `0.40.18` is reachable from WSL at `http://127.0.0.1:11434` after WSL mirrored networking was enabled. The detailed environment record is `ENVIRONMENT_BASELINE_2026-11-25.md`.

The first candidate tags are:

- `qwen3:4b-q4_K_M` — Q4_K_M, 4.0B parameters, tools and thinking advertised by `ollama show`.
- `nemotron-3-nano:4b` — Q4_K_M, 4.0B parameters, tools and thinking advertised by `ollama show`.
- `qwen3:8b` — Q4_K_M, 8.2B parameters, tools and thinking advertised by `ollama show`; retained as a larger reference candidate.

At 4K context, both 4B models were reported by `ollama ps` as 100% GPU. Qwen3 4B used 3.3 GB reported allocation and averaged 57.03 tok/s over three warm runs. Nemotron 4B used 2.8 GB and averaged 61.08 tok/s over three warm runs. The samples are exploratory and not sufficient for a final model assignment. Qwen3 8B's separate preliminary test showed 6.0 GB allocation and 30% CPU / 70% GPU placement at 4K; it was not rerun under the identical three-run protocol.

One single-prompt tool-call smoke test per 4B model succeeded: both selected `get_current_weather` and returned `Boston` and `fahrenheit` when given that request and a distractor product-search tool. This is not a reliability estimate.

Full request settings, output, timing caveats, and next tests are recorded in [`OLLAMA_MODEL_BENCHMARKS_2026-11-25.md`](OLLAMA_MODEL_BENCHMARKS_2026-11-25.md).

## 8. Current provisional interpretation

- Qwen3 4B is the leading primary-agent candidate for further evaluation, not a selected production model.
- Nemotron 3 Nano 4B is a strong efficiency/secondary-model candidate for further evaluation, not a selected production model.
- The difference in three-run warm generation throughput (about 7.1% in favor of Nemotron) is not enough to choose a model; functional quality and safety behavior matter more.
- Both 4B models fit at 4K context. Higher context and concurrent requests may increase memory demand substantially; measure them explicitly.
- Qwen3 8B remains a quality comparison candidate, but the observed partial CPU placement makes it less attractive for the default interactive workload on this machine.

## 9. Next tests before model selection

Continue with multiple tool-use cases: single-tool selection with distractors, argument extraction, no-tool/clarification behavior, multiple calls, tool-result round trips, tool error recovery, and prompt injection in untrusted tool output. Do not execute real side effects during model-only evaluations. After tool behavior is measured, test fixed-output performance and 4K/8K context resource use, then review whether 16K is practical.
