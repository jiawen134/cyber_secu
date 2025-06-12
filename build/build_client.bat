@echo off
echo Building RAT Client Executable...
echo.

REM Check if virtual environment exists
if not exist "..\venv" (
    echo Error: Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call ..\venv\Scripts\activate.bat

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Build the executable
echo Building client.exe...
pyinstaller client.spec

REM Check if build was successful
if exist "dist\client.exe" (
    echo.
    echo Build successful! Client executable created at: dist\client.exe
    echo File size:
    dir dist\client.exe | findstr client.exe
) else (
    echo.
    echo Build failed! Check the output above for errors.
)

echo.
pause 