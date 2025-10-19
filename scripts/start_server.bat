@echo off
REM Start MetricDuck MCP Server for local development on Windows
setlocal

echo MetricDuck MCP Server - Starting...

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

echo Project Root: %PROJECT_ROOT%

REM Check if virtual environment exists
if not exist "%PROJECT_ROOT%\venv" (
    echo ERROR: Virtual environment not found
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate
    echo Then: pip install -e .
    exit /b 1
)

REM Activate virtual environment
call "%PROJECT_ROOT%\venv\Scripts\activate.bat"

REM Load environment variables if .env exists
if exist "%PROJECT_ROOT%\.env" (
    echo Loading environment variables from .env
    for /f "usebackq tokens=*" %%a in ("%PROJECT_ROOT%\.env") do set %%a
) else (
    echo WARNING: No .env file found. Using default configuration.
    echo Copy .env.example to .env and configure API URL and key.
)

REM Start MCP server
echo Starting MCP server...
cd "%PROJECT_ROOT%"
python -m metricduck_mcp
