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
