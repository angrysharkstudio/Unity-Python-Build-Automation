@echo off
REM Unity Build Automation - WebGL Hook and Build
REM Executes pre-build hook and builds WebGL (no upload)
REM
REM MIT License - Copyright (c) 2025 Angry Shark Studio

cd /d "%~dp0\.."
echo Building Unity project for WebGL with pre-build hook...
echo.

python build_cli.py webgl

if errorlevel 1 (
    echo.
    echo Build failed! Check logs for details.
    exit /b 1
) else (
    echo.
    echo Build completed successfully!
    echo Output in: Builds\WebGL\
    exit /b 0
)