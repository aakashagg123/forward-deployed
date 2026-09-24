---
name: failure-playbook
description: Production failure modes of a coding-agent harness and the structural fix for each.
kind: prompt
phase: 14
lesson: 6
---

# Harness failure-mode playbook

Symptom → structural fix (a mechanism, not a longer prompt). Use as a pre-launch checklist
and an incident guide.

| Failure mode | Structural fix |
|---|---|
| JSON sometimes doesn't parse | validation + repair loop; prefer tool-schema output |
| "It worked yesterday" (silent regression) | golden-set eval + CI gate |
| Agent runs 40 steps / spends $12 | step + tool + token + cost budgets |
| Latency spikes / provider overloaded | retries with backoff+jitter; fallback chain |
| Double-charged / double-sent | idempotency keys on side-effecting tools |
| Retrieved doc hijacked the agent | treat model output as data; prompt-injection defenses |
| Claimed success but tests failed | verify before reporting; degraded mode |
| Half-finished multi-file change | atomic patches; checkpoints |
| Secret leaked into logs/output | secret redaction hook |
| Same mistake every week | encode a lint rule / hook; delete the matching prompt line |
| Context full → wrong answers | budgeting, truncation, compaction; measure context rot |
| Two parallel workers clobber a file | disjoint files per wave (dependency graph) |

## Rule
When you hit a new failure mode, add a row. Prefer patching the harness (a rule, a hook, an
eval) over lengthening the prompt — the rule is enforcement; the prompt is persuasion.
