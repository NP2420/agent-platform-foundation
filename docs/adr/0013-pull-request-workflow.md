# ADR 0013: Branches, Pull Requests, and CI

- **Status:** Accepted
- **Date:** 2026-11-26

## Context

Companies review every change through pull requests with automated checks. The owner wants to practise that workflow. The assistant writes most of the code and the owner reviews it. The repository will be public on GitHub.

## Decision

- Each chunk of work happens on a feature branch and becomes one pull request.
- The assistant may commit and push to feature branches. It never commits to, pushes to, or merges into `master`.
- The owner reviews and merges every PR.
- CI (GitHub Actions) runs lint, type checks, and tests on every PR. Evals join once they can run in CI.
- A PR description states the objective, design and alternatives, files changed, commands run with their actual output, and the next step.
- Commits use the owner's GitHub noreply address, not a personal email.
- Licence: Apache-2.0.
- **Two working copies.** The owner works in a clone on WSL ext4 (fast, and the only place Ollama is reachable). The assistant works in the Windows-side folder it can access, and runs unit tests on a scratch copy on its own disk. The owner's clone fetches the assistant's branches from that folder as a git remote named `assistant`, runs integration tests and evals, pushes to GitHub, and opens the PR. Measurements behind this are in the [environment baseline](../research/2026-11-25-environment-baseline.md).

## Consequences

- This replaces the earlier rule that assistants never commit. The new boundary is `master`.
- Branch protection on `master` (PR required, CI must pass) is configured once the remote exists.
- Personal data, private eval sets, secrets, and model weights must never reach any branch, because every branch is public.

## Revisit when

Collaborators join, or the review load makes a different flow necessary.
