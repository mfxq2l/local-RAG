@echo off
REM ============================================================
REM  Local RAG - interactive ask (retrieval + local LLM answer)
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

echo ============================================================
echo   Local RAG - Ask
echo ============================================================
echo   Type a question and press Enter. Type "exit" to quit.
echo ============================================================
echo.

:loop
set "Q="
set /p "Q=Q> "
if not defined Q goto loop
if /i "%Q%"=="exit" goto :eof
if /i "%Q%"=="quit" goto :eof

"%PY%" run.py ask "%Q%"
echo.
goto loop
