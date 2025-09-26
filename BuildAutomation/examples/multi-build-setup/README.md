# Multi-Build Setup Guide

This guide explains how to set up and manage multiple build variants (e.g., Recorder and VR) with different scene configurations and email notifications.

## Overview

The multi-build setup allows you to:
- Maintain separate configurations for different build variants
- Automatically select the correct scenes for each variant
- Send emails with distinct subject prefixes (e.g., "Recorder" or "VR")
- Build all variants sequentially with a single command

## Setup Instructions

### 1. Copy Environment Files

Copy the example `.env` files from this directory to your BuildAutomation folder:

```bash
# From BuildAutomation directory:
copy examples\multi-build-setup\.env.recorder .env.recorder
copy examples\multi-build-setup\.env.vr .env.vr
```

### 2. Update Configuration

Edit each `.env` file with your specific settings:

#### .env.recorder
- Set your Unity path
- Update Google Drive folder ID for Recorder builds
- Configure email settings and recipients
- Keep `EMAIL_SUBJECT_PREFIX="Recorder"`
- Keep `PRE_BUILD_HOOK="BuildHooks.SelectProject1Scenes"`

#### .env.vr
- Set your Unity path (same as above)
- Update Google Drive folder ID for VR builds (can be different)
- Configure email settings and recipients
- Keep `EMAIL_SUBJECT_PREFIX="VR"`
- Keep `PRE_BUILD_HOOK="BuildHooks.SelectProject2Scenes"`

### 3. Update BuildHooks.cs

Copy `Assets/__Scripts/Editor/BuildHooks.cs` to your Unity project and modify:

```csharp
public static void SelectProject1Scenes() {
    // Update with your Recorder-specific scenes
    EditorBuildSettings.scenes = new[] {
        new EditorBuildSettingsScene("Assets/Scenes/Recorder/MainScene.unity", true),
        new EditorBuildSettingsScene("Assets/Scenes/Recorder/UIScene.unity", true)
    };
    PlayerSettings.productName = "MyGame - Recorder";
}

public static void SelectProject2Scenes() {
    // Update with your VR-specific scenes
    EditorBuildSettings.scenes = new[] {
        new EditorBuildSettingsScene("Assets/Scenes/VR/GameScene.unity", true),
        new EditorBuildSettingsScene("Assets/Scenes/VR/MenuScene.unity", true)
    };
    PlayerSettings.productName = "MyGame - VR";
}
```

## Usage

### Switching Between Configurations

Use the provided batch files to switch configurations:

```batch
# Switch to Recorder configuration
BuildAutomation\examples\multi-build-setup\switch-to-recorder.bat

# Switch to VR configuration
BuildAutomation\examples\multi-build-setup\switch-to-vr.bat
```

### Building Individual Variants

After switching configuration:

```batch
# Interactive menu
python build.py

# Direct build with upload
python build_cli.py windows --gdrive-upload

# Using quick scripts
scripts\build-windows-gdrive.bat
```

### Building All Variants

Build both variants automatically:

```batch
BuildAutomation\examples\multi-build-setup\build-all-variants.bat
```

This will:
1. Switch to Recorder configuration
2. Build and upload Recorder variant
3. Switch to VR configuration
4. Build and upload VR variant
5. Send separate emails for each build

## Email Notifications

With this setup, you'll receive distinct emails:

- **Recorder Build**: "Recorder - Unity Windows Build Ready - v1.0.0"
- **VR Build**: "VR - Unity Windows Build Ready - v1.0.0"

Each email will contain:
- The appropriate download link
- Build information (version, time, size)
- Clear identification of which variant was built

## Advanced Configuration

### Different Google Drive Folders

You can upload each variant to a different Google Drive folder:
- Set different `GDRIVE_FOLDER_ID` values in each `.env` file
- Organize builds by variant in your Drive

### Different Recipients

Send notifications to different teams:
- Recorder builds → recorder-team@example.com
- VR builds → vr-team@example.com

### Custom Build Settings

In BuildHooks.cs, you can also:
- Set different version numbers
- Enable/disable specific Unity features
- Apply different compiler defines
- Configure platform-specific settings

## Troubleshooting

### Configuration Not Switching
- Ensure you're running the switch scripts from the correct directory
- Check that the `.env` files exist in the examples directory

### Wrong Scenes in Build
- Verify BuildHooks.cs is in Assets/__Scripts/Editor/
- Check that scene paths in BuildHooks match your project
- Ensure scenes are added to Build Settings in Unity

### Email Prefix Not Appearing
- Verify `EMAIL_SUBJECT_PREFIX` is set in your active .env file
- Check that you're using the latest windows_gdrive_uploader.py

## Example Workflow

1. **Morning**: Build Recorder variant for QA team
   ```batch
   switch-to-recorder.bat
   scripts\build-windows-gdrive.bat
   ```

2. **Afternoon**: Build VR variant for VR testing
   ```batch
   switch-to-vr.bat
   scripts\build-windows-gdrive.bat
   ```

3. **End of day**: Build all variants for overnight testing
   ```batch
   build-all-variants.bat
   ```

## Best Practices

1. **Version Control**: Don't commit actual .env files, only the examples
2. **Backup**: Keep backups of your configured .env files
3. **Documentation**: Document which scenes belong to which variant
4. **Testing**: Test the switch scripts before relying on automated builds
5. **Monitoring**: Set up different email aliases to track build notifications