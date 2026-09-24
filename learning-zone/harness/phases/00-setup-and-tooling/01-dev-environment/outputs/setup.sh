#!/usr/bin/env bash
# Idempotent harness dev-environment bootstrap. Safe to re-run.
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
