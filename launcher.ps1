# ChannelPulse AI Launcher
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================"
Write-Host "  ChannelPulse AI - Launcher"
Write-Host "========================================"

$venv = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (-not (Test-Path $venv)) {
    python -m venv .venv
}
& $venv

pip install -q -r requirements.txt

if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
}

$env:COMPANY_AUTONOMOUS = "1"
$env:COMPANY_MOCK = "1"

$url = "http://127.0.0.1:8765"
Write-Host "`nPanel: $url`n"
Start-Process $url

python -m uvicorn dashboard.app:app --host 127.0.0.1 --port 8765
