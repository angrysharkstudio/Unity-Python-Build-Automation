@echo off
REM Unity Build Automation - macOS Build Script
REM Quick non-interactive build for macOS platform
REM
REM MIT License - Copyright (c) 2025 Angry Shark Studio

cd /d "%~dp0\.."
echo Building Unity project for macOS...
echo.

python build_cli.py mac

if errorlevel 1 (
    echo.
    echo Build failed! Check logs for details.
    exit /b 1
) else (
    echo.
    echo Build completed successfully!
    exit /b 0
)