#!/usr/bin/env python3
"""Context-scaling measurement for local Ollama models.

For each model and context length (num_ctx) it:
  1. unloads the model, then loads it at that num_ctx (empty-messages request),
  2. records Ollama's reported allocation, GPU/CPU split, and nvidia-smi memory,
  3. sends one prompt filled to a fraction of the context, with a short
     "needle" at the start that the model must repeat at the end,
  4. records timings, done_reason, and whether the needle was recalled.

Standard library only, so it runs on a bare WSL Python. Raw responses are saved
as JSONL under evals/results/. See evals/README.md.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
DEFAULT_MODELS = ["qwen3:4b-q4_K_M", "nemotron-3-nano:4b"]
DEFAULT_CTX = [4096, 8192, 16384, 32768]
NEEDLE = "KESTREL-4417"
CHARS_PER_TOKEN = 3.5  # conservative; the real count is read from prompt_eval_count
DEFAULT_NUM_PREDICT = 64

SENTENCES = [
    "The harbour office opens early and closes when the last ferry has left.",
    "Maintenance crews inspect the north pier twice a week during the summer.",
    "A new schedule was posted near the entrance, replacing the older printed one.",
    "Visitors are asked to sign the register before walking out to the lighthouse.",
    "Supplies arrive by truck on Tuesdays and are logged by the duty clerk.",
    "Rain delayed the repainting of the boathouse, which should resume next month.",
    "The community board reviewed the budget and approved a modest increase for repairs.",
    "Several volunteers offered to help catalogue the old photographs in the archive.",
]


def http(method, path, body=None, timeout=900):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE_URL + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        raise RuntimeError(f"HTTP {exc.code} on {path}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"request to {path} failed: {exc}") from exc
    return payload, time.perf_counter() - start


def unload(model):
    http("POST", "/api/chat", {"model": model, "messages": [], "keep_alive": 0})


def unload_all():
    ps, _ = http("GET", "/api/ps")
    for m in ps.get("models", []):
        unload(m["name"])


def load(model, num_ctx):
    _, wall = http(
        "POST",
        "/api/chat",
        {
            "model": model,
            "messages": [],
            "keep_alive": "5m",
            "options": {"num_ctx": num_ctx},
        },
    )
    return wall


def ps_entry(model):
    ps, _ = http("GET", "/api/ps")
    for m in ps.get("models", []):
        if m["name"] == model or m.get("model") == model:
            size, vram = m.get("size", 0), m.get("size_vram", 0)
            return {
                "size_bytes": size,
                "size_vram_bytes": vram,
                "gpu_fraction": round(vram / size, 3) if size else None,
                "context_length": m.get("context_length"),
            }
    return None


def nvidia_smi_mib():
    try:
        out = (
            subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.used,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )
            .stdout.strip()
            .splitlines()[0]
        )
        used, total = (int(x) for x in out.split(","))
        return {"used_mib": used, "total_mib": total}
    except OSError, subprocess.SubprocessError, ValueError, IndexError:
        return None


def build_prompt(num_ctx, fill):
    target_chars = int(num_ctx * fill * CHARS_PER_TOKEN)
    parts, size, i = [], 0, 0
    while size < target_chars:
        sentence = f"{SENTENCES[i % len(SENTENCES)]} (note {i + 1})"
        parts.append(sentence)
        size += len(sentence) + 1
        i += 1
    return (
        f"Remember this: the access code is {NEEDLE}.\n\n"
        + " ".join(parts)
        + "\n\nQuestion: what is the access code? Answer with the code only."
    )


def run_config(model, num_ctx, fill, think, num_predict):
    record = {
        "model": model,
        "num_ctx": num_ctx,
        "fill": fill,
        "think": think,
        "num_predict": num_predict,
    }
    try:
        unload(model)
        record["load_wall_s"] = round(load(model, num_ctx), 2)
        record["ps_after_load"] = ps_entry(model)
        record["gpu_after_load"] = nvidia_smi_mib()

        prompt = build_prompt(num_ctx, fill)
        record["prompt_sha256"] = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        request = {
            "model": model,
            "stream": False,
            "think": think,
            "keep_alive": "5m",
            "messages": [{"role": "user", "content": prompt}],
            "options": {
                "num_ctx": num_ctx,
                "num_predict": num_predict,
                "temperature": 0,
                "seed": 42,
            },
        }
        resp, wall = http("POST", "/api/chat", request)
        record["response"] = resp
        record["wall_s"] = round(wall, 2)
        record["ps_after_generate"] = ps_entry(model)
        record["gpu_after_generate"] = nvidia_smi_mib()

        msg = resp.get("message", {})
        record["needle_in_content"] = NEEDLE in (msg.get("content") or "")
        record["needle_in_thinking"] = NEEDLE in (msg.get("thinking") or "")
        record["done_reason"] = resp.get("done_reason")
        pe, ev = resp.get("prompt_eval_count", 0), resp.get("eval_count", 0)
        record["prompt_tokens"] = pe
        record["truncated"] = pe >= num_ctx - num_predict
        pd, ed = resp.get("prompt_eval_duration", 0), resp.get("eval_duration", 0)
        record["prompt_tok_s"] = round(pe / (pd / 1e9), 1) if pd else None
        record["gen_tok_s"] = round(ev / (ed / 1e9), 1) if ed else None
        record["error"] = None
    except RuntimeError as exc:
        record["error"] = str(exc)
    return record


def fmt_row(r):
    if r.get("error"):
        return f"{r['model']:<22}{r['num_ctx']:>7}  ERROR: {r['error'][:70]}"
    ps = r.get("ps_after_generate") or r.get("ps_after_load") or {}
    gb = ps.get("size_bytes", 0) / 1e9
    gpu = ps.get("gpu_fraction")
    gpu_s = f"{gpu * 100:.0f}%" if gpu is not None else "?"
    smi = (r.get("gpu_after_generate") or {}).get("used_mib")
    if r["needle_in_content"]:
        needle = "yes"
    elif r["needle_in_thinking"]:
        needle = "think"  # only inside the reasoning; no final answer
    else:
        needle = "NO"
    out_tokens = r["response"].get("eval_count", 0)
    return (
        f"{r['model']:<22}{r['num_ctx']:>7}{gb:>8.1f}{gpu_s:>6}"
        f"{(str(smi) if smi is not None else '?'):>9}{r['prompt_tokens']:>9}"
        f"{(r['prompt_tok_s'] or 0):>9.0f}{(r['gen_tok_s'] or 0):>8.1f}{out_tokens:>6}"
        f"{needle:>7}{'TRUNC' if r['truncated'] else '':>7}{r['wall_s']:>8.1f}"
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("--ctx", nargs="+", type=int, default=DEFAULT_CTX)
    ap.add_argument(
        "--fill",
        type=float,
        default=0.6,
        help="fraction of num_ctx to fill with prompt text (default 0.6)",
    )
    ap.add_argument("--think", action="store_true", help="enable thinking (default off)")
    ap.add_argument(
        "--num-predict",
        type=int,
        default=DEFAULT_NUM_PREDICT,
        help="max output tokens (default 64; raise it with --think)",
    )
    ap.add_argument("--out", type=Path, default=Path(__file__).parent / "results")
    args = ap.parse_args()

    try:
        version, _ = http("GET", "/api/version", timeout=10)
        tags, _ = http("GET", "/api/tags", timeout=10)
    except RuntimeError as exc:
        sys.exit(f"Cannot reach Ollama at {BASE_URL}: {exc}")
    digests = {m["name"]: m.get("digest") for m in tags.get("models", [])}
    missing = [m for m in args.models if m not in digests]
    if missing:
        sys.exit(f"Models not installed: {', '.join(missing)}")

    args.out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    path = args.out / f"{stamp}_context_scaling{'_think' if args.think else ''}.jsonl"
    meta = {
        "kind": "meta",
        "started_utc": stamp,
        "ollama_version": version.get("version"),
        "base_url": BASE_URL,
        "digests": {m: digests[m] for m in args.models},
        "args": {
            "models": args.models,
            "ctx": args.ctx,
            "fill": args.fill,
            "think": args.think,
            "num_predict": args.num_predict,
            "temperature": 0,
            "seed": 42,
        },
        "gpu_idle": nvidia_smi_mib(),
    }
    print(f"Ollama {meta['ollama_version']} at {BASE_URL}; writing {path}")
    print(
        f"{'model':<22}{'ctx':>7}{'GB':>8}{'GPU':>6}{'smi MiB':>9}{'prompt':>9}"
        f"{'pp t/s':>9}{'tg t/s':>8}{'out':>6}{'needle':>7}{'':>7}{'wall s':>8}"
    )

    unload_all()
    with path.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(meta) + "\n")
        for model in args.models:
            for num_ctx in args.ctx:
                rec = run_config(model, num_ctx, args.fill, args.think, args.num_predict)
                rec["kind"] = "result"
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                print(fmt_row(rec), flush=True)
            unload(model)
    print(f"\nRaw results: {path}")


if __name__ == "__main__":
    main()
