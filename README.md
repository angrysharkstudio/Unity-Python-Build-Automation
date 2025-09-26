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

### 2. Create Virtual Environment (Recommended)

Setting up a Python virtual environment ensures clean dependency management:

**Windows:**
```bash
cd YourUnityProject/BuildAutomation
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
cd YourUnityProject/BuildAutomation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Remember to activate the virtual environment before running build scripts!

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
- Can be automatically uploaded to FTP (see WebGL FTP Deployment section)

## Pre-Build Hooks (Advanced)

Execute custom Unity methods before building to automate environment switching, version updates, or other preparations.

### Setup

1. Create a static method in your Unity project:
```csharp
public class BuildHooks {
    public static void SwitchToProduction() {
        // Your custom logic here
        Debug.Log("Switched to production environment");
        // Example: Update server URLs, API keys, etc.
    }
    
    public static void IncrementBuildNumber() {
        var currentVersion = PlayerSettings.bundleVersion;
        // Parse and increment version logic
        PlayerSettings.bundleVersion = newVersion;
    }
}
```

2. Configure in `.env`:
```
PRE_BUILD_HOOK="BuildHooks.SwitchToProduction"
```

3. The hook runs automatically before each build.

### Command Line Usage

```bash
# Use hook from .env
python build_cli.py webgl

# Override with custom hook
python build_cli.py webgl --hook "BuildHooks.PrepareWebGL"

# Skip hook even if configured
python build_cli.py webgl --no-hook
```

## WebGL FTP Deployment

Automatically upload WebGL builds to your web server after building.

### Setup

1. Configure FTP in `.env`:
```
WEBGL_FTP_ENABLED=true
WEBGL_FTP_HOST="ftp.yourdomain.com"
WEBGL_FTP_USERNAME="your-username"
WEBGL_FTP_PASSWORD="your-password"
WEBGL_FTP_REMOTE_PATH="/public_html/games/mygame"
WEBGL_FTP_OVERWRITE=true
```

2. Build and upload:
```bash
python build_cli.py webgl --upload
```

### One-Command Deployment

Full pipeline with hook → build → upload:

**Windows:**
```batch
scripts\webgl-full-deploy.bat
```

**macOS/Linux:**
```bash
chmod +x scripts/*.sh  # First time only
./scripts/webgl-full-deploy.sh
```

The script will:
1. Execute your pre-build hook (if configured)
2. Build WebGL
3. Upload to FTP with progress tracking
4. Overwrite existing files (perfect for updates)

### Additional WebGL Scripts

- `webgl-build-upload.bat/.sh` - Build and upload (skip hook)
- `webgl-hook-build.bat/.sh` - Hook and build (no upload)
- `webgl-upload-only.bat/.sh` - Upload existing build

### Security Considerations

- Use FTPS (FTP over TLS) when possible: `WEBGL_FTP_USE_TLS=true`
- Never commit `.env` files with passwords
- Consider using deployment keys or CI/CD secrets for production

## Windows Build Google Drive Upload

Automatically upload Windows builds to Google Drive with email notifications.

### Setup

1. Follow the [Google Drive Credentials Setup Guide](GoogleCredentialsSetup.md)

2. Configure in `.env`:
```
WINDOWS_GDRIVE_ENABLED=true
GDRIVE_CREDENTIALS_FILE="credentials.json"
GDRIVE_FOLDER_ID="your-folder-id"

# Email notifications (optional)
EMAIL_ENABLED=true
EMAIL_SMTP_HOST="smtp.gmail.com"
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USERNAME="your-email@gmail.com"
EMAIL_SMTP_PASSWORD="your-app-password"
EMAIL_FROM="your-email@gmail.com"
EMAIL_TO="team@example.com"
EMAIL_SUBJECT_PREFIX="MyProject"  # For multi-build setups
```

3. Build and upload:
```bash
python build_cli.py windows --gdrive-upload
```

### Features
- Automatic zipping with intelligent exclusion of debug folders
- Resumable uploads for large files
- Email notifications with shareable download links
- Support for multi-build workflows with email prefixes

See [Multi-Build Setup Guide](BuildAutomation/examples/multi-build-setup/README.md) for advanced workflows.

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