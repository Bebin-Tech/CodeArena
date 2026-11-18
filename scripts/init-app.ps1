$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    if (-not (Test-Path '.env')) { throw 'Run scripts/setup-dev.ps1 first.' }
    $content = Get-Content '.env' -Raw
    if ($content -notmatch '(?m)^SECRET_KEY=.+') {
        $bytes = New-Object byte[] 48
        $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
        $secret = -join ($bytes | ForEach-Object { $_.ToString('x2') })
        if ($content -match '(?m)^SECRET_KEY=') { $content = $content -replace '(?m)^SECRET_KEY=.*', "SECRET_KEY=$secret" }
        else { $content += "`nSECRET_KEY=$secret`n" }
        Set-Content '.env' $content -Encoding ascii
        Write-Host 'Generated the application signing key.'
    }
    & '.\.venv\Scripts\python.exe' -m pip install -r backend/requirements.lock.txt
    if ($LASTEXITCODE -ne 0) { throw 'Backend installation failed.' }
    $npmCli = Join-Path (Split-Path (Get-Command node).Source) 'node_modules\npm\bin\npm-cli.js'
    node $npmCli ci --prefix frontend
    if ($LASTEXITCODE -ne 0) { throw 'Frontend installation failed.' }
    docker compose up -d --wait
    if ($LASTEXITCODE -ne 0) { throw 'Dependencies failed to start.' }
    & '.\.venv\Scripts\python.exe' -m alembic -c backend/alembic.ini upgrade head
    if ($LASTEXITCODE -ne 0) { throw 'Migration failed.' }
} finally { Pop-Location }
