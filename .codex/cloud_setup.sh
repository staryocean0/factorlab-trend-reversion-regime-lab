#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m venv .venv
.venv/bin/python -m pip install -e '.[maintenance]'
.venv/bin/python scripts/repository_consistency.py --check
.venv/bin/python -m pytest -q tests/test_repository_consistency.py
# Full retained-data regression is explicit; setup never starts a historical fit.
if [[ "${RUN_FULL_REGRESSION:-0}" == 1 ]]; then
  .venv/bin/python -m pytest -q
fi
