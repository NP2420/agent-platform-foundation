# Models: Gateway, Profiles, and Evaluation

**Status:** The provider abstraction and configurable profiles are accepted; one profile (`primary`) for now. Both tool-call methods, no automatic fallback, the licence registry, and pinned digests are accepted (2026-11-27). Model IDs, profile assignments, and routing policy stay open until benchmarked.

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

A profile is a named role mapped to a provider and model in configuration. Milestone 1 defines one, `primary`, and the eval can run it against any configured deployment.

```yaml
# illustrative
profiles:
  primary:
    provider: ollama
    model: nemotron-3-nano:4b
    num_ctx: 16384
providers:
  ollama:    { base_url: ${OLLAMA_BASE_URL} }
  anthropic: { api_key: ${ANTHROPIC_API_KEY}, monthly_limit_usd: 10 }
```

More profiles (for example `fast`, `summarizer`, `evaluator`) are added only when a measured need appears: a task category that one model handles too slowly, too expensively, or too poorly. Automatic routing between profiles comes later still.

## Model registry, licences, and pinning

Every model the system can call has a registry entry: provider, model ID, tag, full digest (for local weights), licence, source, the date it was added, and the uses the licence permits. A model whose licence doesn't permit the intended use (commercial use, for example) can't be assigned to a profile. Embedding and reranker models are registered the same way.

Profiles reference a model by tag **and** digest. At startup, and before an eval run, the adapter checks that the served model matches the pinned digest, and refuses to run on a mismatch. A silent `ollama pull` that changes the weights under a tag would otherwise change results with no record. Hosted models are pinned to a dated model ID, never to an alias that moves.

## Tool-call methods

Two ways to get tool calls out of a model, both implemented in M1.4 behind the same adapter contract:

- **Native tool calling:** tool definitions go in the provider's tool field, and calls come back in its structured tool-call format.
- **Schema-constrained JSON:** the model is asked for one JSON object matching a schema that covers every allowed action (tool calls, `ask_user`, final answer), with the server's structured-output constraint where the provider supports one.

Each profile names its method. Small local models differ in which method they handle reliably, so the choice is made per model by the M1.7–M1.9 eval, never assumed. Either way, the result is an untrusted proposal that is validated before policy sees it.

## Request and response

**Request:** profile and deployment, normalised messages, provider-neutral tool definitions, output schema, inference options, deadline, correlation IDs, and an optional data-handling classification.

**Response:** content blocks, tool-call proposals, finish reason or refusal, structured-output status, usage, provider and model version, timings, and a normalised error.

## Routing

The router considers: task type and modality, required capabilities, measured quality for that task category, available VRAM and RAM and current load, the deadline, the run budget, local-data policy, and circuit-breaker state.

**No automatic fallback.** A run never switches to another model or provider because a call failed. The failure is retried within the [retry policy](RUNTIME_SPEC.md#retries) and then surfaced, so every result can be traced to the model that produced it, and a quality or cost difference never hides behind a silent switch. Moving private local data to a remote provider always requires an explicit data policy and user configuration. Restricted data never goes to a hosted model.

The model can suggest delegation; the router and policy decide whether another model call or child run actually happens. Depth, concurrency, budget, tool scope, and deadline are all enforced. The evaluator model is not ground truth and has to be calibrated against reference labels.

## Providers

| Provider | Role | Notes |
|---|---|---|
| Ollama | Default, local | Free, private; limited to models that fit 6 GB of VRAM |
| Anthropic API | Optional, hosted | Quality baseline for evals and hard tasks. Paid from a prepaid Console balance with a hard spend limit; a Claude chat subscription doesn't include API access. Default comparison model: the cheapest current Claude model, with larger ones opt-in. |
| Fake | Tests | Scripted responses and errors; no network |

Every call records input and output tokens, latency, and cost (computed from a configured price table for hosted models; zero for local). Runs enforce token and spend budgets ([runtime spec](RUNTIME_SPEC.md#budgets)). API keys come from the environment and never appear in logs, traces, or the repository.

## Ollama baseline

Windows-hosted Ollama, reached from WSL at `http://127.0.0.1:11434` over mirrored networking ([ADR 0010](adr/0010-windows-hosted-ollama-initial-deployment.md)). The endpoint comes from configuration (`OLLAMA_BASE_URL`) and nothing about Windows networking is hard-coded.

Capabilities to verify against each exact model tag and Ollama version: text generation and streaming, tool calls including malformed arguments, how parallel tool calls are represented, JSON-schema output, resource use and latency, and behaviour on timeout and server restart.

**Current candidates.** Numbers and caveats are in the [benchmark record](research/OLLAMA_MODEL_BENCHMARKS_2026-11-25.md).

| Model | Role under evaluation |
|---|---|
| `qwen3:4b-q4_K_M` | Candidate. Fully on GPU only up to 8K context on this card. |
| `nemotron-3-nano:4b` | Candidate. Fully on GPU through 32K context. |
| `qwen3:8b` | Quality reference. Partly offloads to CPU on this GPU. |

No profile is assigned yet. Resource fit now favours Nemotron at agent-realistic context lengths; output quality is untested, so that is not a selection.

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

**Stages.** Experiments run in stages, so expensive runs go only to candidates that survived cheap ones: a screen on a handful of cases (does it fit in memory, call tools, follow the schema), then the dev set to compare and tune, then the held-out test set once to confirm a decision. A result from an earlier stage never stands in for a later one.

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
| vLLM | More than one concurrent user. M3 runs the same load test on Ollama and vLLM behind the adapter, and adopts vLLM if Ollama's throughput is the bottleneck ([decision audit, A5](research/DECISION_AUDIT_2026-11-27.md#a5-ollama-until-m7--amend)). Caveats on this host: 6 GB of VRAM, and vLLM favours AWQ or GPTQ weights over GGUF, so the model files and their digests differ from Ollama's. |
| Hosted providers | Quality comparison, or tasks beyond local capability. Always optional. |
| LiteLLM | Enough providers that routing and fallback become a burden in our own adapters |
