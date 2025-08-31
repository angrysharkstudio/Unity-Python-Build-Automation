/*
 * Unity Build Automation - Command Line Build Script
 *
 * MIT License - Copyright (c) 2025 Angry Shark Studio
 * See LICENSE file for full license text
 *
 * This script provides command-line build methods for Unity automation.
 * Place this file in: Assets/Scripts/Editor/CommandLineBuild.cs
 */

using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

// ReSharper disable UnusedMember.Global
// ReSharper disable UnusedType.Global

public static class CommandLineBuild {

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

    public static void BuildWindows() {
        var productName = GetProductName();
        var bundleVersion = GetBundleVersion();
        var outputPath = $"Builds/Windows/{bundleVersion}/{productName}.exe";

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
        var outputPath = $"Builds/Mac/{bundleVersion}/{productName}.app";

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
        var outputPath = $"Builds/Android/{bundleVersion}/{productName}.apk";

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
        var productName = GetProductName();
        var bundleVersion = GetBundleVersion();
        var outputPath = $"Builds/WebGL/{bundleVersion}/{productName}";

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

    // Utility method to verify build setup
    public static void VerifyBuildSetup() {
        var scenes = GetScenePaths();

        if (scenes.Length == 0) {
            Debug.LogError("No scenes in Build Settings! Please add at least one scene.");
            EditorApplication.Exit(1);
        }

        Debug.Log($"Build setup verified:");
        Debug.Log($"- Product Name: {GetProductName()}");
        Debug.Log($"- Bundle Version: {GetBundleVersion()}");
        Debug.Log($"- Scenes ({scenes.Length}): {string.Join(", ", scenes)}");
        Debug.Log($"- Company Name: {PlayerSettings.companyName}");
        Debug.Log($"- Bundle ID: {PlayerSettings.applicationIdentifier}");
    }

}