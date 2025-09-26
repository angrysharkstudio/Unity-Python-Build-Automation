@echo off
REM Switch to VR build configuration
echo Switching to VR build configuration...
echo.

cd /d "%~dp0\..\.."
copy /Y examples\multi-build-setup\.env.vr .env

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Switched to VR configuration
    echo.
    echo Current configuration:
    echo - Email prefix: VR
    echo - Pre-build hook: BuildHooks.SelectProject2Scenes
    echo - Build will include VR-specific scenes
    echo.
    echo You can now run build commands:
    echo - python build.py
    echo - scripts\build-windows-gdrive.bat
) else (
    echo [ERROR] Failed to switch configuration
    exit /b 1
)