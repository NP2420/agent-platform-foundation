# ADR 0022: Dependency Licences, Code Scanning, and Coverage

- **Status:** Accepted
- **Date:** 2026-11-27
- **Extends:** [ADR 0020](0020-data-and-model-governance.md) (licences, now for code dependencies too) and [ADR 0021](0021-supply-chain-and-releases.md) (required checks)

## Context

ADR 0020 governs the licences of the corpus and the models, but not of the Python packages the product ships with. Nothing scans our own source for security bugs; zizmor covers workflows only. Nothing measures which code the tests reach.

Checking this turned up two licences in the planned stack that a permissive-only policy would block: psycopg 3 (our chosen database driver, [ADR 0019](0019-search-architecture.md)) is LGPL-3.0, and certifi (pulled in through httpx by the Anthropic and Ollama clients) is MPL-2.0.

## Decision

**Licences.** A `licenses` CI job checks **runtime dependencies only**. Dev tools aren't shipped, so their licences don't bind the product. It installs the locked runtime dependencies plus the `licenses` dependency group (pip-licenses), and fails on any licence string not in `licenses-allowed.txt`.

- **Allowed:** permissive licences (MIT, BSD, Apache-2.0, ISC, PSF-2.0, 0BSD, Unlicense, CC0-1.0, Zlib) and weak copyleft (MPL-2.0, LGPL-2.1, LGPL-3.0). Weak-copyleft packages may be imported unmodified; any change to their files stays under their licence.
- **Never allowed:** GPL, AGPL, SSPL, and unknown licences.
- **Exact strings.** Packages report licences inconsistently ("MIT", "MIT License", SPDX expressions), so the file lists exact strings. A new string fails until someone reviews it, and the PR that adds it names the package.

Verified locally: the check passes on today's tree; a simulated future stack (psycopg, httpx, Pydantic) passes; adding pylint (GPL-2.0-or-later) fails.

**Code scanning.** CodeQL default setup, enabled in repository settings with the default query suite. It scans PRs and runs weekly, and supports Python 3.15 syntax since CodeQL 2.27.3. The `protect-master` ruleset blocks merges on high-severity or worse code-scanning alerts.

**Coverage.** coverage.py with branch coverage runs the test suite in CI and writes a Markdown report to the job summary. There is no minimum: with one test today, any number would be arbitrary. Revisit with diff coverage (changed lines only) once real code exists.

**Required checks** on `master` become: `lint, types, tests`, `audit`, `licenses`, `pr title`, `zizmor`, plus the code-scanning rule.

## Consequences

- A dependency with a new licence string blocks its PR until the string is reviewed. That's intended.
- CodeQL adds a few minutes per PR, running in parallel with CI.
- Coverage is visible on every run, without a gate.

## Revisit when

A copyleft dependency needs modifying, the product ships as a distributed binary rather than a service, or the test suite is large enough for a coverage gate to mean something.
