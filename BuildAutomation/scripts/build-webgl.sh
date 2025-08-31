#!/bin/bash
# Unity Build Automation - WebGL Build Script
# Quick non-interactive build for WebGL platform
#
# MIT License - Copyright (c) 2025 Angry Shark Studio

# Change to parent directory (BuildAutomation)
cd "$(dirname "$0")/.." || exit 1

echo "Building Unity project for WebGL..."
echo

python build_cli.py webgl

if [ $? -eq 0 ]; then
    echo
    echo "Build completed successfully!"
    exit 0
else
    echo
    echo "Build failed! Check logs for details."
    exit 1
fi