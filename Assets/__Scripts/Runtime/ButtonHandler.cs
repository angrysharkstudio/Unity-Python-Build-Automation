/*
 * Unity Build Automation - Command Line Build Script
 *
 * MIT License - Copyright (c) 2025 Angry Shark Studio
 * See LICENSE file for full license text
 *
 */
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class ButtonHandler : MonoBehaviour {

    [SerializeField] private Button button;
    [SerializeField] private TextMeshProUGUI textToChange;

    private int clickCount;

    private void OnEnable() {
        button.onClick.AddListener(OnButtonClick);
    }

    private void OnDisable() {
        button.onClick.RemoveListener(OnButtonClick);
    }

    private void OnButtonClick() {
        clickCount++;
        textToChange.text = $"Clicked {clickCount} times!";
        Debug.Log($"Button clicked {clickCount} times");
    }

    private void OnValidate() {
        if (!button) {
            button = GetComponent<Button>();
        }
    }

}