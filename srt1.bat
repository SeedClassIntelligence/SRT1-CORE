@echo off
setlocal
cd /d "%~dp0"
python -m srt1_code_indexer.engine %*
