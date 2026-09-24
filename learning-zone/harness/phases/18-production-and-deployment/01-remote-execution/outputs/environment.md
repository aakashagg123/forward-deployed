---
name: remote-execution-environment
description: Deployment contract for running an agent in a fresh, isolated, ephemeral box.
kind: settings
phase: 18
lesson: 1
---

# Remote execution environment

| Property | Setting |
|---|---|
| Trigger | web / CI / schedule / webhook |
| Base image | <language + tools, e.g. python:3.12 + node 20> |
| Setup script | install deps, build, warm caches (runs once on boot) |
| Repo | cloned fresh each run (no state from prior runs) |
| Network policy | default-deny → allowlist (registries, your APIs, api.anthropic.com) |
| Secrets | injected as env, least-privilege, never written to the repo |
| Persistence | **commit & push** anything to keep — the box is reclaimed after inactivity |
| Permissions | scoped per the project `settings.json` (Phase 8) |

## Rules
- Treat the environment as untrusted-by-default toward your machine: it can't reach your
  laptop or your unrelated credentials.
- Everything reproducible from the repo + setup script (no snowflake state).
- On finish: commit, push, and let the box be reclaimed.
