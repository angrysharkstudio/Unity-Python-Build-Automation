@echo off
REM Unity Build Automation - Android Build Script
REM Quick non-interactive build for Android platform
REM
REM MIT License - Copyright (c) 2025 Angry Shark Studio

cd /d "%~dp0\.."
echo Building Unity project for Android...
echo.

python build_cli.py android

if errorlevel 1 (
    echo.
    echo Build failed! Check logs for details.
    exit /b 1
) else (
    echo.
    echo Build completed successfully!
    exit /b 0
)