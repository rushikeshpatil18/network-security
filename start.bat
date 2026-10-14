@echo off
setlocal EnableDelayedExpansion

:: Set console title and working directory to this script's folder
title Classical Cryptography Toolkit
cd /d "%~dp0"

:: Detect Python executable (checks 'python', then 'py', then 'python3')
set "PY_CMD="
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PY_CMD=python"
) else (
    where py >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PY_CMD=py"
    ) else (
        where python3 >nul 2>&1
        if %ERRORLEVEL% equ 0 (
            set "PY_CMD=python3"
        )
    )
)

if "%PY_CMD%"=="" (
    echo ====================================================================
    echo [ERROR] Python was not detected on your system PATH!
    echo ====================================================================
    echo Please install Python 3.8 or higher from:
    echo   https://www.python.org/downloads/
    echo.
    echo Ensure you check the box: "Add python.exe to PATH" during installation.
    echo ====================================================================
    pause
    exit /b 1
)

:: Direct argument handling (non-interactive shortcuts)
if /i "%~1"=="--gui" (
    "%PY_CMD%" main.py --gui
    exit /b %ERRORLEVEL%
)
if /i "%~1"=="-g" (
    "%PY_CMD%" main.py --gui
    exit /b %ERRORLEVEL%
)
if /i "%~1"=="--cli" (
    "%PY_CMD%" main.py
    exit /b %ERRORLEVEL%
)
if /i "%~1"=="-c" (
    "%PY_CMD%" main.py
    exit /b %ERRORLEVEL%
)
if /i "%~1"=="--test" (
    "%PY_CMD%" -m unittest discover -s tests -p "test_*.py" -v
    exit /b %ERRORLEVEL%
)
if /i "%~1"=="-t" (
    "%PY_CMD%" -m unittest discover -s tests -p "test_*.py" -v
    exit /b %ERRORLEVEL%
)

:MENU
cls
echo ====================================================================
echo                   CLASSICAL CRYPTOGRAPHY TOOLKIT
echo             Network Security Project - Pure Python 3
echo ====================================================================
echo.
echo   [1] Launch Graphical User Interface (GUI Dashboard)
echo   [2] Launch Interactive Command-Line Interface (CLI Menu)
echo   [3] Run Automated Unit Tests (17 Test Cases)
echo   [4] View Project User Manual
echo   [5] Exit
echo.
echo ====================================================================
set "CHOICE="
set /p "CHOICE=Enter your choice (1-5) [Default: 1]: "

if "%CHOICE%"=="" set "CHOICE=1"
if "%CHOICE%"=="1" goto LAUNCH_GUI
if "%CHOICE%"=="2" goto LAUNCH_CLI
if "%CHOICE%"=="3" goto RUN_TESTS
if "%CHOICE%"=="4" goto VIEW_MANUAL
if "%CHOICE%"=="5" goto EXIT_SCRIPT

echo.
echo [ERROR] Invalid choice '%CHOICE%'. Please choose 1, 2, 3, 4, or 5.
timeout /t 2 >nul
goto MENU

:LAUNCH_GUI
cls
echo ====================================================================
echo Starting Classical Cryptography Toolkit GUI Dashboard...
echo ====================================================================
"%PY_CMD%" main.py --gui
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] An error occurred while launching the GUI.
    pause
)
goto MENU

:LAUNCH_CLI
cls
"%PY_CMD%" main.py
echo.
echo CLI session ended.
pause
goto MENU

:RUN_TESTS
cls
echo ====================================================================
echo Running Automated Unit Tests...
echo ====================================================================
echo.
"%PY_CMD%" -m unittest discover -s tests -p "test_*.py" -v
echo.
echo ====================================================================
pause
goto MENU

:VIEW_MANUAL
cls
if exist "user_manual.md" (
    echo ====================================================================
    echo PROJECT USER MANUAL (user_manual.md)
    echo ====================================================================
    type user_manual.md
) else (
    echo [WARNING] user_manual.md not found.
)
echo.
pause
goto MENU

:EXIT_SCRIPT
echo.
echo Exiting Classical Cryptography Toolkit. Goodbye!
exit /b 0
