# Usage: .\paste_from_clipboard.ps1 staging_round_0001
param(
  [string]$Round = "staging_round_0001"
)
$clip = Get-Clipboard
$python = "py"
if (-not (Get-Command $python -ErrorAction SilentlyContinue)) { $python = "python" }
$script = Join-Path $PSScriptRoot "paste_to_staging.py"
$clip | & $python $script --round $Round
