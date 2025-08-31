#!/bin/bash
# Unity Build Automation - iOS Build Script
# Quick non-interactive build for iOS platform (macOS only)
#
# MIT License - Copyright (c) 2025 Angry Shark Studio

# Change to parent directory (BuildAutomation)
cd "$(dirname "$0")/.." || exit 1

echo "Building Unity project for iOS..."
echo "Note: iOS builds require macOS and create Xcode projects"
echo

python build_cli.py ios

if [ $? -eq 0 ]; then
    echo
    echo "Build completed successfully!"
    echo "Open the Xcode project to build final iOS app."
    exit 0
else
    echo
    echo "Build failed! Check logs for details."
    exit 1
fi