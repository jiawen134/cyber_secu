@echo off
echo Setting up RAT Demo Environment...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10+ and try again
    pause
    exit /b 1
)

REM Check if uv is available
where uv >nul 2>&1
if errorlevel 1 (
    echo uv not found, using pip instead
    set USE_UV=false
) else (
    echo Found uv, using it for faster package installation
    set USE_UV=true
)

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
if "%USE_UV%"=="true" (
    uv pip install -r requirements.txt
) else (
    pip install -r requirements.txt
)

echo.
echo Setup complete!
echo.
echo To run the RAT demo:
echo 1. Start C2 Server: python server/server.py
echo 2. Start Operator CLI: python operator/operator.py
echo 3. Start Client: python client/client.py
echo 4. Build Client EXE: cd build && build_client.bat
echo.
pause 