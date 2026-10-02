@echo off
REM ============================================================
REM  Local RAG - start web server (http://127.0.0.1:8000/ui)
REM
REM  NOTE: this project ships an *embedded* Python whose
REM  python312._pth fixes sys.path, so `python -m src.server`
REM  and PYTHONPATH both FAIL. Everything must go through run.py.
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

if not exist "%~dp0runtime\llama.cpp\llama-server.exe" (
    echo [WARN] llama-server.exe not found under runtime\llama.cpp
    echo        embedding will fail until it is restored.
    echo.
)

echo ============================================================
echo   Local RAG WebUI
echo ============================================================
echo   Web UI   : http://127.0.0.1:8000/ui
echo   API Docs : http://127.0.0.1:8000/docs
echo.
echo   First run may take a while: the embedding model and the
echo   chat model are loaded lazily on first use.
echo ============================================================
echo.

"%PY%" run.py serve

echo.
echo Server stopped.
pause
