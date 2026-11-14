@echo off
REM CyberCity 2085 - Godot Combat UI Launcher
REM This launches the Godot combat mission UI in a standalone window

setlocal enabledelayedexpansion

REM Check if Godot is installed, try common locations
set GODOT_PATH=
set GODOT_CMD="godot"

REM Try to find godot.exe in PATH or common installation directories
for %%G in ("godot" "C:\Program Files\Godot*\" "C:\Program Files (x86)\Godot*\" "D:\Godot*" "E:\Godot*\") do (
    if exist "%%~$PATH:G\godot.exe" set GODOT_PATH="%%~$PATH:G"
)

if "!GODOT_PATH!"=="" (
    echo [ERROR] Godot not found! Please install Godot 4.2+ from https://godotengine.org/
    echo Installing Godot will add "godot" command to your PATH automatically.
    pause
    exit /b 1
)

echo Starting CyberCity 2085 Combat UI...
echo Working directory: %~dp0

REM Launch Godot with the combat missions UI project
"!GODOT_CMD!" --path "%~dp0godot\combat_missions_ui" --quit=false
pause
