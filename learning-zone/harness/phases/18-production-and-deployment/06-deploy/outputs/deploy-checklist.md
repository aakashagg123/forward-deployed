---
name: agent-deploy-checklist
description: Production go-live checklist for a coding-agent harness.
kind: settings
phase: 18
lesson: 6
---

# Agent deployment checklist

Run before pointing real traffic / real repos at the agent. Each item → its lesson.

## Environment
- [ ] Runs in a fresh, isolated, **ephemeral** container (P18 L1).
- [ ] Results are committed/pushed (box is reclaimed).

## Gate
- [ ] Eval harness runs in CI and **blocks** regressions (P18 L2 / P15).
- [ ] Security review + injection eval pass (P17).

## Behavior control
- [ ] Model, budgets, prompt version, features behind layered config + flags (P18 L4).
- [ ] Shipped behind a **canary**; **kill switch** wired to a flag (P18 L5).

## Safety
- [ ] Least-privilege permissions; `.env` blocked; egress allowlist (P8, P17).
- [ ] Model output treated as data, never control flow (P17 L2).

## Reliability
- [ ] Retries + backoff; loop/tool/token/cost budgets; degraded mode (P14).

## Observability
- [ ] Traces, token/cost accounting, drift detection live (P16).

## Triggers (if event-driven)
- [ ] Webhook signatures verified; payloads treated as data; actions gated (P18 L3).

> For Claude Code / Codex users: sandboxed execution, permissions, and network policy are
> platform-provided. You supply `settings.json`, `CLAUDE.md`/`AGENTS.md`, hooks, and the
> CI eval gate.
