@echo off
REM Build Windows and upload to Google Drive
REM This script builds for Windows platform and uploads the result to Google Drive

echo Unity Build Automation - Windows Build with Google Drive Upload
echo ============================================================
echo.

cd /d "%~dp0\..\BuildAutomation"

echo Building Windows and uploading to Google Drive...
python build_cli.py windows --gdrive-upload

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Build or upload failed!
    pause
    exit /b 1
)

echo.
echo Windows build and upload completed successfully!
pause