@echo off
REM Execute pre-build hook, then build Windows and upload to Google Drive
REM Usage: hook-build-windows-gdrive.bat "BuildHooks.SwitchToProduction"

echo Unity Build Automation - Hook + Windows Build + Google Drive Upload
echo =================================================================
echo.

if "%~1"=="" (
    echo Error: Please specify a pre-build hook method
    echo Usage: hook-build-windows-gdrive.bat "ClassName.MethodName"
    echo Example: hook-build-windows-gdrive.bat "BuildHooks.SwitchToProduction"
    pause
    exit /b 1
)

cd /d "%~dp0\..\BuildAutomation"

echo Executing pre-build hook: %1
echo Then building Windows and uploading to Google Drive...
echo.

python build_cli.py windows --gdrive-upload --hook "%~1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Build or upload failed!
    pause
    exit /b 1
)

echo.
echo Hook execution, Windows build, and upload completed successfully!
pause