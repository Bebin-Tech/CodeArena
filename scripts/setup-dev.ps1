[CmdletBinding()]
param([switch]$StartServices)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    if (-not (Test-Path -LiteralPath '.env')) {
        $bytes = New-Object byte[] 32
        $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
        $password = -join ($bytes | ForEach-Object { $_.ToString('x2') })
        $content = (Get-Content -LiteralPath '.env.example' -Raw).Replace('POSTGRES_PASSWORD=', "POSTGRES_PASSWORD=$password")
        Set-Content -LiteralPath '.env' -Value $content -Encoding ascii
        Write-Host 'Created .env with a random local database password.'
    }
    $python = Get-Command python -ErrorAction SilentlyContinue
    $localPython = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python313\python.exe'
    if (Test-Path -LiteralPath $localPython) { $pythonExe = $localPython }
    elseif ($python) { $pythonExe = $python.Source }
    else { throw 'Install Python 3.13, then rerun this script.' }
    & $pythonExe -c 'import sys; assert sys.version_info[:2] == (3, 13), "Python 3.13 is required"'
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.13 is unavailable.' }
    if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
        & $pythonExe -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
    }
    $requirements = 'requirements-dev.txt'
    if (Test-Path -LiteralPath 'requirements-dev.lock.txt') { $requirements = 'requirements-dev.lock.txt' }
    & '.\.venv\Scripts\python.exe' -m pip install -r $requirements
    if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed.' }
    if ($StartServices) {
        docker compose up -d --wait
        if ($LASTEXITCODE -ne 0) { throw 'Services failed to start. Check Docker Desktop is running Linux containers.' }
    }
    Write-Host 'Development environment initialized. Run scripts/check-dev.ps1 to verify.'
} finally { Pop-Location }
