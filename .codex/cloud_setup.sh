#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python scripts/validate_seed.py
.venv/bin/python -m pytest -q
