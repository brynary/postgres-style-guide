#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> validator tests"
python3 "$ROOT/checks/test_validate.py"

echo "==> skill structure, links, routing, and code fences"
python3 "$ROOT/checks/validate.py" "$ROOT"

echo "==> mdBook build"
mdbook build "$ROOT"

echo "All checks passed."
