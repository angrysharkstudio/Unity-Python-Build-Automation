#!/bin/bash
# Unity Build Automation - Build Multiple Platforms Script
# Example of building multiple specific platforms
#
# MIT License - Copyright (c) 2025 Angry Shark Studio

# Change to parent directory (BuildAutomation)
cd "$(dirname "$0")/.." || exit 1

echo "Building Unity project for Windows and Android..."
echo

python build_cli.py windows android

if [ $? -eq 0 ]; then
    echo
    echo "Build completed successfully!"
    exit 0
else
    echo
    echo "Build failed! Check logs for details."
    exit 1
fi