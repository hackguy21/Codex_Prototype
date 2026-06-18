param(
    [switch]$SkipPipUpgrade,
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$venvPath = Join-Path $root ".venv"
$pythonPath = Join-Path $venvPath "Scripts\python.exe"
$requirementsPath = Join-Path $root "requirements.txt"

function Resolve-Python311 {
    $candidates = @()

    if ($env:PROJECT_PROTOTYPE_PYTHON) {
        $candidates += @{ Command = $env:PROJECT_PROTOTYPE_PYTHON; Args = @() }
    }

    $candidates += @(
        @{ Command = "python"; Args = @() },
        @{ Command = "python3"; Args = @() },
        @{ Command = "py"; Args = @("-3.11") }
    )

    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate.Command -ErrorAction SilentlyContinue
        if (-not $command) {
            continue
        }

        $versionCheck = @"
import sys
raise SystemExit(0 if sys.version_info >= (3, 11) else 1)
"@

        try {
            & $command.Source @($candidate.Args) -c $versionCheck
            if ($LASTEXITCODE -eq 0) {
                return @{ Path = $command.Source; Args = $candidate.Args }
            }
        } catch {
            continue
        }
    }

    throw "Python 3.11 or newer was not found. Install Python 3.11+ and rerun this script."
}

Set-Location $root

if (-not (Test-Path $pythonPath)) {
    $python = Resolve-Python311
    Write-Host "Creating virtual environment at $venvPath"
    & $python.Path @($python.Args) -m venv $venvPath
}

& $pythonPath -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
if ($LASTEXITCODE -ne 0) {
    throw "The virtual environment Python must be 3.11 or newer."
}

if (-not $SkipPipUpgrade) {
    & $pythonPath -m pip install --upgrade pip
}

if (-not $SkipInstall) {
    & $pythonPath -m pip install -r $requirementsPath
}

Write-Host "Virtual environment is ready."
Write-Host "Python: $pythonPath"
& $pythonPath --version
