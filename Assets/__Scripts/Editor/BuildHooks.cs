/*
 * Unity Build Automation - Build Hooks Example
 *
 * This file demonstrates how to create pre-build hooks that can be called
 * before Unity builds to configure scenes, settings, and other build parameters.
 *
 * Usage:
 * 1. Copy this file to your project and modify for your needs
 * 2. Update scene paths to match your actual scenes
 * 3. Reference these methods in your .env file:
 *    PRE_BUILD_HOOK="BuildHooks.SelectProject1Scenes"
 *
 * MIT License - Copyright (c) 2025 Angry Shark Studio
 */

using System;
using UnityEngine;
using UnityEditor;

public class BuildHooks {
    
    // Example: Configure build for Project 1 (e.g., "Recorder" variant)
    public static void SelectProject1Scenes() {
        Debug.Log("[BuildHooks] Configuring build for Project 1...");
        
        // Clear existing scenes and add Project 1 specific scenes
        EditorBuildSettings.scenes = new[] {
            new EditorBuildSettingsScene("Assets/Scenes/Project1/MainScene.unity", true),
            // new EditorBuildSettingsScene("Assets/Scenes/Project1/UIScene.unity", true)
        };
        
        // Optional: Set project-specific settings
        // NOTE: Changing ProductName here is supported! The build automation
        // system will detect the change and use the new name for output files.
        PlayerSettings.productName = "MyGame - Project 1";
        // PlayerSettings.bundleVersion = "1.0.0-project1";
        
        // Optional: Configure project-specific defines
        // PlayerSettings.SetScriptingDefineSymbolsForGroup(
        //     BuildTargetGroup.Standalone, 
        //     "PROJECT1_BUILD;ENABLE_FEATURE_X"
        // );
        
        Debug.Log($"[BuildHooks] Configured {EditorBuildSettings.scenes.Length} scenes for Project 1");
        Debug.Log("[BuildHooks] Project 1 configuration complete!");
    }
    
    // Example: Configure build for Project 2 (e.g., "VR" variant)
    public static void SelectProject2Scenes() {
        Debug.Log("[BuildHooks] Configuring build for Project 2...");
        
        // Clear existing scenes and add Project 2 specific scenes
        EditorBuildSettings.scenes = new[] {
            new EditorBuildSettingsScene("Assets/Scenes/Project2/GameScene.unity", true),
            // new EditorBuildSettingsScene("Assets/Scenes/Project2/MenuScene.unity", true),
            // new EditorBuildSettingsScene("Assets/Scenes/Project2/LoadingScene.unity", true)
        };
        
        // Optional: Set project-specific settings
        PlayerSettings.productName = "MyGame - Project 2";
        // PlayerSettings.bundleVersion = "1.0.0-project2";
        
        // Optional: Configure project-specific defines
        // PlayerSettings.SetScriptingDefineSymbolsForGroup(
        //     BuildTargetGroup.Standalone, 
        //     "PROJECT2_BUILD;ENABLE_VR;ENABLE_FEATURE_Y"
        // );
        
        Debug.Log($"[BuildHooks] Configured {EditorBuildSettings.scenes.Length} scenes for Project 2");
        Debug.Log("[BuildHooks] Project 2 configuration complete!");
    }
    
    // Example: Development build configuration
    public static void ConfigureDevelopmentBuild() {
        Debug.Log("[BuildHooks] Configuring development build...");
        
        // Enable development build settings
        EditorUserBuildSettings.development = true;
        EditorUserBuildSettings.allowDebugging = true;
        EditorUserBuildSettings.connectProfiler = true;
        
        // Add debug scenes
        var currentScenes = EditorBuildSettings.scenes;
        var scenesWithDebug = new EditorBuildSettingsScene[currentScenes.Length + 1];
        Array.Copy(currentScenes, scenesWithDebug, currentScenes.Length);
        scenesWithDebug[currentScenes.Length] = new EditorBuildSettingsScene(
            "Assets/Scenes/Debug/DebugConsole.unity", true
        );
        EditorBuildSettings.scenes = scenesWithDebug;
        
        Debug.Log("[BuildHooks] Development build configuration complete!");
    }
    
    // Example: Production build configuration
    public static void ConfigureProductionBuild() {
        Debug.Log("[BuildHooks] Configuring production build...");
        
        // Disable development build settings
        EditorUserBuildSettings.development = false;
        EditorUserBuildSettings.allowDebugging = false;
        EditorUserBuildSettings.connectProfiler = false;
        
        // Set production defines
        PlayerSettings.SetScriptingDefineSymbolsForGroup(
            BuildTargetGroup.Standalone, 
            "PRODUCTION_BUILD;DISABLE_DEBUG_FEATURES"
        );
        
        // Optional: Set production API endpoints, keys, etc.
        Debug.Log("[BuildHooks] Production build configuration complete!");
    }
    
    // Example: Configure specific scene by name
    public static void SelectSingleScene() {
        Debug.Log("[BuildHooks] Configuring single scene build...");
        
        var sceneName = GetCommandLineArg("-sceneName");
        if (string.IsNullOrEmpty(sceneName)) {
            Debug.LogError("[BuildHooks] No scene name provided! Use -sceneName parameter");
            return;
        }
        
        EditorBuildSettings.scenes = new[] {
            new EditorBuildSettingsScene($"Assets/Scenes/{sceneName}.unity", true)
        };
        
        Debug.Log($"[BuildHooks] Configured build with scene: {sceneName}");
    }
    
    // Helper: Get command line argument value
    private static string GetCommandLineArg(string name) {
        var args = Environment.GetCommandLineArgs();
        for (int i = 0; i < args.Length; i++) {
            if (args[i] == name && i + 1 < args.Length) {
                return args[i + 1];
            }
        }
        return null;
    }
    
    // Example: Switch to different environment configurations
    public static void SwitchToTestEnvironment() {
        Debug.Log("[BuildHooks] Switching to TEST environment...");
        PlayerSettings.SetScriptingDefineSymbolsForGroup(
            BuildTargetGroup.Standalone, 
            "TEST_ENVIRONMENT;USE_TEST_SERVERS"
        );
    }
    
    public static void SwitchToStagingEnvironment() {
        Debug.Log("[BuildHooks] Switching to STAGING environment...");
        PlayerSettings.SetScriptingDefineSymbolsForGroup(
            BuildTargetGroup.Standalone, 
            "STAGING_ENVIRONMENT;USE_STAGING_SERVERS"
        );
    }
    
    public static void SwitchToProductionEnvironment() {
        Debug.Log("[BuildHooks] Switching to PRODUCTION environment...");
        PlayerSettings.SetScriptingDefineSymbolsForGroup(
            BuildTargetGroup.Standalone, 
            "PRODUCTION_ENVIRONMENT;USE_PRODUCTION_SERVERS"
        );
    }
    
    // Example: Dynamic product naming based on build type
    // This demonstrates how the build automation handles ProductName changes
    public static void SetProductNameForBranch() {
        Debug.Log("[BuildHooks] Setting product name based on git branch...");
        
        // Example: Get current git branch (you'd implement this based on your needs)
        // string branchName = GetCurrentGitBranch();
        string branchName = "feature/new-ui"; // Example
        
        // Set product name based on branch
        if (branchName.StartsWith("release/")) {
            PlayerSettings.productName = "MyGame";
        } else if (branchName.StartsWith("feature/")) {
            string featureName = branchName.Replace("feature/", "").Replace("-", " ");
            PlayerSettings.productName = $"MyGame Dev - {featureName}";
        } else {
            PlayerSettings.productName = $"MyGame - {branchName}";
        }
        
        Debug.Log($"[BuildHooks] Product name set to: {PlayerSettings.productName}");
        // The build automation will automatically detect this change and:
        // - Output files will use the new product name
        // - Zip files will be named correctly
        // - Email notifications will show the actual product name
    }
    
    // Example: Add build metadata to product name
    public static void AddBuildMetadataToProductName() {
        Debug.Log("[BuildHooks] Adding build metadata to product name...");
        
        string originalName = PlayerSettings.productName;
        string buildNumber = GetCommandLineArg("-buildNumber") ?? "local";
        string timestamp = DateTime.Now.ToString("MMdd");
        
        // Append build info to product name
        PlayerSettings.productName = $"{originalName}_B{buildNumber}_{timestamp}";
        
        Debug.Log($"[BuildHooks] Product name changed from '{originalName}' to '{PlayerSettings.productName}'");
        // The Python build system will handle this gracefully!
    }
}