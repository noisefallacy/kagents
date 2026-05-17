param(
    [string]$PythonExe = "C:\Users\kagin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
)

$ErrorActionPreference = "Stop"
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"

function Update-VenvActivationPaths {
    param(
        [string]$VenvPath
    )

    $activatePath = Join-Path $VenvPath "Scripts\activate"
    $activatePs1Path = Join-Path $VenvPath "Scripts\Activate.ps1"
    $activateBatPath = Join-Path $VenvPath "Scripts\activate.bat"

    if (Test-Path $activatePath) {
        $content = Get-Content $activatePath -Raw
        $content = [regex]::Replace(
            $content,
            "VIRTUAL_ENV=\$\(cygpath '.*?'\)",
            "VIRTUAL_ENV=`$(cygpath '$VenvPath')"
        )
        $content = [regex]::Replace(
            $content,
            "export VIRTUAL_ENV='.*?'",
            "export VIRTUAL_ENV='$VenvPath'"
        )
        Set-Content $activatePath $content -NoNewline
    }

    if (Test-Path $activatePs1Path) {
        $content = Get-Content $activatePs1Path -Raw
        $content = [regex]::Replace(
            $content,
            '\$env:VIRTUAL_ENV = ".*?"',
            '$env:VIRTUAL_ENV = "' + $VenvPath + '"'
        )
        Set-Content $activatePs1Path $content -NoNewline
    }

    if (Test-Path $activateBatPath) {
        $content = Get-Content $activateBatPath -Raw
        $content = [regex]::Replace(
            $content,
            'set "VIRTUAL_ENV=.*?"',
            'set "VIRTUAL_ENV=' + $VenvPath + '"'
        )
        Set-Content $activateBatPath $content -NoNewline
    }
}

if (-not (Test-Path $PythonExe)) {
    throw "Python executable not found at $PythonExe"
}

Write-Host "Using Python: $PythonExe"

if (-not (Test-Path ".venv")) {
    & $PythonExe -m venv .venv
}

$VenvPython = Join-Path $PWD ".venv\Scripts\python.exe"
$VenvPath = (Resolve-Path ".venv").ProviderPath

Update-VenvActivationPaths -VenvPath $VenvPath

& $VenvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "Failed to upgrade pip."
}

& $VenvPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install requirements."
}

& $VenvPython -m pip install -e . --no-build-isolation
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install the local project package."
}

Write-Host ""
Write-Host "Virtual environment ready."
Write-Host "Activate with:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
