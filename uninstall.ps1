param(
  [switch]$Purge
)

$ErrorActionPreference = "Stop"
$InstallDir = Join-Path $HOME ".dual-agent"
$BinDir = Join-Path $HOME ".local\bin"
$CmdPath = Join-Path $BinDir "dual-agent.cmd"

Remove-Item -Force -ErrorAction SilentlyContinue $CmdPath
Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $InstallDir "dual_agent.py"), (Join-Path $InstallDir "dual_agent_cli.py"), (Join-Path $InstallDir "orchestrator.py")

if ($Purge) {
  if (Test-Path $InstallDir) { Remove-Item -Recurse -Force $InstallDir }
  Write-Host "Dual Agent supprimé, rapports compris." -ForegroundColor Green
} else {
  Write-Host "Dual Agent supprimé. Rapports conservés dans $InstallDir\runs (utilise -Purge pour les effacer)." -ForegroundColor Green
}
Write-Host "Les connexions Claude/Codex n'ont pas été supprimées."
Write-Host "Les branches dual-agent/* de tes dépôts restent : utilise 'dual-agent clean' avant de désinstaller si besoin."
