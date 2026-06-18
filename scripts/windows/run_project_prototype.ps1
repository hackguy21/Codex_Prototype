$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
Set-Location $root

if (Test-Path $venvPython) {
    & $venvPython .\backend\server.py
} else {
    python .\backend\server.py
}
