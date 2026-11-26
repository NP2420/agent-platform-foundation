#!/usr/bin/env python3
"""Compare developer-loop speed on two filesystems (e.g. /mnt/c vs WSL ext4).

Usage (from WSL, with uv on PATH):
    python3 scripts/bench_fs.py /mnt/c/Users/<you>/bench-c
    python3 scripts/bench_fs.py ~/bench-wsl
    python3 scripts/bench_fs.py /mnt/c/Users/<you>/bench-c --venv ~/bench-venv   # hybrid

--venv puts the virtualenv somewhere else (e.g. WSL ext4) while the project
files stay in the target directory.

Each run creates a scratch project in the given directory and times:
  - creating a virtualenv with uv
  - installing a representative dependency set (uv cache warmed first)
  - importing those packages
  - running a generated pytest suite (100 files x 10 tests)
  - ruff over the installed site-packages (many files, like a large codebase)
  - git status on the generated tree

Standard library only. Prints a table and appends one JSON line to
bench_fs_results.jsonl in the current directory. Delete the scratch
directory afterwards.
"""

import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

PACKAGES = ["pytest", "ruff", "mypy", "pydantic", "fastapi", "sqlalchemy", "httpx"]
REPEATS = 3


def run(cmd, cwd, check=True):
    start = time.perf_counter()
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    elapsed = time.perf_counter() - start
    if check and proc.returncode != 0:
        sys.exit(f"command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr[-2000:]}")
    return elapsed


def median_of(cmd, cwd, check=True):
    return statistics.median(run(cmd, cwd, check) for _ in range(REPEATS))


def generate_tests(root):
    tests = root / "tests"
    tests.mkdir()
    for i in range(100):
        body = "\n".join(
            f"def test_{i}_{j}():\n    assert sum(range({j})) == {j * (j - 1) // 2}\n"
            for j in range(10)
        )
        (tests / f"test_mod_{i:03d}.py").write_text(body)


def main():
    args = sys.argv[1:]
    venv_parent = None
    if "--venv" in args:
        i = args.index("--venv")
        venv_parent = Path(args[i + 1]).expanduser().resolve()
        del args[i:i + 2]
    if len(args) != 1:
        sys.exit(__doc__)
    if not shutil.which("uv"):
        sys.exit("uv not found on PATH. Install it first: https://docs.astral.sh/uv/")
    root = Path(args[0]).expanduser().resolve() / "bench_fs_scratch"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    venv = (venv_parent / "bench_fs_venv") if venv_parent else (root / ".venv")
    if venv_parent:
        if venv.exists():
            shutil.rmtree(venv)
        venv_parent.mkdir(parents=True, exist_ok=True)

    # Warm uv's cache on the home filesystem so the timed install measures
    # writing into the target filesystem, not downloading.
    with tempfile.TemporaryDirectory() as warm:
        run(["uv", "venv", "-q", f"{warm}/.venv"], warm)
        run(["uv", "pip", "install", "-q", "--python", f"{warm}/.venv/bin/python", *PACKAGES], warm)

    py = str(venv / "bin" / "python")
    results = {}
    results["uv venv"] = run(["uv", "venv", "-q", str(venv)], root)
    results["uv pip install (warm cache)"] = run(
        ["uv", "pip", "install", "-q", "--python", py, *PACKAGES], root)
    results["import packages"] = median_of(
        [py, "-c", "import fastapi, sqlalchemy, pydantic, httpx"], root)
    generate_tests(root)
    results["pytest 1,000 tests"] = median_of(
        [py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"], root)
    results["ruff check tests"] = median_of(
        [str(venv / "bin" / "ruff"), "check", "--no-cache", "--exit-zero", "-q", "tests"], root)
    (root / ".gitignore").write_text(".venv/\n")
    run(["git", "init", "-q"], root)
    run(["git", "add", "tests", ".gitignore"], root)
    results["git status"] = median_of(["git", "status", "--porcelain"], root)

    print(f"\nproject: {root}\nvenv:    {venv}")
    for name, secs in results.items():
        print(f"  {name:<30}{secs:>9.3f} s")
    total = sum(results.values())
    print(f"  {'total':<30}{total:>9.3f} s")

    record = {
        "when_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target": str(root.parent),
        "venv": str(venv),
        "python": platform.python_version(),
        "uv": subprocess.run(["uv", "--version"], capture_output=True, text=True).stdout.strip(),
        "repeats": REPEATS,
        "seconds": {k: round(v, 3) for k, v in results.items()},
        "total_seconds": round(total, 3),
    }
    with open("bench_fs_results.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
    print(f"\nAppended to {os.path.abspath('bench_fs_results.jsonl')}")
    extra = f" {venv}" if venv_parent else ""
    print(f"Delete the scratch directories when done: rm -rf {root}{extra}")


if __name__ == "__main__":
    main()
