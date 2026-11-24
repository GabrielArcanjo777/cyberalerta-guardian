#!/usr/bin/env bash
# Mesma verificação dos jobs "backend" e "frontend" do CI.
set -euo pipefail
raiz="$(cd "$(dirname "$0")/../../../.." && pwd)"

echo "== backend: ruff"
(cd "$raiz/backend" && python -m ruff check .)
echo "== backend: pytest"
(cd "$raiz/backend" && python -m pytest app/tests -q)
echo "== frontend: tsc"
(cd "$raiz/frontend" && npx tsc --noEmit)
echo "== frontend: eslint"
(cd "$raiz/frontend" && npm run lint)

echo "OK: tudo verde"
