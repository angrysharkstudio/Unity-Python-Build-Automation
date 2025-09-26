@echo off
REM Switch to Recorder build configuration
echo Switching to RECORDER build configuration...
echo.

cd /d "%~dp0\..\.."
copy /Y examples\multi-build-setup\.env.recorder .env

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Switched to Recorder configuration
    echo.
    echo Current configuration:
    echo - Email prefix: Recorder
    echo - Pre-build hook: BuildHooks.SelectProject1Scenes
    echo - Build will include Recorder-specific scenes
    echo.
    echo You can now run build commands:
    echo - python build.py
    echo - scripts\build-windows-gdrive.bat
) else (
    echo [ERROR] Failed to switch configuration
    exit /b 1
)