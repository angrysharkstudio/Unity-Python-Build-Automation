@echo off
REM Unity Build Automation - WebGL Upload Only
REM Uploads existing WebGL build to FTP (no building)
REM
REM MIT License - Copyright (c) 2025 Angry Shark Studio

cd /d "%~dp0\.."
echo Uploading existing WebGL build to FTP...
echo.

python build_cli.py --upload-only

if errorlevel 1 (
    echo.
    echo Upload failed! Check logs for details.
    exit /b 1
) else (
    echo.
    echo Upload completed successfully!
    exit /b 0
)