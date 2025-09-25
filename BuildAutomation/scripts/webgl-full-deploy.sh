#!/bin/bash
# Unity Build Automation - Full WebGL Deployment
# Executes pre-build hook, builds WebGL, and uploads to FTP
#
# MIT License - Copyright (c) 2025 Angry Shark Studio

# Get the directory of the script and navigate to BuildAutomation
cd "$(dirname "$0")/.."

echo ""
echo "========================================"
echo "    Full WebGL Deployment Pipeline"
echo "========================================"
echo ""
echo "1. Executing pre-build hook (if configured)"
echo "2. Building WebGL"
echo "3. Uploading to FTP (with overwrite)"
echo ""
echo "----------------------------------------"
echo ""

python build_cli.py webgl --upload

if [ $? -eq 0 ]; then
    echo ""
    echo "Deployment completed successfully!"
    echo "Check your FTP server for the uploaded build."
    exit 0
else
    echo ""
    echo "Deployment failed! Check logs for details."
    exit 1
fi