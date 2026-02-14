$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptRoot

$venvActivate = Join-Path $scriptRoot "env\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    . $venvActivate
} else {
    Write-Host "No se encontro el entorno virtual en env\\Scripts\\Activate.ps1" -ForegroundColor Yellow
}

python .\QRStudio.py @Args
