<#
.SYNOPSIS
    SRT-1 Core installer and local launcher.

.DESCRIPTION
    Installs SRT-1 Core into a local Python virtual environment.
    If this script is run from an existing SRT1-CORE checkout, that checkout is
    used directly. Otherwise it clones the public Core repository.

.EXAMPLE
    .\Install-SRT1.ps1
    # Install from the current checkout when available, otherwise clone Core.

.EXAMPLE
    .\Install-SRT1.ps1 -LocalPath "C:\Path\To\SRT1-CORE" -Start
    # Install an existing Core checkout and launch the local engine/dashboard.
#>

param (
    [string]$RepoUrl = "https://github.com/SeedClassIntelligence/SRT1-CORE.git",
    [string]$LocalPath = "",
    [string]$InstallDir = "$HOME\SRT1-Workspace",
    [switch]$Start
)

$ErrorActionPreference = "Stop"

function Resolve-Srt1Root {
    if ($LocalPath -ne "") {
        if (!(Test-Path $LocalPath)) {
            Write-Error "Local path does not exist: $LocalPath"
        }
        return (Resolve-Path $LocalPath).Path
    }

    if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "pyproject.toml"))) {
        return $PSScriptRoot
    }

    $target = Join-Path $InstallDir "SRT1-CORE"
    if (Test-Path $target) {
        return (Resolve-Path $target).Path
    }

    if (!(Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Error "Git is required to clone SRT1-CORE. Install Git or pass -LocalPath."
    }

    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
    Set-Location $InstallDir
    git clone $RepoUrl
    return (Resolve-Path $target).Path
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "              SRT-1 Core Installer" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH. Install Python 3.9+."
}

$TargetDir = Resolve-Srt1Root
Set-Location $TargetDir

Write-Host "[1/3] Using SRT-1 Core at: $TargetDir" -ForegroundColor Yellow

$VenvPath = Join-Path $TargetDir "venv"
if (!(Test-Path $VenvPath)) {
    Write-Host "[2/3] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host "[2/3] Reusing existing virtual environment..." -ForegroundColor Yellow
}

$ActivateScript = Join-Path $TargetDir "venv\Scripts\Activate.ps1"
if (!(Test-Path $ActivateScript)) {
    $ActivateScript = Join-Path $TargetDir "venv\bin\Activate.ps1"
}
if (!(Test-Path $ActivateScript)) {
    Write-Error "Could not find virtual environment activation script."
}

Write-Host "[3/3] Installing SRT-1 Core..." -ForegroundColor Yellow
& $ActivateScript
python -m pip install --upgrade pip
pip install -e .

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " SRT-1 Core is installed." -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Common commands:" -ForegroundColor Yellow
Write-Host "  srt1-index --repo_path . --port 7483" -ForegroundColor Green
Write-Host "  srt1-mcp" -ForegroundColor Green
Write-Host ""
Write-Host "Local launcher:" -ForegroundColor Yellow
Write-Host "  .\START_SRT1.bat" -ForegroundColor Green
Write-Host ""

if ($Start) {
    if (Test-Path (Join-Path $TargetDir "START_SRT1.bat")) {
        Start-Process (Join-Path $TargetDir "START_SRT1.bat")
    } else {
        Write-Host "START_SRT1.bat was not found in $TargetDir" -ForegroundColor Red
    }
}
