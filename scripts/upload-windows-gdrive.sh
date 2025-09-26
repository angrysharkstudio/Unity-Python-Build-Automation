#!/bin/bash
# Upload existing Windows build to Google Drive
# This script uploads the latest Windows build without building

echo "Unity Build Automation - Upload Windows Build to Google Drive"
echo "==========================================================="
echo ""

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Navigate to BuildAutomation directory
cd "$SCRIPT_DIR/../BuildAutomation"

echo "Uploading existing Windows build to Google Drive..."
python3 build_cli.py --upload-only

if [ $? -ne 0 ]; then
    echo ""
    echo "Upload failed!"
    exit 1
fi

echo ""
echo "Windows build upload completed successfully!"