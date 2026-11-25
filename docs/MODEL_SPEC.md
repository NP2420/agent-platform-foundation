# Model Gateway and Routing Specification

**Status:** Model abstraction and tiered intent are agreed directions; exact providers, profiles, model IDs, and routing policy remain open until benchmarked.

## 1. Goals

- Keep the runtime independent of any one inference provider.
- Use Ollama as the first local inference baseline.
- Represent different model capabilities and usage profiles.
- Permit one model to fill multiple profiles initially.
- Route work by task requirements, measured quality, latency, resource cost, and policy—not by model size or marketing labels alone.
- Preserve provider-specific capabilities where needed rather than pretending every API is identical.

## 2. Logical components

- **Model registry:** known model deployments and metadata.
- **Model profile:** logical role/policy (for example primary or summarizer), independent of a specific model ID.
- **Router:** selects a profile/deployment based on task and policy.
- **Provider adapter:** translates internal requests to provider-specific API calls and normalizes responses.
- **Capability registry:** declares supported tool calling, structured output, parallel calls, vision, streaming, context size, and relevant limitations.
- **Usage accounting:** captures token counts and provider metrics where available; clearly marks unavailable/estimated values.

## 3. Initial logical profiles

| Profile | Intended tasks | Requirements to measure |
|---|---|---|
| `primary` | Main reasoning, planning, final synthesis | Task success, reliable tool use, context capacity |
| `fast` | Classification, extraction, simple transformation | Low latency, schema reliability, acceptable quality |
| `summarizer` | Summarize history/results for context management | Faithfulness, preservation of key constraints and provenance |
| `specialist` | Bounded task requiring a particular modality/domain | Relevant benchmark and output contract |
| `evaluator` | Independent verification/critique | Agreement with expert/reference labels; calibration and bias |

These are profiles, not a required five-model deployment. Initially one Ollama-served model may back several profiles. The router should allow the owner to map each role to a deployment explicitly.

## 4. Request/response abstraction

A request should carry:

- profile/task category and selected model deployment;
- normalized message/content blocks;
- tool definitions in a provider-neutral schema form;
- output format/schema constraints;
- inference options and timeout/deadline;
- correlation/run/step identifiers;
- optional privacy and data-handling classification.

A response should carry:

- normalized content blocks;
- candidate tool-call requests (untrusted proposals);
- finish reason/refusal/structured-output status;
- usage details (provider reported, estimated, or unavailable);
- provider, deployment, and model version metadata;
- timing and request correlation;
- normalized error type and bounded provider details.

The adapter must not execute tool calls. It returns tool-call proposals to the runtime.

## 5. Capability-aware routing

Routing should consider:

1. Task type and required modality.
2. Required capabilities (tools, schema output, vision, streaming, context size).
3. Quality from evaluation results for this task category.
4. Resource availability (VRAM/RAM, active requests, local server load).
5. Deadline and latency objective.
6. Run budget and local-first/remote-data policy.
7. Availability/circuit-breaker state.

A fallback must not silently move private local data to a remote provider. Any remote fallback requires an explicit data policy and user configuration.

## 6. Ollama baseline

Ollama is the initial serving runtime. Its API supports message/tool interactions and schema-constrained structured output in current documentation, but actual behavior depends on the selected model and API version. Test each capability with the precise model tag and Ollama version.

Initial work:
- capture Ollama version and model tag/digest;
- verify health and model availability;
- test basic text generation and streaming;
- test a tool-call request and malformed tool arguments;
- test JSON-schema output;
- record actual resource use and request latency;
- verify whether parallel tool calls are returned and how they are represented;
- test behavior under timeout and server restart.

## 7. Other serving options

- **llama.cpp:** investigate for GGUF quantization/control and CPU/local-device flexibility.
- **vLLM:** investigate when throughput/batching and compatible GPU resources justify a serving stack with more configuration.
- **Hosted providers:** optional adapters for model quality comparison or tasks where local capability is insufficient. They are not mandatory to operate the platform.
- **LiteLLM:** reconsider if provider count, routing, fallback, and central usage policy become burdensome enough to justify a gateway.

## 8. Routing policy and model delegation

The model can suggest delegation or specialist analysis, but the runtime's router and policy engine decide whether to create another model invocation or child run. Do not allow unbounded recursive model spawning. Enforce call depth, concurrency, token/resource budget, tool scope, and deadline.

Use escalation sparingly: a fast model can classify or extract, but important decisions may require primary-model or deterministic verification. The evaluator model is not ground truth; benchmark it and calibrate it against reference labels/human review.

## 9. Required evaluation metrics

For each candidate model/profile, measure task success, tool selection accuracy, argument/schema validity, final-answer correctness, refusal/policy compliance, tokens or other reported usage, time-to-first-token, end-to-end latency, throughput under concurrency, peak RAM/VRAM, model loading time, stability under context growth, and failure behavior. Publish per-task results and sample sizes; do not rely on one aggregate score.

See `research/LOCAL_MODEL_BASELINE.md` and `EVALUATION_SPEC.md`.
