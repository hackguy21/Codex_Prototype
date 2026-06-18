#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$script_dir/../.." && pwd)"
setup_script="$script_dir/setup_venv.sh"
python_path="$root/.venv/bin/python"
url="http://127.0.0.1:${PORT:-8000}"

cd "$root"

if [[ ! -x "$python_path" ]]; then
  "$setup_script"
fi

echo "Project Prototype running at $url"
echo "Close this Terminal window or press Ctrl+C to stop the server."

(sleep 1; open "$url" >/dev/null 2>&1 || true) &
exec "$python_path" "$root/backend/server.py"
