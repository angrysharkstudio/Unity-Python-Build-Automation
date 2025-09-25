@echo off
REM Unity Build Automation - Full WebGL Deployment
REM Executes pre-build hook, builds WebGL, and uploads to FTP
REM
REM MIT License - Copyright (c) 2025 Angry Shark Studio

cd /d "%~dp0\.."
echo.
echo ========================================
echo    Full WebGL Deployment Pipeline
echo ========================================
echo.
echo 1. Executing pre-build hook (if configured)
echo 2. Building WebGL
echo 3. Uploading to FTP (with overwrite)
echo.
echo ----------------------------------------
echo.

python build_cli.py webgl --upload

if errorlevel 1 (
    echo.
    echo Deployment failed! Check logs for details.
    pause
    exit /b 1
) else (
    echo.
    echo Deployment completed successfully!
    echo Check your FTP server for the uploaded build.
    pause
    exit /b 0
)