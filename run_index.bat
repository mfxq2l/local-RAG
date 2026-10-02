@echo off
REM ============================================================
REM  Local RAG - build / rebuild the vector index
REM
REM  Rebuilds from scratch: clears the Qdrant collection and the
REM  BM25 index, re-chunks File\Markdown, re-embeds everything.
REM  Takes several minutes on first run (model load + 1700 chunks).
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

set REBUILD=%1
if "%REBUILD%"=="" set REBUILD=--rebuild

echo ============================================================
echo   Local RAG - building index (%REBUILD%)
echo ============================================================
echo.

"%PY%" run.py index %REBUILD%

echo.
echo Done.
pause
