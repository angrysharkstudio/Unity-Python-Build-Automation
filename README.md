# Unity Build Automation - Zero Configuration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Unity 2021.3+](https://img.shields.io/badge/Unity-2021.3+-black.svg)](https://unity.com/)

Automate Unity builds for multiple platforms with zero configuration! This Python script automatically detects your Unity project settings and builds for Windows, Mac, Android, and WebGL with a single command.

## ✨ Features

- **Zero Configuration**: Automatically detects project name, company, Unity version, and more
- **Multi-Platform**: Build for Windows, Mac, Android, and WebGL
- **Smart Detection**: Finds Unity project root, reads settings from ProjectSettings.asset
- **Interactive Menu**: Choose what to build with a simple menu
- **Beautiful Reports**: Generates HTML build reports with timing and file sizes
- **Platform Checking**: Automatically skips unavailable platforms
- **Portable**: Scripts live inside your Unity project

## 🚀 Quick Start

### 1. Copy Scripts to Your Unity Project

Copy the `BuildAutomation` folder into your Unity project root:

```
YourUnityProject/
├── Assets/
├── ProjectSettings/
├── BuildAutomation/      ← Add this folder
│   ├── build.py
│   ├── .env.example
│   └── requirements.txt
```

### 2. Set Up Python Environment

```bash
cd YourUnityProject/BuildAutomation
pip install -r requirements.txt
```

### 3. Configure Unity Path

```bash
cp .env.example .env
# Edit .env and add your Unity installation path
```

Example `.env` contents:
```
UNITY_PATH="C:/Program Files/Unity/Hub/Editor/2021.3.16f1/Editor/Unity.exe"
```

### 4. Run the Build

```bash
python build.py
```

That's it! The script will auto-detect everything else.

## 📋 Prerequisites

- Python 3.8 or higher
- Unity 2021.3 LTS or newer
- Unity build support for desired platforms installed
- For Android builds: Android SDK with `ANDROID_HOME` environment variable set

## 🎯 What Gets Auto-Detected

| Setting | Source | Example |
|---------|---------|---------|
| Project Name | ProjectSettings.asset | "My Awesome Game" |
| Company Name | ProjectSettings.asset | "Indie Studio" |
| Unity Version | ProjectVersion.txt | "2021.3.16f1" |
| Bundle ID | ProjectSettings.asset | "com.IndieStudio.MyAwesomeGame" |
| Project Root | Script location | Finds Assets/ProjectSettings folders |

## 📁 Unity Setup

Your Unity project needs a build script. Create `Assets/Scripts/Editor/CommandLineBuild.cs`:

```csharp
using UnityEditor;
using UnityEngine;

public class CommandLineBuild
{
    static void BuildWindows()
    {
        BuildPlayerOptions buildPlayerOptions = new BuildPlayerOptions();
        buildPlayerOptions.scenes = new[] { "Assets/Scenes/MainScene.unity" };
        buildPlayerOptions.locationPathName = "Builds/Windows/YourGame.exe";
        buildPlayerOptions.target = BuildTarget.StandaloneWindows64;
        buildPlayerOptions.options = BuildOptions.None;
        BuildPipeline.BuildPlayer(buildPlayerOptions);
    }

    // Add similar methods for BuildMac(), BuildAndroid(), BuildWebGL()
}
```

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

## 📊 Build Reports

After building, find your HTML report at:
```
BuildAutomation/build_report.html
```

The report includes:
- Build status for each platform
- Build times
- Output file sizes
- File locations

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