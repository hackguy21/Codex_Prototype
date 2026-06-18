#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$script_dir/../.." && pwd)"
python_path="$root/.venv/bin/python"

cd "$root"

if [[ -x "$python_path" ]]; then
  exec "$python_path" "$root/backend/server.py"
fi

exec python3 "$root/backend/server.py"
