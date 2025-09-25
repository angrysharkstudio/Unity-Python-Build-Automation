@echo off
REM Unity Build Automation - WebGL Build and Upload
REM Builds WebGL and uploads to FTP (no pre-build hook)
REM
REM MIT License - Copyright (c) 2025 Angry Shark Studio

cd /d "%~dp0\.."
echo Building Unity project for WebGL and uploading to FTP...
echo.

python build_cli.py webgl --upload --no-hook

if errorlevel 1 (
    echo.
    echo Build or upload failed! Check logs for details.
    exit /b 1
) else (
    echo.
    echo Build and upload completed successfully!
    exit /b 0
)