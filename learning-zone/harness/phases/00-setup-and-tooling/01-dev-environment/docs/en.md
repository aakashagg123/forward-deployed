# Dev environment & the SDK

> **Motto** — Before you build a harness, make a clean room to build it in.

*Part of Phase 00 — Setup & Tooling.*

## The Problem

A harness is code that calls a model and runs tools on your machine. Your Python version
can drift, your dependencies can leak between projects, or your API key can end up in
shell history. Any of these mistakes carries into every later lesson. Five minutes of
setup now saves hours of "works on my machine" later.

## The Concept

You need exactly four things: a recent **Python** (3.10+), an isolated **virtualenv**,
the **Anthropic SDK**, and an **API key in the environment** (never in code). That's the
whole floor.

```
python3 -m venv .venv     →  isolated interpreter
source .venv/bin/activate →  this shell uses it
pip install anthropic     →  the SDK
export ANTHROPIC_API_KEY  →  the key, in env not code
```

## Build It

`outputs/setup.sh` does it idempotently and verifies the install:

```bash
#!/usr/bin/env bash
set -euo pipefail
python3 -c 'import sys; assert sys.version_info >= (3,10), "need Python 3.10+"'
[ -d .venv ] || python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --quiet --upgrade pip anthropic
python3 - <<'PY'
import anthropic, os
print("anthropic", anthropic.__version__)
print("key set:", bool(os.getenv("ANTHROPIC_API_KEY")))
PY
```

Run `bash outputs/setup.sh`. It's safe to re-run: the venv is created once and deps are
upgraded each time. The check at the end tells you whether your key is visible.

## Use It

Every later lesson assumes this environment: `source .venv/bin/activate`, key in
`ANTHROPIC_API_KEY`. The Use-It code throughout the course defaults to the latest model,
**Claude Opus 5** (`claude-opus-5`).

## Ship It

[`outputs/setup.sh`](../../01-dev-environment/outputs/setup.sh) — an idempotent environment
bootstrap you can drop into any harness repo.

## Check Yourself

**Q1.** Why a virtualenv per project?

- A) it's faster
- B) it isolates dependencies so one project can't break another
- C) the SDK requires it
- D) to save disk

<details><summary>Answer</summary>B — isolation prevents version conflicts across
projects.</details>

**Q2.** Where does the API key belong?

- A) hardcoded in the script
- B) in an environment variable, never in code
- C) in the README
- D) in git

<details><summary>Answer</summary>B — secrets live in the environment (next lessons make
this enforceable).</details>

**Challenge.** Extend `setup.sh` to write a `.python-version` and fail with a clear
message if `ANTHROPIC_API_KEY` is unset.

## Related

- Next: [Your first raw model call](../../02-first-raw-call/docs/en.md)
- [Roadmap](../../../../ROADMAP.md)
