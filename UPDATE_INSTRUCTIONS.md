# Documentation update 0.2.0 — installation instructions

This is a **patch bundle** for the existing Agent Platform documentation baseline 0.1.0. It contains only new or replacement documentation files; it does not contain source code or dependencies.

## Apply it

1. Make sure the original documentation baseline is already in your repository.
2. Extract this ZIP into the repository root, preserving directory paths.
3. Allow the included files to replace the existing versions when prompted.
4. Review `docs/PROJECT_STATUS.md` and `docs/DEVELOPMENT_ROADMAP.md`.
5. Check `git status` and commit the update.

PowerShell example, from the repository root (adjust the ZIP path):

```powershell
Expand-Archive -LiteralPath "$HOME\Downloads\agent-platform-docs-update-0.2.0.zip" -DestinationPath . -Force

git status

git add README.md docs

git commit -m "docs: record Phase 0 environment and inference findings"
```

If you have edited any of these files locally, inspect/merge the differences rather than overwriting your work.

## What changed

- Added the observed Windows/WSL2/Docker/GPU environment baseline.
- Added the initial Ollama inference and tool-call benchmark report.
- Added a project status snapshot.
- Recorded Windows-hosted Ollama over WSL mirrored networking as the initial deployment decision (ADR 0010).
- Updated the model baseline, model specification, technology stack, research log, roadmap, index, README, and file manifest.

## Important interpretation

The two 4B models have only passed a small number of exploratory tests. No final model/profile assignment has been made. No application code has been implemented. Phase 0 remains in progress.
