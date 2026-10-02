@echo off
REM ============================================================
REM  Local RAG - environment self check + unit tests
REM ============================================================
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set PY=%~dp0runtime\python3.12\python.exe

if not exist "%PY%" (
    echo [ERROR] python.exe not found: %PY%
    pause
    exit /b 1
)

echo.
"%PY%" run.py check
echo.
"%PY%" run.py test
echo.
pause
