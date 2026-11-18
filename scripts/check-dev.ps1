$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    $failed = $false
    $checks = @(
        @{ Name = 'Python 3.13 and FastAPI'; Run = { & '.\.venv\Scripts\python.exe' -c 'import sys, fastapi; assert sys.version_info[:2] == (3,13); print(sys.version.split()[0], "FastAPI", fastapi.__version__)' } },
        @{ Name = 'Node.js'; Run = { node --version } },
        @{ Name = 'npm'; Run = {
            $nodeDir = Split-Path -Parent (Get-Command node -ErrorAction Stop).Source
            $npmCli = Join-Path $nodeDir 'node_modules\npm\bin\npm-cli.js'
            if (Test-Path -LiteralPath $npmCli) { node $npmCli --version }
            else { npm.cmd --version }
        } },
        @{ Name = 'VS Code'; Run = {
            if (-not (Get-Command code -ErrorAction SilentlyContinue)) { throw 'VS Code is not on PATH.' }
            Write-Host 'VS Code launcher found.'
        } },
        @{ Name = 'Git'; Run = { git --version } },
        @{ Name = 'Docker Compose'; Run = { docker compose version } },
        @{ Name = 'PostgreSQL'; Run = { docker compose exec -T postgres sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' } },
        @{ Name = 'Redis'; Run = { docker compose exec -T redis redis-cli ping } }
    )
    foreach ($check in $checks) {
        Write-Host "Checking $($check.Name)..."
        try {
            $global:LASTEXITCODE = 0
            & $check.Run
            if ($LASTEXITCODE -ne 0) { throw "Exit code $LASTEXITCODE" }
        } catch { Write-Warning "$($check.Name): $_"; $failed = $true }
    }
    if ($failed) { throw 'One or more development environment checks failed.' }
} finally { Pop-Location }
