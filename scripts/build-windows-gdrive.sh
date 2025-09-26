#!/bin/bash
# Build Windows and upload to Google Drive
# This script builds for Windows platform and uploads the result to Google Drive

echo "Unity Build Automation - Windows Build with Google Drive Upload"
echo "============================================================"
echo ""

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Navigate to BuildAutomation directory
cd "$SCRIPT_DIR/../BuildAutomation"

echo "Building Windows and uploading to Google Drive..."
python3 build_cli.py windows --gdrive-upload

if [ $? -ne 0 ]; then
    echo ""
    echo "Build or upload failed!"
    exit 1
fi

echo ""
echo "Windows build and upload completed successfully!"