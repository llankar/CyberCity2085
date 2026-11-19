@echo off
REM CyberCity 2085 - Windows Game Launcher
REM Validates tactical systems before launching game

echo ============================================
echo   CyberCity 2085 - Tactical System Build
echo ============================================
echo.

REM Step 1: Quick test validation
echo [1/3] Running tactical system tests...
python -m pytest "d:\SynologyDrive\rpg\Python\Cybercity-2085\CyberCity2085\tests" --tb=no -q 2>&1 | findstr /C:"passed" /C:"failed"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Some tests failed. Continuing anyway...
)

echo.
echo [2/3] Starting Arcade game...
echo ============================================
echo.

REM Launch the game
python "d:\SynologyDrive\rpg\Python\Cybercity-2085\CyberCity2085\game\views.py"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Game exited normally.
) else (
    echo.
    echo Game encountered an error.
)

echo.
echo ============================================
echo   Build validation complete
echo ============================================
