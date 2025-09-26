@echo off
REM Upload existing Windows build to Google Drive
REM This script uploads the latest Windows build without building

echo Unity Build Automation - Upload Windows Build to Google Drive
echo ===========================================================
echo.

cd /d "%~dp0\..\BuildAutomation"

echo Uploading existing Windows build to Google Drive...
python build_cli.py --upload-only

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Upload failed!
    pause
    exit /b 1
)

echo.
echo Windows build upload completed successfully!
pause