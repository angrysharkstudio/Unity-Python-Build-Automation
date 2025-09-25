#!/bin/bash
# Unity Build Automation - WebGL Hook and Build
# Executes pre-build hook and builds WebGL (no upload)
#
# MIT License - Copyright (c) 2025 Angry Shark Studio

cd "$(dirname "$0")/.."

echo "Building Unity project for WebGL with pre-build hook..."
echo ""

python build_cli.py webgl

if [ $? -eq 0 ]; then
    echo ""
    echo "Build completed successfully!"
    echo "Output in: Builds/WebGL/"
    exit 0
else
    echo ""
    echo "Build failed! Check logs for details."
    exit 1
fi