@echo off
REM Unity Build Automation - Build All Platforms Script
REM Quick non-interactive build for all available platforms
REM
REM MIT License - Copyright (c) 2025 Angry Shark Studio

cd /d "%~dp0\.."
echo Building Unity project for all platforms...
echo.

python build_cli.py --all

if errorlevel 1 (
    echo.
    echo Build failed! Check logs for details.
    exit /b 1
) else (
    echo.
    echo Build completed successfully!
    exit /b 0
)