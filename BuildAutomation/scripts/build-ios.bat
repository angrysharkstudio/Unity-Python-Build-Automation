@echo off
REM Unity Build Automation - iOS Build Script
REM Quick non-interactive build for iOS platform (macOS only)
REM
REM MIT License - Copyright (c) 2025 Angry Shark Studio

cd /d "%~dp0\.."
echo Building Unity project for iOS...
echo Note: iOS builds require macOS and create Xcode projects
echo.

python build_cli.py ios

if errorlevel 1 (
    echo.
    echo Build failed! Check logs for details.
    exit /b 1
) else (
    echo.
    echo Build completed successfully!
    echo Open the Xcode project to build final iOS app.
    exit /b 0
)