#!/bin/bash
# Unity Build Automation - WebGL Build and Upload
# Builds WebGL and uploads to FTP (no pre-build hook)
#
# MIT License - Copyright (c) 2025 Angry Shark Studio

cd "$(dirname "$0")/.."

echo "Building Unity project for WebGL and uploading to FTP..."
echo ""

python build_cli.py webgl --upload --no-hook

if [ $? -eq 0 ]; then
    echo ""
    echo "Build and upload completed successfully!"
    exit 0
else
    echo ""
    echo "Build or upload failed! Check logs for details."
    exit 1
fi