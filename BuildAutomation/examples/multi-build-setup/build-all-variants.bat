@echo off
REM Build all project variants sequentially
echo Unity Build Automation - Build All Variants
echo ===========================================
echo.

cd /d "%~dp0\..\.."

REM Build Recorder variant
echo [1/2] Building RECORDER variant...
echo ================================
copy /Y examples\multi-build-setup\.env.recorder .env
if %ERRORLEVEL% NEQ 0 goto :error

python build_cli.py windows --gdrive-upload
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo [1/2] Recorder build completed!
echo.

REM Build VR variant
echo [2/2] Building VR variant...
echo ============================
copy /Y examples\multi-build-setup\.env.vr .env
if %ERRORLEVEL% NEQ 0 goto :error

python build_cli.py windows --gdrive-upload
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo [2/2] VR build completed!
echo.

echo ========================================
echo All variants built successfully!
echo.
echo Check your email for download links:
echo - Recorder build (prefix: "Recorder")
echo - VR build (prefix: "VR")
echo ========================================

pause
exit /b 0

:error
echo.
echo [ERROR] Build process failed!
pause
exit /b 1