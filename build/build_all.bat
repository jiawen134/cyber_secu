@echo off
echo Building All RAT Components...
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

echo.
echo ========================================
echo Building Server (server.exe)...
echo ========================================
pyinstaller server.spec

echo.
echo ========================================
echo Building Operator (rat_operator.exe)...
echo ========================================
pyinstaller operator.spec

echo.
echo ========================================
echo Building Client (client.exe)...
echo ========================================
pyinstaller client.spec

echo.
echo ========================================
echo Build Summary
echo ========================================

REM Check build results
if exist "dist\server.exe" (
    echo [+] Server.exe: SUCCESS
    dir dist\server.exe | findstr server.exe
) else (
    echo [-] Server.exe: FAILED
)

if exist "dist\rat_operator.exe" (
    echo [+] Rat_operator.exe: SUCCESS
    dir dist\rat_operator.exe | findstr rat_operator.exe
) else (
    echo [-] Rat_operator.exe: FAILED
)

if exist "dist\client.exe" (
    echo [+] Client.exe: SUCCESS
    dir dist\client.exe | findstr client.exe
) else (
    echo [-] Client.exe: FAILED
)

echo.
echo All executables are in the 'dist' folder.
echo.
pause 