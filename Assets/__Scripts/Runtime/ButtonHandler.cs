/*
 * Unity Build Automation - Command Line Build Script
 *
 * MIT License - Copyright (c) 2025 Angry Shark Studio
 * See LICENSE file for full license text
 *
 * Usage:
 * 1. Import TextMeshPro package in Unity
 * 2. Attach this script to a GameObject
 * 3. Drag Button and TextMeshProUGUI components in Inspector
 */

using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class ButtonHandler : MonoBehaviour {

    [Header("UI References")]
    [SerializeField] private Button button;
    [SerializeField] private TextMeshProUGUI textToChange;

    [Header("Settings")]
    [SerializeField] private string clickTextFormat = "Clicked {0} times!";
    [SerializeField] private string initialText = "Hello Build Automation!";

    private int clickCount;

    private void Awake() {
        // Initialize text on awake
        if (textToChange != null) {
            textToChange.text = initialText;
        }
    }

    private void OnEnable() {
        // Subscribe to button click event
        if (button != null) {
            button.onClick.AddListener(OnButtonClick);
        }
    }

    private void OnDisable() {
        // Unsubscribe from the button click event
        if (button != null) {
            button.onClick.RemoveListener(OnButtonClick);
        }
    }

    private void OnButtonClick() {
        clickCount++;

        // Update text
        if (textToChange != null) {
            textToChange.text = string.Format(clickTextFormat, clickCount);
        }

        // Log click for debugging
        Debug.Log($"Button clicked {clickCount} times");

        // Optional: Add visual feedback
        StartCoroutine(AnimateClick());
    }

    private IEnumerator AnimateClick() {
        if (textToChange == null) {
            yield break;
        }

        // Simple scale animation
        var originalScale = textToChange.transform.localScale;
        textToChange.transform.localScale = originalScale * 1.1f;

        yield return new WaitForSeconds(0.1f);

        textToChange.transform.localScale = originalScale;
    }

    private void OnValidate() {
        // Auto-assign button if not set
        if (button == null) {
            button = GetComponent<Button>();
        }

        // Try to find TextMeshProUGUI in children if not set
        if (textToChange == null) {
            textToChange = GetComponentInChildren<TextMeshProUGUI>();
        }
    }

}