# GitHub integration & CI triggers

> **Motto** — Wire the agent and its evals into the same CI that guards your code.

*Part of Phase 18 — Production & Deployment.*

## The Problem

A harness reaches production through GitHub. It opens PRs, responds to issues, and —
crucially — its **evals run in CI** as a required check (Phase 15). GitHub events also
trigger agent work: a label, a comment, a failing build. This lesson wires the eval gate into
a GitHub Actions workflow, so a change that regresses the harness can't merge.

## The Concept

<style>
.dgm-gci{background:#ffffff;border:1px solid #d1d9e0;border-top:3px solid #008300;
  border-radius:16px;padding:28px 26px 22px;box-shadow:0 1px 3px rgba(31,35,40,.04),0 8px 24px rgba(31,35,40,.04);
  margin:26px 0;max-width:100%;font-family:inherit;text-align:left;position:relative}
.dgm-gci-chip{position:absolute;top:-11px;left:24px;background:#008300;color:#ffffff;
  font-size:10.5px;font-weight:700;letter-spacing:1px;text-transform:uppercase;
  border-radius:20px;padding:3px 12px;box-shadow:0 2px 6px rgba(0,131,0,.28)}
.dgm-gci h4{margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:.4px;text-transform:uppercase;color:#59636e}
.dgm-gci-sub{font-size:12px;color:#59636e;margin:0 0 16px}
.dgm-gci-row{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
.dgm-gci-n{background:#f6f8fa;border:1px solid #d1d9e0;border-radius:9px;padding:9px 11px;text-align:center;
  font-size:10.5px;font-weight:700;color:#1f2328;line-height:1.3}
.dgm-gci-n.accent{background:#e6f5e6;border-color:#a8d8a8;color:#0d5c0d}
.dgm-gci-n.blue{background:#ddf4ff;border-color:#b6e3ff;color:#0550ae}
.dgm-gci-n.green{background:#dafbe1;border-color:#aceebb;color:#1a614f}
.dgm-gci-n.red{background:#ffebe9;border-color:#ffcecb;color:#82061e}
.dgm-gci-arr{color:#8c959f;font-size:12px;display:flex;flex-direction:column;align-items:center;gap:1px}
.dgm-gci-arr .lbl{font-size:8.5px;font-weight:700;color:#8c959f;text-transform:uppercase;letter-spacing:.3px}
@media (max-width:640px){.dgm-gci{padding:20px 16px 18px}.dgm-gci-row{flex-direction:column}}
.dgm-gci-q{background:#f6f8fa;border:1px dashed #d1d9e0;border-radius:10px;padding:9px 14px;text-align:center;
  font-size:11px;font-weight:700;color:#1f2328;margin-bottom:10px}
.dgm-gci-branches{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.dgm-gci-b{border-radius:11px;padding:11px 13px;border:1.5px solid}
.dgm-gci-b h6{margin:0 0 4px;font-size:10.5px;font-weight:700}
.dgm-gci-b p{margin:0;font-size:10px;color:#59636e;line-height:1.35}
.dgm-gci-b.accent{background:#e6f5e6;border-color:#a8d8a8}
.dgm-gci-b.accent h6{color:#0d5c0d}
.dgm-gci-b.blue{background:#ddf4ff;border-color:#b6e3ff}
.dgm-gci-b.blue h6{color:#0550ae}
.dgm-gci-b.green{background:#dafbe1;border-color:#aceebb}
.dgm-gci-b.green h6{color:#1a614f}
.dgm-gci-b.red{background:#ffebe9;border-color:#ffcecb}
.dgm-gci-b.red h6{color:#82061e}
.dgm-gci-b.neutral{background:#f6f8fa;border-color:#d1d9e0}
.dgm-gci-b.neutral h6{color:#1f2328}
@media (max-width:640px){.dgm-gci{padding:20px 16px 18px}.dgm-gci-branches{grid-template-columns:1fr}}
</style>
<div class="dgm-gci">
  <span class="dgm-gci-chip">The eval harness is the merge gate</span>
  <h4>A PR, push, or label triggers Actions, which runs Phase 15's eval harness</h4>
  <p class="dgm-gci-sub">Mergeable is a gate decision, not a suggestion — a failing gate blocks the merge.</p>
  <div class="dgm-gci-row">
    <div class="dgm-gci-n neutral">PR / push / label</div>
    <span class="dgm-gci-arr">→</span>
    <div class="dgm-gci-n accent">GitHub Actions</div>
    <span class="dgm-gci-arr">→</span>
    <div class="dgm-gci-n blue">Run eval harness (Phase 15)</div>
  </div>
  <div class="dgm-gci-q">Gate passes?</div>
  <div class="dgm-gci-branches">
    <div class="dgm-gci-b green">
      <h6>Yes</h6>
      <p>Mergeable</p>
    </div>
    <div class="dgm-gci-b red">
      <h6>No</h6>
      <p>Block</p>
    </div>
  </div>
</div>


## Build It

The artifact is a CI workflow. `outputs/evals.yml` runs the Phase 15 eval harness on PRs and
fails the build on regression:

```yaml
name: Harness Evals
on:
  pull_request:
  workflow_dispatch:
jobs:
  evals:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - name: Run eval gate
        run: python3 harness-engineering/phases/15-evals-and-testing-the-harness/06-eval-harness/code/eval_harness.py
```

The eval harness exits nonzero on a regression (Phase 15 L6). The job fails and the PR is
blocked. Evals become a required check, exactly like unit tests.

## Use It

For the GitHub side of an agent — opening PRs, reading issues, posting reviews — you use the
**GitHub MCP server** or the `gh` CLI. The agent's GitHub actions flow through MCP tools
(Phase 12). For triggering, a workflow on `issues`/`pull_request`/`label` events can dispatch
an agent run (for example, "Claude, fix this"). The discipline stays the same: agent *output*
still goes through review and the eval gate before it merges.

## Ship It

[`outputs/evals.yml`](../../02-github-ci/outputs/evals.yml) — a GitHub Actions workflow running
the eval gate on PRs.

## Check Yourself

**Q1.** Why run the eval harness in CI?

- A) for logs
- B) to block PRs that regress the harness, like a required test check
- C) to slow merges
- D) no reason

<details><summary>Answer</summary>B — evals as a required, blocking check.</details>

**Q2.** How does an agent perform GitHub actions (PRs, comments)?

- A) it can't
- B) via the GitHub MCP server or `gh` CLI (tools, Phase 12)
- C) by editing git internals
- D) email

<details><summary>Answer</summary>B — GitHub MCP / `gh` as tools.</details>

**Challenge.** Add a workflow that triggers on an issue labeled `agent`, runs the agent to
propose a fix on a branch, and opens a PR — leaving the eval gate + human review as the
guards before merge.

## Related

- Builds on: Phase 15 — [Eval harness](../../../15-evals-and-testing-the-harness/06-eval-harness/docs/en.md), Phase 12 — MCP
- Next: [Webhooks & event-driven agents](../../03-webhooks/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
