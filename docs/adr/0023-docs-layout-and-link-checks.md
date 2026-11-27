# ADR 0023: Docs Layout and Link Checks

- **Status:** Accepted
- **Date:** 2026-11-27

## Context

Most docs sat flat in `docs/` with upper-case names (`RUNTIME_SPEC.md`, `DEVELOPMENT_ROADMAP.md`), and research notes put the date at the end of the name, so they didn't sort by date. The assistant rules lived at `docs/ASSISTANT_WORKING_GUIDE.md`, where no coding agent looks for them. Nothing checked links: a rename could break dozens of them without anyone noticing.

Renaming gets more expensive as more files link to each other, so it is cheapest now, before milestone 1 adds code docs.

## Decision

**Layout by purpose.**

| Folder | Holds |
| --- | --- |
| `docs/project/` | Charter and roadmap: why the project exists and what happens when |
| `docs/design/` | Specs: how the system works or will work |
| `docs/adr/` | Decisions and their reasons (the MADR and adr-tools convention) |
| `docs/research/` | Evidence: benchmarks, audits, comparisons, and the research log |
| `docs/learning/` | The owner's learning path and sources |

**Names.** Lower-case kebab-case (`data-model.md`). Notes tied to a date start with it (`2026-11-27-decision-audit.md`), so they sort in order. Repository-level files keep their conventional upper-case names (`README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`).

**Agent instructions.** The assistant rules move to `AGENTS.md` at the root, the open format read by most coding agents and now stewarded under the Linux Foundation. `CLAUDE.md` holds only `@AGENTS.md`, the import syntax Claude Code documents, so there is one copy of the rules.

**Python version.** `.python-version` (`3.15`) tells uv and other tools which interpreter to use, matching `requires-python`.

**Link checks** with lychee, pinned like every other action:

- `links` runs on every PR and push to `master`, offline: relative file links and `#anchors` only. It's fast and doesn't depend on other sites, so it is a required check.
- `external links` runs weekly and on demand against the web. Outside sites go down and rate-limit, so it never blocks a PR; on failure it opens one issue, or comments on the open one.

**Not now:** a published docs site (MkDocs). It's worth having once there are readers other than the owner. At that point, the user-facing docs follow Diátaxis (tutorials, how-to guides, reference, explanation).

**Required checks** on `master` become: `lint, types, tests`, `audit`, `licenses`, `links`, `pr title`, `zizmor`, plus the code-scanning rule.

## Consequences

- One large rename PR. Old paths in closed PRs and earlier commits point at files that no longer exist under those names; `git log --follow` still traces them.
- Links that break in later PRs fail the `links` check before merge.
- lychee-action downloads the lychee binary from GitHub releases without checking a checksum. The action and the lychee version are both pinned, which limits but doesn't remove that risk.

## Revisit when

The project gets users who need a docs site, or the folder split stops matching how the docs are used.

## Sources

- [AGENTS.md](https://agents.md/)
- [Claude Code memory: importing files into CLAUDE.md](https://code.claude.com/docs/en/memory)
- [Diátaxis](https://diataxis.fr/)
- [lychee](https://github.com/lycheeverse/lychee) and [lychee-action](https://github.com/lycheeverse/lychee-action)
- [uv: Python versions and `.python-version`](https://docs.astral.sh/uv/concepts/python-versions/)
