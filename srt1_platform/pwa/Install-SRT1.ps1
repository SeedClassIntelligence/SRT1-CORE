<#
.SYNOPSIS
    SRT-1 Master Installer & Launcher

.DESCRIPTION
    This script downloads, installs, and launches SRT-1 (CORE or ENTERPRISE) on your system.
    It automatically handles:
    1. Git cloning the repository (if not already local)
    2. Creating a Python virtual environment
    3. Installing all required dependencies
    4. Registering global commands (srt1-index, srt1-bundle)
    5. Starting the SRT-1 Dashboard

.EXAMPLE
    .\Install-SRT1.ps1
    # Installs the public SRT1-CORE from GitHub and launches the dashboard.

.EXAMPLE
    .\Install-SRT1.ps1 -LocalPath "C:\Path\To\SRT1-ENTERPRISE"
    # Installs from a local private enterprise folder instead of downloading.
#>

param (
    [string]$RepoUrl = "https://github.com/SeedClassIntelligence/SRT1-CORE.git",
    [string]$LocalPath = "",
    [string]$InstallDir = "$HOME\SRT1-Workspace"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "      SRT-1 Cognitive Operating System Installer        " -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Prerequisites
Write-Host "[1/4] Checking prerequisites..." -ForegroundColor Yellow

if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    if ($LocalPath -eq "") {
        Write-Error "Git is not installed. Please install Git to download the repository, or provide a -LocalPath to an existing folder."
    }
}

if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.9+."
}

# 2. Download / Locate Code
Write-Host "[2/4] Locating SRT-1 Source Code..." -ForegroundColor Yellow

$TargetDir = ""
if ($LocalPath -ne "") {
    if (!(Test-Path $LocalPath)) {
        Write-Error "Local path provided does not exist: $LocalPath"
    }
    $TargetDir = $LocalPath
    Write-Host "      Using local repository at: $TargetDir" -ForegroundColor Green
} else {
    $TargetDir = "$InstallDir\SRT1-CORE"
    if (Test-Path $TargetDir) {
        Write-Host "      Repository already exists at $TargetDir. Pulling latest changes..." -ForegroundColor Green
        Set-Location $TargetDir
        git pull origin main
    } else {
        Write-Host "      Downloading SRT-1 from GitHub to $TargetDir..." -ForegroundColor Green
        New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
        Set-Location $InstallDir
        git clone $RepoUrl
    }
}

Set-Location $TargetDir

# 3. Setup Virtual Environment & Install
Write-Host "[3/4] Setting up Python Environment..." -ForegroundColor Yellow

$VenvPath = "$TargetDir\venv"
if (!(Test-Path $VenvPath)) {
    Write-Host "      Creating virtual environment..."
    python -m venv venv
}

Write-Host "      Activating virtual environment & installing..."
# Determine activation script path based on OS
$ActivateScript = ".\venv\Scripts\Activate.ps1"
if (!(Test-Path $ActivateScript)) {
    $ActivateScript = ".\venv\bin\Activate.ps1" # Fallback for some environments
}

# Run the installation inside the venv
& $ActivateScript
python -m pip install --upgrade pip
pip install -e .

Write-Host "      Global SRT-1 commands registered (srt1-index, srt1-execute)!" -ForegroundColor Green

# 4. Launch Instructions & Dashboard
Write-Host "[4/4] Installation Complete!" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " SRT-1 is now installed on your system! " -ForegroundColor White
Write-Host ""
Write-Host " HOW TO USE IT:" -ForegroundColor Yellow
Write-Host " 1. Open any coding project folder in your terminal."
Write-Host " 2. Activate the SRT-1 environment if not active:"
Write-Host "    $ActivateScript" -ForegroundColor DarkGray
Write-Host " 3. Run the indexer on that folder:"
Write-Host "    srt1-index --repo_path ./" -ForegroundColor Green
Write-Host ""
Write-Host " This will create a '.srt1' intelligence folder and start the dashboard."
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$response = Read-Host "Would you like to start the SRT-1 Master Launcher now? (Y/N)"
if ($response -match "^[yY]") {
    if (Test-Path "START_SRT1.bat") {
        Start-Process "START_SRT1.bat"
    } else {
        Write-Host "Could not find START_SRT1.bat in $TargetDir" -ForegroundColor Red
    }
}
