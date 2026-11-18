$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root 'frontend')
$npmCli = Join-Path (Split-Path (Get-Command node).Source) 'node_modules\npm\bin\npm-cli.js'
node $npmCli run dev
