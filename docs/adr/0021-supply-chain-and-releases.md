# ADR 0021: Supply Chain and Releases

- **Status:** Accepted
- **Date:** 2026-11-27

## Context

The roadmap ends every milestone with a release: a version tag, a changelog, release notes, and an SBOM. CI so far runs lint, types, and tests, with actions pinned to commit SHAs. Nothing yet keeps dependencies current, scans them for known vulnerabilities, checks the workflows themselves, or enforces the commit format that a changelog depends on. Six PR titles (#6–#11) already broke that format unnoticed.

## Decision

**Dependency updates.** Dependabot, weekly and grouped, for two ecosystems: `github-actions`, which keeps the SHA pins current, and `uv`. Dependabot's uv support covers version updates (generally available March 2025) and security updates (December 2025). It always raises the lower bounds in `pyproject.toml`, which is acceptable for an application whose real pins live in `uv.lock`; CI's `uv sync --locked` catches a lock that doesn't resolve.

**Cooldown.** `exclude-newer = "7 days"` in `pyproject.toml`, and a 7-day Dependabot cooldown. Compromised packages are often detected only days after publication, so nothing younger than a week gets resolved. An urgent security fix gets an explicit per-package override. Adding it on 2026-11-27 moved five transitive dev dependencies back to their previous releases.

**Vulnerability scan.** An `audit` CI job runs `uv audit --locked` against the OSV database on every PR. `uv audit` is a preview feature; CI pins the uv version, so its interface can't change unannounced. A finding with no fix available may be ignored by ID, with a reason in the PR.

**Workflow analysis.** zizmor on every PR, for template injection, credential persistence, over-broad permissions, and unpinned actions. The initial workflows pass its auditor persona with no findings.

**Commit format.** A `pr title` check enforces Conventional Commits on PR titles with a plain shell pattern; the title reaches the script through an environment variable, never by interpolation.

**Releases.** release-please (v5.0.0) keeps a release PR open on `master`, with the version and changelog computed from the commits. Merging it at the end of a milestone creates the tag and GitHub release; the workflow then attaches a CycloneDX SBOM (`uv export --format cyclonedx1.5`, runtime dependencies only).

- The version also lives in `uv.lock`, which would otherwise go stale on every release. release-please's TOML updater rewrites that one field; tested against this repository's lock file, it changes nothing else.
- PRs opened with `GITHUB_TOKEN` don't trigger CI, so the release PR could never pass the ruleset. The workflow instead mints a short-lived token from a GitHub App installed only on this repository. The App's private key is a secret of the `release` environment, which only `master` may deploy to.
- The version restarts at 0.0.0, so the first release, at the end of milestone 1, is v0.1.0.

**Required checks** on `master`: `lint, types, tests`, `audit`, `pr title`, and `zizmor`.

## Consequences

- Weekly Dependabot PRs to review. Grouping keeps it to about two a week.
- A newly published advisory can block unrelated PRs until it's fixed or explicitly ignored. That's intended.
- The GitHub App and the `release` environment are manual setup outside the repository, documented in CONTRIBUTING.
- The release PR stays open through a milestone and is merged only at its end.

## Revisit when

`uv audit` or uv's CycloneDX export leave preview with changed interfaces, Dependabot gains lockfile-only updates for uv, or releases need signing and provenance attestations.
