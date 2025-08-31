# Unity Build Automation with Python

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Unity 2021.3+](https://img.shields.io/badge/Unity-2021.3+-black.svg)](https://unity.com/)

A zero-configuration Python automation system for building Unity projects across multiple platforms. Save hours of manual work with a single command!

## Features

- **Zero Configuration**: Automatically detects project settings from Unity files
- **Multi-Platform Builds**: Windows, macOS, Android, WebGL, and iOS support
- **Beautiful Console UI**: Rich formatting with progress indicators
- **Version Management**: Organizes builds by version and timestamp
- **Build Reports**: Generates HTML reports with build statistics
- **Command-Line Interface**: Non-interactive builds for CI/CD integration
- **Cross-Platform**: Works on Windows, macOS, and Linux (iOS requires macOS)
- **Unity Version Validation**: Detects version mismatches between project and executable
- **Smart Path Detection**: Shows both project Unity version and actual executable being used

## Requirements

- Unity 2021.3 LTS or newer
- Python 3.8 or newer
- TextMeshPro package (imported in Unity)

## Quick Start

### 1. Setup

Place the `BuildAutomation` folder inside your Unity project:

```
YourUnityProject/
├── Assets/
├── ProjectSettings/
├── BuildAutomation/        # Copy this folder here
│   ├── build.py
│   ├── build_cli.py
│   ├── unity_builder/
│   ├── scripts/
│   └── requirements.txt
└── Builds/                 # Build outputs will go here
```

### 2. Install Dependencies

```bash
cd YourUnityProject/BuildAutomation
pip install -r requirements.txt
```

### 3. Configure Unity Path

Copy `.env.example` to `.env` and set your Unity installation path:

```bash
cp .env.example .env
```

Edit `.env`:
```
# Windows example:
UNITY_PATH="C:/Program Files/Unity/Hub/Editor/2021.3.16f1/Editor/Unity.exe"

# macOS example:
# UNITY_PATH="/Applications/Unity/Hub/Editor/2021.3.16f1/Unity.app/Contents/MacOS/Unity"

# Linux example:
# UNITY_PATH="/home/username/Unity/Hub/Editor/2021.3.16f1/Editor/Unity"
```

**Important: Unity Version Considerations**
- The script will detect if your Unity executable version differs from the project version
- Using a different Unity version may cause compatibility issues
- You'll be warned if versions don't match, but can choose to continue

### 4. Add Unity Build Script

Copy `CommandLineBuild.cs` to `Assets/Scripts/Editor/` in your Unity project. This script enables command-line builds.

### 5. Run Your First Build

Interactive mode:
```bash
python build.py
```

Non-interactive mode:
```bash
python build_cli.py windows
```

## Usage Guide

### Interactive Mode

Run `python build.py` for an interactive menu:

```
Unity Build Automation
Zero Configuration Edition

What would you like to build?
  1. Windows only
  2. All platforms
  3. Custom selection
  4. Exit

Enter your choice (1-4):
```

### Command-Line Mode

Use `build_cli.py` for non-interactive builds:

```bash
# Build specific platform
python build_cli.py windows
python build_cli.py android
python build_cli.py webgl

# Build multiple platforms
python build_cli.py windows android

# Build all platforms
python build_cli.py --all

# Skip HTML report generation
python build_cli.py windows --no-report

# Show help
python build_cli.py --help
```

### Quick Build Scripts

Use platform-specific scripts for even faster builds:

**Windows:**
```batch
# Windows batch files
scripts\build-windows.bat
scripts\build-mac.bat
scripts\build-android.bat
scripts\build-webgl.bat
scripts\build-ios.bat
scripts\build-all.bat
```

**macOS/Linux:**
```bash
# Shell scripts
chmod +x scripts/*.sh  # Make executable (first time only)
./scripts/build-windows.sh
./scripts/build-mac.sh
./scripts/build-android.sh
./scripts/build-webgl.sh
./scripts/build-ios.sh
./scripts/build-all.sh
```

## Build Output Structure

Builds are organized by platform, version, and timestamp:

```
Builds/
├── Windows/
│   └── 1.0.0_31-08-2025_14-30/
│       └── MyGame.exe
├── Android/
│   └── 1.0.0_31-08-2025_14-30/
│       └── MyGame.apk
├── WebGL/
│   └── 1.0.0_31-08-2025_14-30/
│       └── MyGame/
│           ├── index.html
│           └── Build/
└── Mac/
    └── 1.0.0_31-08-2025_14-30/
        └── MyGame.app
```

**How timestamp folders work:**
1. Unity builds to a simple version folder (e.g., `Builds/Windows/1.0.0/`)
2. Python automatically moves the build to a timestamped folder (e.g., `Builds/Windows/1.0.0_31-08-2025_14-30/`)
3. This prevents overwriting when building the same version multiple times

## Auto-Detection Features

The system automatically detects:
- Project name from `ProjectSettings.asset`
- Company name and bundle identifier
- Unity version from `ProjectVersion.txt`
- Build version number
- Scene files from Build Settings

No manual configuration needed!

| Setting         | Source                | Example                              |
|-----------------|-----------------------|--------------------------------------|
| Project Name    | ProjectSettings.asset | "My Awesome Game"                    |
| Company Name    | ProjectSettings.asset | "Indie Studio"                       |
| Project Version | ProjectSettings.asset | "1.0.0"                              |
| Unity Version   | ProjectVersion.txt    | "2021.3.16f1"                        |
| Bundle ID       | ProjectSettings.asset | "com.IndieStudio.MyAwesomeGame"      |
| Project Root    | Script location       | Finds Assets/ProjectSettings folders |

### Understanding Unity Versions

**Project Unity Version**: The Unity version your project was created/last saved with (from `ProjectVersion.txt`)

**Unity Executable Version**: The Unity installation you're using to build (from `.env` file)

These can be different! The script will:
1. Show both versions in the configuration display
2. Warn you if they don't match
3. Let you decide whether to continue

**When is a version mismatch OK?**
- Minor version differences (e.g., 2021.3.16f1 → 2021.3.18f1) are usually safe
- Using a newer Unity version to build an older project often works
- Major version differences may cause issues

## HTML Build Reports

After each build session, an HTML report is generated:
- Build times and file sizes
- Success/failure status
- Platform-specific details
- Version information

Find reports in: `BuildAutomation/build_report.html`

## CI/CD Integration

Perfect for continuous integration pipelines:

```yaml
# Example GitHub Actions workflow
- name: Build Unity Project
  run: |
    cd BuildAutomation
    python build_cli.py --all
```

Exit codes:
- 0: At least one build succeeded
- 1: All builds failed or error occurred

## Platform-Specific Notes

### Android Builds
- Requires Android SDK installed
- Set `ANDROID_HOME` environment variable
- Unity Android build support must be installed

### macOS Builds
- Only available when running on macOS
- Requires Xcode command line tools

### iOS Builds
- Only available when running on macOS
- Requires iOS Build Support module
- Outputs Xcode project (not final .ipa)
- Must set bundle identifier in Player Settings
- Open in Xcode to build the final app

### WebGL Builds
- Requires WebGL Build Support module
- Requires significant memory (8GB+ recommended)
- Build times are longer than other platforms
- Creates a folder instead of a single file

## Troubleshooting

### Unity Path Not Found
- Check `.env` file exists and contains a correct path
- Verify Unity installation location in Unity Hub
- Path must point to Unity executable, not just the installation folder

### Build Fails Silently
Check log files in `BuildAutomation/`:
- `build_windows.log`
- `build_android.log`
- `build_webgl.log`
- `build_mac.log`

Common issues:
- Scene isn't added to Build Settings
- Missing Android SDK for Android builds
- Script compilation errors in a Unity project

### Permission Denied (macOS/Linux)
```bash
chmod +x /path/to/Unity
chmod +x scripts/*.sh
```

## License

MIT License - Copyright © 2025 Angry Shark Studio

See the LICENSE file for details.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support

- [GitHub Issues](https://github.com/angrysharkstudio/Unity-Python-Build-Automation/issues)
- [Blog Tutorial](https://angrysharkstudio.com/blog/python-unity-build-automation-tutorial?utm_source=github&utm_medium=readme&utm_campaign=unity_build_automation)

---

Made with Python and Unity by [Angry Shark Studio](https://www.angry-shark-studio.com?utm_source=github&utm_medium=readme&utm_campaign=unity_build_automation)