# ADR 0012: Portable, Cloud-Ready Deployment Shape

- **Status:** Accepted
- **Date:** 2026-11-26

## Context

The goal is to practise production engineering. Company services run as containers on Linux, configured from the environment, with state kept outside the app. Development currently happens on Windows with WSL, and Ollama runs on the Windows side ([ADR 0010](0010-windows-hosted-ollama-initial-deployment.md)).

## Decision

Build so the stack runs unchanged on the laptop, a Linux server, or a cloud VM. Only configuration differs.

- The application runs in containers; Docker Compose starts the stack locally.
- All configuration comes from environment variables and config files (endpoints, model profiles, folder grants, budgets). Nothing about Windows or WSL is hard-coded.
- App processes hold no state. PostgreSQL and the artifact store hold it.
- Health and readiness endpoints, logs to stdout, secrets from the environment or a secrets file and never from code.
- CI runs on Linux.

There is no actual cloud deployment, to keep running costs at zero.

## Consequences

- The Windows-hosted Ollama endpoint is a local configuration value.
- The sandbox choice must work on a plain Linux host, not only under WSL.
- A clean-host bring-up test (fresh clone, `.env` from the example, `docker compose up`) joins the release review.

## Revisit when

A real deployment target appears with requirements this shape doesn't meet.
