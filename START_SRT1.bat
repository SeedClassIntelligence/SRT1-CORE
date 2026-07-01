@echo off
setlocal
cd /d "%~dp0"
TITLE SRT-1 Core Launcher
color 0b
echo ========================================================
echo             SRT-1 Core Local Launcher
echo ========================================================
echo.

echo Starting SRT-1 Core Engine on http://127.0.0.1:7483 ...
start "SRT-1 Core Engine (7483)" cmd /k "python -m srt1_code_indexer.engine --repo_path . --port 7483"

echo Opening packaged SRT-1 dashboard on http://127.0.0.1:7483/dashboard ...
start "" "http://127.0.0.1:7483/dashboard"

echo.
echo ========================================================
echo SRT-1 Core started.
echo.
echo Dashboard:   http://127.0.0.1:7483/dashboard
echo Mobile PWA:  http://127.0.0.1:7483/mobile
echo Core API:    http://127.0.0.1:7483/status
echo ========================================================
echo.
pause
