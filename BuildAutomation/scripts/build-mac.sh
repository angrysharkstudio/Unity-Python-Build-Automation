#!/bin/bash
# Unity Build Automation - macOS Build Script
# Quick non-interactive build for macOS platform
#
# MIT License - Copyright (c) 2025 Angry Shark Studio

# Change to parent directory (BuildAutomation)
cd "$(dirname "$0")/.." || exit 1

echo "Building Unity project for macOS..."
echo

python build_cli.py mac

if [ $? -eq 0 ]; then
    echo
    echo "Build completed successfully!"
    exit 0
else
    echo
    echo "Build failed! Check logs for details."
    exit 1
fi