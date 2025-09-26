# Unity Build Automation Troubleshooting Guide

## How Build Output Paths Work

**Important**: Unity and Python handle the build output paths in a coordinated way:

1. **Unity builds to**: `Builds/Platform/Version/` (e.g., `Builds/Windows/1.0.0/MyGame.exe`)
2. **Python expects**: Unity output in the version folder
3. **Python moves to**: Timestamped folder (e.g., `Builds/Windows/1.0.0_31-08-2025_14-30/MyGame.exe`)

This approach ensures:
- Unity uses simple, predictable paths
- Python adds timestamps to prevent overwriting
- No synchronization issues between Unity and Python timestamps

## Common Build Failures

### 1. Build Output Not Found

**Symptom**: A Python script reports "build failed" even though Unity might have succeeded.

**Solution**: We've updated `CommandLineBuild.cs` to include timestamps in the output paths to match what the Python script expects. Make sure to:
1. Copy the updated `CommandLineBuild.cs` to your Unity project's `Assets/Scripts/Editor/` folder
2. The output paths now include timestamps: `Builds/Platform/Version_Timestamp/GameName`

### 2. No Scenes in Build Settings

**Symptom**: Build fails with the "No scenes in Build Settings" error.

**Solution**:
1. Open Unity
2. Go to File → Build Settings
3. Add your scene(s) to the "Scenes In Build" list
4. Make sure at least one scene is checked/enabled
5. Save the project

### 3. Android Build Failures

**Common Issues**:

#### Android SDK Not Found
- Set the `ANDROID_HOME` environment variable to your Android SDK location
- Example Windows: `C:\Users\YourName\AppData\Local\Android\Sdk`
- Example macOS: `/Users/YourName/Library/Android/sdk`
- Example Linux: `/home/YourName/Android/Sdk`

#### Unity Android Build Support Isn't Installed
- Open Unity Hub
- Go to Installs
- Click the gear icon on your Unity version
- Add modules → Android Build Support (including Android SDK & NDK Tools, OpenJDK)

#### Minimum API Level Issues
- In Unity: File → Build Settings → Player Settings
- Under Android settings, check "Minimum API Level"
- Set to API Level 21 or higher for most modern apps

### 4. Windows Build Failures

**Common Issues**:

#### Missing Visual Studio Build Tools
- Windows builds require Visual Studio or Build Tools for Visual Studio
- Download from: https://visualstudio.microsoft.com/downloads/
- Install at least "Game development with Unity" workload

#### Antivirus Blocking Build
- Some antivirus software may block Unity from creating executables
- Temporarily disable antivirus or add Unity and your project folder to exclusions

### 5. Unity Path Issues

**Symptom**: "Unity path not found" error

**Solution**:
1. Verify Unity is installed via Unity Hub
2. Find the exact path to Unity executable:
   - Windows: Usually `C:\Program Files\Unity\Hub\Editor\[version]\Editor\Unity.exe`
   - macOS: Usually `/Applications/Unity/Hub/Editor/[version]/Unity.app/Contents/MacOS/Unity`
   - Linux: Usually `/home/[user]/Unity/Hub/Editor/[version]/Editor/Unity`
3. Update `.env` file with the correct path

### 6. Script Compilation Errors

**Symptom**: Build fails due to script errors

**Solution**:
1. Open your Unity project
2. Check the Console window for any compilation errors (Window → General → Console)
3. Fix any red errors before attempting to build
4. Common issues:
   - Missing TextMeshPro package (install via Package Manager)
   - Script errors in your game code
   - Missing dependencies

### 7. Build Log Location

Build logs are saved in the `BuildAutomation` folder:
- `build_windows.log`
- `build_android.log`
- `build_webgl.log`
- `build_mac.log`

Check these logs for detailed error messages.

### 8. Project Settings Issues

**Bundle Version Not Set**:
- File → Build Settings → Player Settings
- Set "Version" field (e.g., "1.0.0")

**Product Name Not Set**:
- File → Build Settings → Player Settings
- Set the "Product Name" field

**Company Name Not Set**:
- File → Build Settings → Player Settings
- Set the "Company Name" field

### 9. Python Environment Issues

**Missing Dependencies**:
```bash
cd BuildAutomation
pip install -r requirements.txt
```

**Wrong Python Version**:
- Requires Python 3.8 or newer
- Check version: `python --version`

### 10. WebGL Build Failures

**"Error building player because build target was unsupported"**:
This is the most common WebGL build error. Solutions:

1. **Install WebGL Build Support**:
   - Open Unity Hub
   - Click the gear icon on your Unity version
   - Add modules → WebGL Build Support
   - Verify installation at: `Unity/Editor/Data/PlaybackEngines/WebGLSupport`

2. **Command Line Fix**:
   - The script now includes `-buildTarget WebGL` parameter automatically
   - This tells Unity to load the WebGL module before building

3. **Antivirus Issues**:
   - Check if antivirus quarantined `MonoBleedingEdge`
   - Add Unity installation to antivirus exceptions

4. **Memory Requirements**:
   - WebGL builds need 8GB+ RAM
   - Close other applications during the build
   - Consider increasing virtual memory

### 11. iOS Build Information

**iOS builds have special requirements**:

1. **Platform Requirements**:
   - Must run on macOS (Xcode required)
   - iOS Build Support module must be installed
   - Valid Apple Developer account for device testing

2. **Build Output**:
   - Creates Xcode project, not final .ipa file
   - Must open in Xcode to create the final app
   - Located in: `Builds/iOS/Version_Timestamp/`

3. **Bundle Identifier**:
   - Must be set in Player Settings
   - Format: `com.yourcompany.yourproduct`
   - Cannot use default `com.Company.ProductName`

4. **Common Errors**:
   - "iOS builds can only be created on macOS" - Running on Windows/Linux
   - "iOS module not installed" - Add iOS Build Support in Unity Hub
   - "Bundle Identifier isn't set" - Configure in Player Settings

### 12. Quick Verification Steps

Run this checklist before building:

1. **Unity Project Check**:
   ```bash
   python -c "from unity_builder.config import Config; c = Config(); c.print_configuration()"
   ```

2. **Unity Path Check**:
   ```bash
   python -c "import os; print('Unity path exists:', os.path.exists(os.getenv('UNITY_PATH', 'not set')))"
   ```

3. **Project Structure Check**:
   - Ensure `Assets/` folder exists
   - Ensure `ProjectSettings/` folder exists
   - Ensure at least one scene is in Build Settings

4. **For Android Builds**:
   ```bash
   echo %ANDROID_HOME%  # Windows
   echo $ANDROID_HOME   # macOS/Linux
   ```

### 13. Unity Version Mismatch Issues

**Symptom**: Warning about Unity version mismatch, or builds failing with compatibility errors.

**Understanding the Issue**:
- **Project Unity Version**: Version from `ProjectSettings/ProjectVersion.txt` (what your project expects)
- **Unity Executable Version**: Version extracted from your `.env` UNITY_PATH (what you're building with)

**When Version Mismatch is OK**:
- Minor updates within the same major version (2021.3.16f1 → 2021.3.18f1)
- Using newer Unity to build older projects (usually works)
- LTS to LTS migrations that are well-tested

**When Version Mismatch Causes Problems**:
- Major version differences (2020.x → 2022.x)
- Beta/Alpha versions mixing with stable
- API changes between versions affecting your scripts

**Solutions**:
1. **Install Matching Unity Version**:
   ```bash
   # The script shows which version is expected
   # Install that specific version via Unity Hub
   ```

2. **Update Project to Newer Unity**:
   - Open a project in a newer Unity version
   - Let Unity upgrade the project
   - Check that everything still works

3. **Override Warning** (if you know it's safe):
   - The script will pause and let you continue anyway
   - Press Enter to proceed with the version mismatch

### Getting More Help

If you're still experiencing issues:

1. Check the full build log in `BuildAutomation/build_[platform].log`
2. Look for specific error messages in the Unity Console
3. Verify all prerequisites are installed (Unity modules, SDKs, etc.)
4. Check Unity versions: Compare a project version with an executable version
5. Create an issue on GitHub with:
   - The error message
   - Your Unity version (both project and executable)
   - Your operating system
   - The build log contents

### Debug Mode

To see more detailed output, you can modify the Python script to show Unity's output:

```python
# In platforms.py, change capture_output=True to capture_output=False
result = subprocess.run(cmd, capture_output=False, text=True)
```

This will show Unity's real-time output in your terminal.

### 14. Virtual Environment Issues

**Python packages not found:**
- Ensure virtual environment is activated
- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`
- Reinstall requirements: `pip install -r requirements.txt`

### 15. Google Drive Upload Issues

**"credentials.json not found":**
- Follow [Google Drive Credentials Setup Guide](GoogleCredentialsSetup.md)
- Ensure credentials.json is in BuildAutomation folder
- Never commit credentials.json to version control

**"Invalid folder ID":**
- Get folder ID from Google Drive URL: drive.google.com/drive/folders/[FOLDER_ID]
- Ensure folder exists and you have access

**Authentication errors:**
- Delete gdrive_token.pickle and re-authenticate
- Check that Google Drive API is enabled in your project
- Verify OAuth consent screen is configured

**Email not sending:**
- Use app-specific password, not your regular password
- Check SMTP settings match your provider
- Verify firewall isn't blocking SMTP ports

### 16. Multi-Build Configuration Issues

**Wrong configuration active:**
- Check which .env file is currently in use
- Use switch scripts: `switch-to-recorder.bat` or `switch-to-vr.bat`

**Email prefix not appearing:**
- Verify EMAIL_SUBJECT_PREFIX is set in active .env
- Check you're using latest windows_gdrive_uploader.py

**Build hooks not working:**
- Ensure BuildHooks.cs is in Assets/__Scripts/Editor/
- Verify method names match PRE_BUILD_HOOK in .env
- Check Unity console for hook execution errors

### 17. Dynamic Product Name Changes

The build automation system now supports changing the product name in pre-build hooks!

**How it works:**
- If your hook changes `PlayerSettings.productName`, the system will detect this
- Output files will use the new product name
- Zip files and emails will reflect the actual product name used

**Example hook:**
```csharp
public static void SetDynamicProductName() {
    PlayerSettings.productName = "MyGame - Dev Build";
}
```

**Common use cases:**
- Different names for different build variants
- Adding build numbers or dates to product names
- Branch-specific naming conventions

**Troubleshooting:**
- Look for yellow messages saying "Product name changed from X to Y"
- Check that build_summary.json contains the actual product name
- Verify output files use the new name