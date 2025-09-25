#!/bin/bash
# Unity Build Automation - WebGL Upload Only
# Uploads existing WebGL build to FTP (no building)
#
# MIT License - Copyright (c) 2025 Angry Shark Studio

cd "$(dirname "$0")/.."

echo "Uploading existing WebGL build to FTP..."
echo ""

python build_cli.py --upload-only

if [ $? -eq 0 ]; then
    echo ""
    echo "Upload completed successfully!"
    exit 0
else
    echo ""
    echo "Upload failed! Check logs for details."
    exit 1
fi