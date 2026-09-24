---
name: agent-team-setup
description: One-shot prompt that generates a full agent harness — governance file, pipeline skill, workspace, hooks, reviewer prompt, and contract template.
kind: prompt
phase: 10
lesson: 01
---

# Fill in the bracketed fields, then send this to Claude Code

I want to set up an agent harness for my project.

Project context:
  Project type:    [e.g. React + FastAPI / Django monolith / Node service]
  Tech stack:      [e.g. TypeScript, Python, PostgreSQL]
  Team size:       [e.g. 4 engineers, 2 PMs]
  Primary concern: [consistency / cost control / security / speed]
  Domain:          [fintech / e-commerce / internal tooling / regulated]

Create these files:

1. CLAUDE.md — short governance file (~100 lines, not an encyclopedia)
   - Mode defaults: PM mode for ambiguous prompts, Eng mode requires explicit trigger
   - Approval gate: echo a 1-line contract before executing vague approvals
   - Phase boundary: stop and report after each phase, no auto-chaining
   - Dispatch rule: use the harness only if parallelising saves >45 minutes

2. .claude/skills/agent-team/SKILL.md — defines the pipeline:
   - Planning agent  — input: spec only. Output: sprint contract + 2-3 arch candidates
   - Discovery agent — input: contract + codebase. Output: codebase map + dep graph
   - Worker agents   — isolated git worktree per task, zero shared files per wave
   - Review agent    — input: diff only (not the plan). Output: ship or hold
   - Memory agent    — input: review report. Output: knowledge.md entries
   - Budget defaults: maxWorkers: 3, maxCallsPerWorker: 15, maxWaves: 2
   - Wave discipline: hard stop between waves, explicit "continue" to proceed

3. Directory structure:
   - _agent-team/cycles/       (per-sprint isolation, never overwrite)
   - _agent-team/knowledge.md  (system of record — append-only, evidence only)
   - .claude-workspace/        (per-task checkpoints: checkpoint.md, file-changes.md)

4. .claude/settings.json — hooks:
   - PostToolUse: run linter after every Edit or Write; inject violations as context
   - PreToolUse:  block .env edits

5. .claude/agents/reviewer.md — review agent prompt:
   - 7 dimensions: correctness, security, regression risk, type safety,
     test coverage, requirements traceability, [your domain rule]
   - Merge score: conflicts 30% + tests 25% + build 20% + blast 15% + spec 10%
   - Threshold: score <70 = blocked. Only two verdicts: ship or hold.

6. _agent-team/sprint-contract-template.json:
   - Fields: sprint_name, tasks[], budget{}, file_manifest[], acceptance_criteria[]

After setup, orient me:
   - How to start a sprint: /agent-team "what to build"
   - How to review arch candidates before workers dispatch
   - How to continue after a wave break: /agent-team continue
   - What to check before merging

# Smoke test: /agent-team "add a health-check route returning {status: ok}"
