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

echo Starting packaged SRT-1 dashboard on http://127.0.0.1:8080 ...
start "SRT-1 Dashboard (8080)" cmd /k "pushd ""%~dp0srt1_platform\pwa"" && python -m http.server 8080"

echo.
echo ========================================================
echo SRT-1 Core started.
echo.
echo Dashboard:   http://127.0.0.1:8080/dashboard.html
echo Mobile PWA:  http://127.0.0.1:8080/mobile.html
echo Core API:    http://127.0.0.1:7483/status
echo ========================================================
echo.
pause
