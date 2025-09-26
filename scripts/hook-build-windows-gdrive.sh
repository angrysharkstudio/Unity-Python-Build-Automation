#!/bin/bash
# Execute pre-build hook, then build Windows and upload to Google Drive
# Usage: ./hook-build-windows-gdrive.sh "BuildHooks.SwitchToProduction"

echo "Unity Build Automation - Hook + Windows Build + Google Drive Upload"
echo "================================================================="
echo ""

if [ -z "$1" ]; then
    echo "Error: Please specify a pre-build hook method"
    echo "Usage: ./hook-build-windows-gdrive.sh \"ClassName.MethodName\""
    echo "Example: ./hook-build-windows-gdrive.sh \"BuildHooks.SwitchToProduction\""
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Navigate to BuildAutomation directory
cd "$SCRIPT_DIR/../BuildAutomation"

echo "Executing pre-build hook: $1"
echo "Then building Windows and uploading to Google Drive..."
echo ""

python3 build_cli.py windows --gdrive-upload --hook "$1"

if [ $? -ne 0 ]; then
    echo ""
    echo "Build or upload failed!"
    exit 1
fi

echo ""
echo "Hook execution, Windows build, and upload completed successfully!"