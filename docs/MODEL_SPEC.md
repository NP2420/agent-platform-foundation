# Models: Gateway, Profiles, and Evaluation

**Status:** The provider abstraction and tiered profiles are accepted. Providers, model IDs, profile assignments, and routing policy stay open until benchmarked.

## Goals

- Keep the runtime independent of any one inference provider.
- Use Ollama first.
- Represent different capabilities and roles, and let one model fill several roles at first.
- Route on task needs, measured quality, latency, resource cost, and policy, never on parameter count or marketing.
- Keep provider-specific capabilities visible instead of pretending every API is the same.

## Components

- **Model registry:** known deployments and their metadata.
- **Profile:** a logical role with a policy, independent of any model ID.
- **Router:** picks a profile and deployment for a task.
- **Provider adapter:** translates internal requests to a provider API and normalises responses. It never executes tool calls; it returns them as untrusted proposals.
- **Capability registry:** tool calling, structured output, parallel calls, vision, streaming, context size, known limitations.
- **Usage accounting:** tokens and timings where the provider reports them; estimated or unavailable values are labelled as such.

## Profiles

| Profile | Used for | What to measure |
|---|---|---|
| `primary` | Reasoning, planning, final synthesis | Task success, tool-use reliability, usable context |
| `fast` | Classification, extraction, small transforms | Latency, schema validity |
| `summarizer` | Compressing history and tool results | Faithfulness; keeps constraints and provenance |
| `specialist` | A bounded task needing a modality or domain | Task-specific benchmark |
| `evaluator` | Independent checking | Agreement with reference labels; calibration |

These are roles, not a five-model deployment. The owner maps each profile to a deployment explicitly. Automatic routing comes later, and only on benchmark evidence.

## Request and response

**Request:** profile and deployment, normalised messages, provider-neutral tool definitions, output schema, inference options, deadline, correlation IDs, and an optional data-handling classification.

**Response:** content blocks, tool-call proposals, finish reason or refusal, structured-output status, usage, provider and model version, timings, and a normalised error.

## Routing

The router considers: task type and modality, required capabilities, measured quality for that task category, available VRAM and RAM and current load, the deadline, the run budget, local-data policy, and circuit-breaker state.

A fallback never moves private local data to a remote provider on its own. Remote fallback requires an explicit data policy and user configuration.

The model can suggest delegation; the router and policy decide whether another model call or child run actually happens. Depth, concurrency, budget, tool scope, and deadline are all enforced. The evaluator model is not ground truth and has to be calibrated against reference labels.

## Ollama baseline

Windows-hosted Ollama, reached from WSL at `http://127.0.0.1:11434` over mirrored networking ([ADR 0010](adr/0010-windows-hosted-ollama-initial-deployment.md)). The endpoint comes from configuration (`OLLAMA_BASE_URL`) and nothing about Windows networking is hard-coded.

Capabilities to verify against each exact model tag and Ollama version: text generation and streaming, tool calls including malformed arguments, how parallel tool calls are represented, JSON-schema output, resource use and latency, and behaviour on timeout and server restart.

**Current candidates.** Numbers and caveats are in the [benchmark record](research/OLLAMA_MODEL_BENCHMARKS_2026-11-25.md).

| Model | Role under evaluation |
|---|---|
| `qwen3:4b-q4_K_M` | Primary candidate |
| `nemotron-3-nano:4b` | Efficiency / secondary candidate |
| `qwen3:8b` | Quality reference. Partly offloads to CPU on this GPU. |

No profile is assigned yet.

## Evaluation plan

Tool calling and structured output vary with the model, prompt, quantisation, runtime version, context length, and serving configuration. Public leaderboards say nothing about this tool set on this hardware, so measure locally.

**Cases**, each with an expected tool or policy behaviour rather than a preferred wording:

1. Plain answer, no tool needed.
2. Correct tool among distractors, with varied phrasing.
3. Valid arguments: required and optional fields, enums, numeric bounds.
4. Missing information: the model asks instead of inventing an argument.
5. Malformed arguments and unknown tool names.
6. Two independent calls in one response.
7. Dependent calls where order matters.
8. Full round trip: tool call → tool result → final answer.
9. Tool error and recovery.
10. Prompt injection inside a tool result.
11. Long context: critical instructions survive at 8K, 16K, and 32K.
12. Summarisation against reference facts.

**Settings to vary:** thinking on and off (both candidates are thinking models, and all tests so far used `think=false`), and context length 4K, 8K, 16K, then 32K if it fits. Both candidates must fit at a realistic agent context before a profile is chosen. At temperature 0 with a fixed seed, repeat runs are near-identical, so confidence comes from more prompt variants, not more repetitions.

**Record:** model tag and full digest, Ollama version, quantisation, generation parameters, context length, prompt and dataset version, hardware, date, raw JSON responses, and `done_reason`. Keep cold-start and warm measurements separate. Report sample counts and failure examples; never hide a failure inside an aggregate.

**Metrics:** task success; tool selection accuracy; schema-valid and semantically correct arguments; unsupported tool attempts; injection resistance; final-answer correctness; calls and tokens per task; time to first token and end-to-end latency; peak VRAM and RAM; load time; parser failures, crashes, and hangs.

The harness lives in the repository (`evals/`), runs from WSL in Python, and saves raw output. Ad-hoc shell sessions are fine for exploration but don't count as results.

## Selection rule

Choose the smallest, fastest model that meets the measured quality and safety bar for a task, not the smallest one that returns valid JSON. Escalate to a stronger model only where that measurably improves outcomes. Add a second deployed model only if the measured trade-off justifies the operational cost.

## Other serving options

| Option | Consider when |
|---|---|
| llama.cpp | Finer control over GGUF quantisation or CPU/GPU placement |
| vLLM | Throughput and batching matter, on a GPU it supports |
| Hosted providers | Quality comparison, or tasks beyond local capability. Always optional. |
| LiteLLM | Enough providers that routing and fallback become a burden in our own adapters |
