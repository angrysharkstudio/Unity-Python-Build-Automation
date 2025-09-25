/*
 * Unity Build Automation - Command Line Build Script
 *
 * MIT License - Copyright (c) 2025 Angry Shark Studio
 * See LICENSE file for full license text
 *
 * This script provides command-line build methods for Unity automation.
 * Place this file in: Assets/Scripts/Editor/CommandLineBuild.cs
 */

using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

// ReSharper disable UnusedMember.Global
// ReSharper disable UnusedType.Global

public class CommandLineBuild {

    // Build summary data structure for JSON output
    [System.Serializable]
    private class BuildSummary {
        public string status;
        public string platform;
        public string product_name;
        public string version;
        public string timestamp;
        public float build_duration_seconds;
        public string output_path;
        public string unity_version;
        public int warnings_count;
        public List<string> errors;
        public float build_size_mb;
        public int scene_count;
    }

    // Write build summary JSON file
    private static void WriteBuildSummary(BuildReport report, string platform, string outputPath, DateTime buildStartTime) {
        var summary = new BuildSummary {
            status = report.summary.result == BuildResult.Succeeded ? "success" : "failed",
            platform = platform,
            product_name = GetProductName(),
            version = GetBundleVersion(),
            timestamp = DateTime.Now.ToString("yyyy-MM-dd'T'HH:mm:ss"),
            build_duration_seconds = (float)(DateTime.Now - buildStartTime).TotalSeconds,
            output_path = outputPath,
            unity_version = Application.unityVersion,
            warnings_count = 0, // Unity doesn't expose warning count in BuildReport
            errors = new List<string>(),
            build_size_mb = report.summary.totalSize / (1024f * 1024f),
            scene_count = GetScenePaths().Length
        };

        // Add error messages if build failed
        if (report.summary.result != BuildResult.Succeeded) {
            summary.errors.Add(report.summary.result.ToString());
            
            // Add any build step messages that indicate errors
            foreach (var step in report.steps) {
                foreach (var message in step.messages) {
                    if (message.type == LogType.Error || message.type == LogType.Exception) {
                        summary.errors.Add(message.content);
                    }
                }
            }
        }

        // Write to JSON file in the output directory
        var outputDir = Path.GetDirectoryName(outputPath);
        var summaryPath = Path.Combine(outputDir, "build_summary.json");
        
        try {
            var json = JsonUtility.ToJson(summary, true);
            File.WriteAllText(summaryPath, json);
            Debug.Log($"Build summary written to: {summaryPath}");
        } catch (Exception e) {
            Debug.LogError($"Failed to write build summary: {e.Message}");
        }
    }

    // Get scenes from Build Settings (no hardcoding!)
    private static string[] GetScenePaths() {
        return EditorBuildSettings.scenes
            .Where(scene => scene.enabled)
            .Select(scene => scene.path)
            .ToArray();
    }

    // Get the product name from Player Settings
    private static string GetProductName() {
        return PlayerSettings.productName;
    }

    // Get bundle version from Player Settings
    private static string GetBundleVersion() {
        return PlayerSettings.bundleVersion;
    }

    // Ensure the build directory exists
    private static void EnsureDirectoryExists(string filePath) {
        var directory = Path.GetDirectoryName(filePath);

        if (!Directory.Exists(directory)) {
            Directory.CreateDirectory(directory);
            Debug.Log($"Created directory: {directory}");
        }
    }

    // Get output path from command line or use default
    private static string GetOutputPath(string platform, string productName, string bundleVersion, string extension) {
        // Check if an output path was passed via the command line
        var args = Environment.GetCommandLineArgs();

        for (var i = 0; i < args.Length - 1; i++) {
            if (args[i] == "-buildPath" && i + 1 < args.Length) {
                var customPath = args[i + 1];
                Debug.Log($"Using custom build path from command line: {customPath}");

                return customPath;
            }
        }

        // Default behavior: Use a simple version folder without timestamp
        // The Python script will handle finding the most recent build
        var outputPath = $"Builds/{platform}/{bundleVersion}/{productName}{extension}";
        Debug.Log($"Using default build path: {outputPath}");

        return outputPath;
    }

    // Get command line argument value
    private static string GetCommandLineArg(string name) {
        var args = Environment.GetCommandLineArgs();
        for (var i = 0; i < args.Length; i++) {
            if (args[i] == name && i + 1 < args.Length) {
                return args[i + 1];
            }
        }
        return null;
    }

    // Execute pre-build hook if specified
    public static void ExecutePreBuildHook() {
        var hookMethod = GetCommandLineArg("-preBuildHook");
        if (string.IsNullOrEmpty(hookMethod)) {
            Debug.Log("No pre-build hook specified");
            return;
        }

        Debug.Log($"Executing pre-build hook: {hookMethod}");
        
        // Parse format: "ClassName.MethodName"
        var parts = hookMethod.Split('.');
        if (parts.Length != 2) {
            Debug.LogError($"Invalid hook format: {hookMethod}. Expected format: ClassName.MethodName");
            EditorApplication.Exit(1);
            return;
        }

        var className = parts[0];
        var methodName = parts[1];
        
        try {
            // Find the type
            Type type = null;
            foreach (var assembly in AppDomain.CurrentDomain.GetAssemblies()) {
                type = assembly.GetType(className);
                if (type != null) break;
            }
            
            if (type == null) {
                Debug.LogError($"Class not found: {className}");
                Debug.LogError("Make sure the class exists and is in a non-Editor assembly");
                EditorApplication.Exit(1);
                return;
            }
            
            // Find the method
            var method = type.GetMethod(methodName, BindingFlags.Public | BindingFlags.Static);
            if (method == null) {
                Debug.LogError($"Method not found: {methodName} in class {className}");
                Debug.LogError("Make sure the method is public and static");
                EditorApplication.Exit(1);
                return;
            }
            
            // Invoke the method
            Debug.Log($"Invoking {className}.{methodName}()...");
            method.Invoke(null, null);
            Debug.Log($"Pre-build hook completed: {className}.{methodName}");
            
        } catch (Exception e) {
            Debug.LogError($"Error executing pre-build hook: {e.Message}");
            if (e.InnerException != null) {
                Debug.LogError($"Inner exception: {e.InnerException.Message}");
            }
            EditorApplication.Exit(1);
        }
    }

    public static void BuildWindows() {
        var productName = GetProductName();
        var bundleVersion = GetBundleVersion();

        // Get an output path from command line arguments
        var outputPath = GetOutputPath("windows", productName, bundleVersion, ".exe");

        var buildPlayerOptions = new BuildPlayerOptions {
            scenes = GetScenePaths(),
            locationPathName = outputPath,
            target = BuildTarget.StandaloneWindows64,
            options = BuildOptions.None
        };

        Debug.Log($"Building Windows: {productName} v{bundleVersion}");
        Debug.Log($"Scenes: {string.Join(", ", buildPlayerOptions.scenes)}");
        Debug.Log($"Output: {outputPath}");

        EnsureDirectoryExists(outputPath);

        var buildStartTime = DateTime.Now;
        var report = BuildPipeline.BuildPlayer(buildPlayerOptions);

        // Write build summary
        WriteBuildSummary(report, "windows", outputPath, buildStartTime);

        if (report.summary.result == BuildResult.Succeeded) {
            Debug.Log("Windows build succeeded!");
        } else {
            Debug.LogError($"Windows build failed: {report.summary.result}");
            // Exit with error code for Python to detect
            EditorApplication.Exit(1);
        }
    }

    public static void BuildMac() {
        var productName = GetProductName();
        var bundleVersion = GetBundleVersion();

        // Get an output path from command line arguments
        var outputPath = GetOutputPath("mac", productName, bundleVersion, ".app");

        var buildPlayerOptions = new BuildPlayerOptions {
            scenes = GetScenePaths(),
            locationPathName = outputPath,
            target = BuildTarget.StandaloneOSX,
            options = BuildOptions.None
        };

        Debug.Log($"Building Mac: {productName} v{bundleVersion}");
        EnsureDirectoryExists(outputPath);

        var buildStartTime = DateTime.Now;
        var report = BuildPipeline.BuildPlayer(buildPlayerOptions);

        // Write build summary
        WriteBuildSummary(report, "mac", outputPath, buildStartTime);

        if (report.summary.result != BuildResult.Succeeded) {
            Debug.LogError($"Mac build failed: {report.summary.result}");
            EditorApplication.Exit(1);
        }
    }

    public static void BuildAndroid() {
        var productName = GetProductName();
        var bundleVersion = GetBundleVersion();

        // Get output path from command line arguments
        var outputPath = GetOutputPath("android", productName, bundleVersion, ".apk");

        // Note: Android signing should be configured in Player Settings
        // or passed via command line arguments for production builds

        var buildPlayerOptions = new BuildPlayerOptions {
            scenes = GetScenePaths(),
            locationPathName = outputPath,
            target = BuildTarget.Android,
            options = BuildOptions.None
        };

        Debug.Log($"Building Android: {productName} v{bundleVersion}");
        EnsureDirectoryExists(outputPath);

        var buildStartTime = DateTime.Now;
        var report = BuildPipeline.BuildPlayer(buildPlayerOptions);

        // Write build summary
        WriteBuildSummary(report, "android", outputPath, buildStartTime);

        if (report.summary.result != BuildResult.Succeeded) {
            Debug.LogError($"Android build failed: {report.summary.result}");
            EditorApplication.Exit(1);
        }
    }

    public static void BuildWebGL() {
        // Check if WebGL module is installed
        if (!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.WebGL, BuildTarget.WebGL)) {
            Debug.LogError("WebGL module not installed! Please install WebGL Build Support in Unity Hub.");
            EditorApplication.Exit(1);
        }

        var productName = GetProductName();
        var bundleVersion = GetBundleVersion();

        // Get an output path from command line arguments
        var outputPath = GetOutputPath("webgl", productName, bundleVersion, "");

        var buildPlayerOptions = new BuildPlayerOptions {
            scenes = GetScenePaths(),
            locationPathName = outputPath,
            target = BuildTarget.WebGL,
            options = BuildOptions.None
        };

        Debug.Log($"Building WebGL: {productName} v{bundleVersion}");
        EnsureDirectoryExists(outputPath);

        var buildStartTime = DateTime.Now;
        var report = BuildPipeline.BuildPlayer(buildPlayerOptions);

        // Write build summary
        WriteBuildSummary(report, "webgl", outputPath, buildStartTime);

        if (report.summary.result != BuildResult.Succeeded) {
            Debug.LogError($"WebGL build failed: {report.summary.result}");
            EditorApplication.Exit(1);
        }
    }

    public static void BuildiOS() {
        // Check if running on macOS
        if (Application.platform != RuntimePlatform.OSXEditor) {
            Debug.LogError("iOS builds can only be created on macOS!");
            EditorApplication.Exit(1);
        }

        // Check if an iOS module is installed
        if (!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.iOS, BuildTarget.iOS)) {
            Debug.LogError("iOS module not installed! Please install iOS Build Support in Unity Hub.");
            EditorApplication.Exit(1);
        }

        // Ensure bundle identifier is set
        var bundleId = PlayerSettings.GetApplicationIdentifier(BuildTargetGroup.iOS);

        if (string.IsNullOrEmpty(bundleId) || bundleId == "com.Company.ProductName") {
            Debug.LogError("iOS Bundle Identifier not set properly in Player Settings!");
            Debug.LogError("Please set a valid bundle identifier (e.g., com.yourcompany.yourproduct)");
            EditorApplication.Exit(1);
        }

        var productName = GetProductName();
        var bundleVersion = GetBundleVersion();

        // Get output path from command line arguments
        var outputPath = GetOutputPath("ios", productName, bundleVersion, "");

        var buildPlayerOptions = new BuildPlayerOptions {
            scenes = GetScenePaths(),
            locationPathName = outputPath,
            target = BuildTarget.iOS,
            options = BuildOptions.None
        };

        Debug.Log($"Building iOS Xcode Project: {productName} v{bundleVersion}");
        Debug.Log($"Bundle Identifier: {bundleId}");
        Debug.Log($"Note: This will create an Xcode project, not a final iOS app");
        EnsureDirectoryExists(outputPath);

        var buildStartTime = DateTime.Now;
        var report = BuildPipeline.BuildPlayer(buildPlayerOptions);

        // Write build summary
        WriteBuildSummary(report, "ios", outputPath, buildStartTime);

        if (report.summary.result != BuildResult.Succeeded) {
            Debug.LogError($"iOS build failed: {report.summary.result}");
            EditorApplication.Exit(1);
        } else {
            Debug.Log("iOS Xcode project created successfully!");
            Debug.Log("Open the project in Xcode to build and deploy to iOS devices");
        }
    }

    // Utility method to verify build setup
    public static void VerifyBuildSetup() {
        var scenes = GetScenePaths();

        if (scenes.Length == 0) {
            Debug.LogError("No scenes in Build Settings! Please add at least one scene.");
            EditorApplication.Exit(1);
        }

        Debug.Log("Build setup verified:");
        Debug.Log($"- Product Name: {GetProductName()}");
        Debug.Log($"- Bundle Version: {GetBundleVersion()}");
        Debug.Log($"- Scenes ({scenes.Length}): {string.Join(", ", scenes)}");
        Debug.Log($"- Company Name: {PlayerSettings.companyName}");
        Debug.Log($"- Bundle ID: {PlayerSettings.applicationIdentifier}");
    }

}

// Example pre-build hook class that users can copy and modify
// This should be placed in a non-Editor script file in the project
/*
public class BuildHooks {
    
    // Example: Switch to production environment
    public static void SwitchToProduction() {
        Debug.Log("[BuildHooks] Switching to production environment...");
        // Add your custom logic here, for example:
        // - Change server URLs
        // - Update API keys
        // - Set production flags
        // PlayerSettings.SetScriptingDefineSymbolsForGroup(BuildTargetGroup.WebGL, "PRODUCTION");
    }
    
    // Example: Increment build number
    public static void IncrementBuildNumber() {
        var currentVersion = PlayerSettings.bundleVersion;
        Debug.Log($"[BuildHooks] Current version: {currentVersion}");
        
        // Parse version (assumes format like "1.0.0" or "1.0.0.123")
        var parts = currentVersion.Split('.');
        if (parts.Length >= 3) {
            int buildNumber = 0;
            if (parts.Length > 3) {
                int.TryParse(parts[3], out buildNumber);
            }
            buildNumber++;
            
            var newVersion = $"{parts[0]}.{parts[1]}.{parts[2]}.{buildNumber}";
            PlayerSettings.bundleVersion = newVersion;
            Debug.Log($"[BuildHooks] New version: {newVersion}");
        }
    }
    
    // Example: Prepare for WebGL deployment
    public static void PrepareWebGLDeployment() {
        Debug.Log("[BuildHooks] Preparing for WebGL deployment...");
        // WebGL-specific settings
        PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Gzip;
        PlayerSettings.WebGL.template = "APPLICATION:Default";
        // Add any other WebGL-specific configurations
    }
}
*/