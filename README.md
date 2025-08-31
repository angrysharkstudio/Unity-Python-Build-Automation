# Unity Build Automation - Zero Configuration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Unity 2021.3+](https://img.shields.io/badge/Unity-2021.3+-black.svg)](https://unity.com/)

Automate Unity builds for multiple platforms with zero configuration! This Python script automatically detects your Unity project settings and builds for Windows, Mac, Android, and WebGL with a single command.

## ✨ Features

- **Zero Configuration**: Automatically detects project name, company, Unity version, and more
- **Multi-Platform**: Build for Windows, Mac, Android, and WebGL
- **Smart Detection**: Finds Unity project root, reads settings from ProjectSettings.asset
- **Version-Based Output**: Builds organized in version folders (e.g., `Builds/Windows/1.0.0/`)
- **Beautiful Console**: Rich formatting with colors, progress bars, and tables
- **Interactive Menu**: Choose what to build with a simple menu
- **Modular Architecture**: Clean Python package structure for easy extension
- **Comprehensive Reports**: Enhanced HTML build reports with version tracking
- **Platform Checking**: Automatically skips unavailable platforms with helpful messages
- **Error Handling**: Clear error messages with actionable solutions
- **Modern Unity Code**: Uses TextMeshPro and proper C# patterns

## 🚀 Quick Start

### 1. Copy Scripts to Your Unity Project

Copy the `BuildAutomation` folder into your Unity project root:

```
YourUnityProject/
├── Assets/
├── ProjectSettings/
├── BuildAutomation/         ← Add this folder
│   ├── unity_builder/       # Python package
│   │   ├── __init__.py
│   │   ├── config.py        # Auto-detection logic
│   │   ├── platforms.py     # Platform builds
│   │   ├── reporter.py      # HTML reports
│   │   ├── builder.py       # Main orchestration
│   │   └── utils.py         # Utilities
│   ├── build.py             # Entry point
│   ├── .env.example         # Unity path template
│   ├── requirements.txt     # Dependencies
│   └── CommandLineBuild.cs  ← Copy to Assets/Scripts/Editor/
```

### 2. Copy Unity Build Script

Copy `CommandLineBuild.cs` to your Unity project:
```bash
cp BuildAutomation/CommandLineBuild.cs Assets/Scripts/Editor/
```

### 3. Set Up Python Environment

```bash
cd YourUnityProject/BuildAutomation
pip install -r requirements.txt
```

### 4. Configure Unity Path

```bash
cp .env.example .env
# Edit .env and add your Unity installation path
```

Example `.env` contents:
```
UNITY_PATH="C:/Program Files/Unity/Hub/Editor/2021.3.16f1/Editor/Unity.exe"
```

### 5. Run the Build

```bash
python build.py
```

That's it! The script will auto-detect everything else.

## 📋 Prerequisites

- Python 3.8 or higher
- Unity 2021.3 LTS or newer
- TextMeshPro package imported in Unity
- Unity build support for desired platforms installed
- For Android builds: Android SDK with `ANDROID_HOME` environment variable set

## 🎯 What Gets Auto-Detected

| Setting | Source | Example |
|---------|---------|---------|
| Project Name | ProjectSettings.asset | "My Awesome Game" |
| Company Name | ProjectSettings.asset | "Indie Studio" |
| Project Version | ProjectSettings.asset | "1.0.0" |
| Unity Version | ProjectVersion.txt | "2021.3.16f1" |
| Bundle ID | ProjectSettings.asset | "com.IndieStudio.MyAwesomeGame" |
| Project Root | Script location | Finds Assets/ProjectSettings folders |

## 📁 Unity Setup

The included `CommandLineBuild.cs` file provides all the build methods needed for automation. It features:

- **Automatic scene detection** from Build Settings
- **Dynamic product naming** from Player Settings
- **Error handling** with proper exit codes
- **Directory creation** for build outputs
- **Support for all platforms** (Windows, Mac, Android, WebGL)

The script reads all configuration from your Unity project settings - no hardcoding required!

## 🛠️ Configuration

The only configuration needed is your Unity installation path in the `.env` file. Everything else is automatic!

### Finding Your Unity Path

**Windows:**
```
C:/Program Files/Unity/Hub/Editor/[version]/Editor/Unity.exe
```

**macOS:**
```
/Applications/Unity/Hub/Editor/[version]/Unity.app/Contents/MacOS/Unity
```

**Linux:**
```
/home/username/Unity/Hub/Editor/[version]/Editor/Unity
```

## 🎨 Beautiful Console Output

With Rich integration, you'll see:
- 🌈 Colored text and emojis for better readability
- ⏳ Progress bars and spinners during builds
- 📊 Formatted tables for build summaries
- 🎯 Clear error messages with solutions

Example output:
```
┌─ Unity Build Configuration ──────────────────────────┐
│ 🎮 Project     My Awesome Game                       │
│ 📦 Version     1.0.0                                 │
│ 🔧 Unity       2021.3.16f1                          │
└──────────────────────────────────────────────────────┘

🏗️  Building for Windows...
Output: Builds/Windows/1.0.0/MyAwesomeGame.exe
✅ Windows build completed!
   Time: 45.2 seconds
   Size: 23.4 MB
   Version: 1.0.0
```

## 📊 Build Reports

After building, find your enhanced HTML report at:
```
BuildAutomation/build_report.html
```

The report includes:
- Project version prominently displayed
- Build status for each platform
- Build times and file sizes
- Version-organized output paths
- Professional styling

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Created as part of a Unity automation tutorial
- Inspired by the need for simpler Unity build workflows
- Thanks to the Unity and Python communities

## 📚 Learn More

Check out the full tutorial: [Python for Unity Developers: Automate Your Builds in 5 Steps](https://angrysharkstudio.com/blog/python-unity-build-automation-tutorial)

---

Made with ❤️ for Unity developers who hate repetitive tasks