param(
  [switch]$NoSetup
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "       DUAL AGENT - INSTALLER" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstallDir = Join-Path $HOME ".dual-agent"
$BinDir = Join-Path $HOME ".local\bin"
$CmdPath = Join-Path $BinDir "dual-agent.cmd"

# --- Python 3.9+ : on teste vraiment l'exécution (évite le faux "python" du Microsoft Store)
$PyExe = $null
$PyArgs = ""
$candidates = @(
  @{ Name = "python"; Args = @() },
  @{ Name = "py";     Args = @("-3") },
  @{ Name = "python3"; Args = @() }
)
foreach ($cand in $candidates) {
  $cmdInfo = Get-Command $cand.Name -ErrorAction SilentlyContinue
  if (-not $cmdInfo) { continue }
  try {
    $res = & $cmdInfo.Source @($cand.Args) -c "import sys; print(int(sys.version_info >= (3, 9)))" 2>$null
    if ("$res".Trim() -eq "1") {
      $PyExe = $cmdInfo.Source
      $PyArgs = ($cand.Args -join " ")
      break
    }
  } catch { }
}
if (-not $PyExe) {
  Write-Host "Python 3.9+ est introuvable." -ForegroundColor Red
  Write-Host "Installe-le depuis https://www.python.org/downloads/ (coche 'Add python.exe to PATH') puis relance."
  exit 1
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Host "Git est introuvable. Installe Git for Windows puis relance." -ForegroundColor Red
  exit 1
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

Copy-Item -Force (Join-Path $Here "dual_agent.py") (Join-Path $InstallDir "dual_agent.py")
# Nettoyage des anciennes versions (0.x)
Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $InstallDir "dual_agent_cli.py"), (Join-Path $InstallDir "orchestrator.py")

$line = '"' + $PyExe + '" ' + $PyArgs + ' "%USERPROFILE%\.dual-agent\dual_agent.py" %*'
$content = "@echo off`r`n" + $line + "`r`n"
Set-Content -Path $CmdPath -Value $content -Encoding ASCII

# Ajoute ~/.local/bin au PATH utilisateur si nécessaire
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $userPath) { $userPath = "" }
$parts = $userPath -split ";" | Where-Object { $_ }
if ($parts -notcontains $BinDir) {
  $newPath = if ($userPath.Trim()) { "$userPath;$BinDir" } else { $BinDir }
  [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
  Write-Host "Ajouté au PATH utilisateur : $BinDir" -ForegroundColor Green
}
if (($env:Path -split ";") -notcontains $BinDir) {
  $env:Path = "$env:Path;$BinDir"
}

Write-Host "Dual Agent installé." -ForegroundColor Green
Write-Host "Commande : dual-agent" -ForegroundColor Green
Write-Host ""

if (-not $NoSetup) {
  Write-Host "Démarrage de la connexion guidée..." -ForegroundColor Cyan
  & $CmdPath setup
  exit $LASTEXITCODE
}
Write-Host "Lance ensuite : dual-agent setup"
