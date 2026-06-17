# Run the ShopByFiber API locally. Usage: .\run.ps1 [-Port 8000]
param([int]$Port = 8000)

$root = $PSScriptRoot

pip install -q -r "$root\api\requirements.txt"
if (-not $?) { exit 1 }

Set-Location "$root\api"
python -m uvicorn app:app --port $Port
