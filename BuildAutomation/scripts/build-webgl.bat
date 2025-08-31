@echo off
REM Unity Build Automation - WebGL Build Script
REM Quick non-interactive build for WebGL platform
REM
REM MIT License - Copyright (c) 2025 Angry Shark Studio

cd /d "%~dp0\.."
echo Building Unity project for WebGL...
echo.

python build_cli.py webgl

if errorlevel 1 (
    echo.
    echo Build failed! Check logs for details.
    exit /b 1
) else (
    echo.
    echo Build completed successfully!
    exit /b 0
)