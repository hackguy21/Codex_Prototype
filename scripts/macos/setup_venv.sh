#!/usr/bin/env bash
set -euo pipefail

skip_pip_upgrade=0
skip_install=0

for arg in "$@"; do
  case "$arg" in
    --skip-pip-upgrade)
      skip_pip_upgrade=1
      ;;
    --skip-install)
      skip_install=1
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 2
      ;;
  esac
done

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$script_dir/../.." && pwd)"
venv_path="$root/.venv"
python_path="$venv_path/bin/python"
requirements_path="$root/requirements.txt"

resolve_python311() {
  local candidates=()

  if [[ -n "${PROJECT_PROTOTYPE_PYTHON:-}" ]]; then
    candidates+=("$PROJECT_PROTOTYPE_PYTHON")
  fi

  candidates+=("python3.12" "python3.11" "python3" "python")

  for candidate in "${candidates[@]}"; do
    if ! command -v "$candidate" >/dev/null 2>&1; then
      continue
    fi

    if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'; then
      command -v "$candidate"
      return 0
    fi
  done

  echo "Python 3.11 or newer was not found. Install Python 3.11+ and rerun this script." >&2
  return 1
}

cd "$root"

if [[ ! -x "$python_path" ]]; then
  python_bin="$(resolve_python311)"
  echo "Creating virtual environment at $venv_path"
  "$python_bin" -m venv "$venv_path"
fi

"$python_path" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)'

if [[ "$skip_pip_upgrade" -eq 0 ]]; then
  "$python_path" -m pip install --upgrade pip
fi

if [[ "$skip_install" -eq 0 ]]; then
  "$python_path" -m pip install -r "$requirements_path"
fi

echo "Virtual environment is ready."
echo "Python: $python_path"
"$python_path" --version
