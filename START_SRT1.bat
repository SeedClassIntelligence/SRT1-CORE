@echo off
TITLE SRT-1 Master Launcher
color 0b
echo ========================================================
echo         SRT-1 Development Environment Launcher
echo ========================================================
echo.

echo Starting Real-Time Development Indexer (Port 7483)...
start cmd /k "TITLE SRT-1 Developer Indexer && python srt1_code_indexer\engine.py --repo_path ./"

echo Starting Consumer Auth/DB API Backend (Port 8000)...
start cmd /k "TITLE SRT-1 Cloud API Backend (8000) && python -m srt1_backend.server"

echo Starting Local Dashboards ^& Marketing Site (Port 8080)...
cd "seed-reflection"
start cmd /k "TITLE SRT-1 Websites (8080) && python -m http.server 8080"

echo.
echo ========================================================
echo SUCCESS! All three background services launched.
echo.
echo Marketing / UI: http://localhost:8080/home.html
echo SaaS Backend:   http://localhost:8000/api/v1
echo Core Engine:    http://localhost:7483/dashboard.html
echo ========================================================
echo.
pause
