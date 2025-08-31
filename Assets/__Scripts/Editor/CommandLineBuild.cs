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
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

// ReSharper disable UnusedMember.Global
// ReSharper disable UnusedType.Global

public class CommandLineBuild {

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

    public static void BuildWindows() {
        var productName = GetProductName();
        var bundleVersion = GetBundleVersion();

        // Get an output path from command line arguments
        var outputPath = GetOutputPath("Windows", productName, bundleVersion, ".exe");

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

        var report = BuildPipeline.BuildPlayer(buildPlayerOptions);

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
        var outputPath = GetOutputPath("Mac", productName, bundleVersion, ".app");

        var buildPlayerOptions = new BuildPlayerOptions {
            scenes = GetScenePaths(),
            locationPathName = outputPath,
            target = BuildTarget.StandaloneOSX,
            options = BuildOptions.None
        };

        Debug.Log($"Building Mac: {productName} v{bundleVersion}");
        EnsureDirectoryExists(outputPath);

        var report = BuildPipeline.BuildPlayer(buildPlayerOptions);

        if (report.summary.result != BuildResult.Succeeded) {
            Debug.LogError($"Mac build failed: {report.summary.result}");
            EditorApplication.Exit(1);
        }
    }

    public static void BuildAndroid() {
        var productName = GetProductName();
        var bundleVersion = GetBundleVersion();

        // Get output path from command line arguments
        var outputPath = GetOutputPath("Android", productName, bundleVersion, ".apk");

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

        var report = BuildPipeline.BuildPlayer(buildPlayerOptions);

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
        var outputPath = GetOutputPath("WebGL", productName, bundleVersion, "");

        var buildPlayerOptions = new BuildPlayerOptions {
            scenes = GetScenePaths(),
            locationPathName = outputPath,
            target = BuildTarget.WebGL,
            options = BuildOptions.None
        };

        Debug.Log($"Building WebGL: {productName} v{bundleVersion}");
        EnsureDirectoryExists(outputPath);

        var report = BuildPipeline.BuildPlayer(buildPlayerOptions);

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
        var outputPath = GetOutputPath("iOS", productName, bundleVersion, "");

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

        var report = BuildPipeline.BuildPlayer(buildPlayerOptions);

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