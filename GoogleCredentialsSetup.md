# Google Drive Credentials Setup Guide

This guide will walk you through setting up Google Drive API credentials for uploading Windows builds.

## Table of Contents
1. [Create a Google Cloud Project](#1-create-a-google-cloud-project)
2. [Enable Google Drive API](#2-enable-google-drive-api)
3. [Create OAuth 2.0 Credentials](#3-create-oauth-20-credentials)
4. [Download and Configure Credentials](#4-download-and-configure-credentials)
5. [Find Your Google Drive Folder ID](#5-find-your-google-drive-folder-id)
6. [Set Up Email Notifications (Optional)](#6-set-up-email-notifications-optional)
7. [Security Best Practices](#7-security-best-practices)
8. [Troubleshooting](#8-troubleshooting)

## 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "Unity Build Automation")
5. Click "Create"
6. Wait for the project to be created (usually takes 10-30 seconds)

## 2. Enable Google Drive API

1. Make sure your new project is selected in the dropdown
2. Go to the [API Library](https://console.cloud.google.com/apis/library)
3. Search for "Google Drive API"
4. Click on "Google Drive API" in the results
5. Click the "Enable" button
6. Wait for the API to be enabled

## 3. Create OAuth 2.0 Credentials

### Step 1: Configure OAuth Consent Screen

1. Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
2. Select "External" user type (unless you have a Google Workspace account)
3. Click "Create"
4. Fill in the required fields:
   - **App name**: Unity Build Automation
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
5. Click "Save and Continue"
6. On the "Scopes" page, click "Add or Remove Scopes"
7. Search for and select: `https://www.googleapis.com/auth/drive.file`
8. Click "Update" and then "Save and Continue"
9. On the "Test users" page, add your email address
10. Click "Save and Continue"
11. Review and click "Back to Dashboard"

### Step 2: Create OAuth Client ID

1. Go to [Credentials page](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Desktop app" as the application type
4. Name it "Unity Build Automation Desktop"
5. Click "Create"
6. A popup will show your client ID and secret
7. Click "Download JSON"
8. Rename the downloaded file to `credentials.json`
9. Save it in your `BuildAutomation` folder

## 4. Download and Configure Credentials

1. Move `credentials.json` to your `BuildAutomation` folder:
   ```
   Unity-Python-Build-Automation/
   └── BuildAutomation/
       └── credentials.json
   ```

2. **IMPORTANT**: `credentials.json` is already in `.gitignore` - never commit this file!

## 5. Find Your Google Drive Folder ID

1. Open [Google Drive](https://drive.google.com)
2. Create a new folder for your builds (e.g., "Unity Builds")
3. Open the folder
4. Look at the URL in your browser. It will look like:
   ```
   https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J
   ```
5. Copy the ID part after `/folders/` (in this example: `1A2B3C4D5E6F7G8H9I0J`)
6. This is your `GDRIVE_FOLDER_ID`

## 6. Set Up Email Notifications (Optional)

If you want email notifications when builds are uploaded:

### For Gmail:

1. Go to your [Google Account settings](https://myaccount.google.com/)
2. Navigate to "Security"
3. Enable 2-Step Verification if not already enabled
4. Go back to Security → "2-Step Verification"
5. Scroll down and click on "App passwords"
6. Select "Mail" and your device
7. Click "Generate"
8. Copy the 16-character password
9. Use this as your `EMAIL_SMTP_PASSWORD` in `.env`

### For other email providers:

- Check your provider's SMTP settings documentation
- You'll need: SMTP host, port, username, and password/app password

## 7. Security Best Practices

1. **Never share or commit `credentials.json`**
   - It's automatically ignored by git
   - Keep it secure on your local machine

2. **Use App Passwords for Email**
   - Never use your regular password
   - App passwords can be revoked if compromised

3. **Limit Access**
   - The app only requests access to files it creates
   - It cannot access your other Google Drive files

4. **Token Storage**
   - After first authentication, a token is saved locally
   - This token is also gitignored automatically

## 8. Troubleshooting

### "Error 400: redirect_uri_mismatch"
- Make sure you selected "Desktop app" when creating credentials
- Re-download the credentials.json file

### "Access blocked: Authorization Error"
- Your app might still be in "Testing" mode
- Add your email to test users in OAuth consent screen

### "Insufficient Permission"
- Check that you added the Drive API scope
- Delete any existing token and re-authenticate

### Browser doesn't open automatically
- Copy the URL from the console and open it manually
- Complete authentication in your browser

### "Quota exceeded" errors
- Google Drive API has usage limits
- Wait a bit or check your quota in Google Cloud Console

## Next Steps

1. Copy `.env.example` to `.env`
2. Update these values in your `.env` file:
   ```env
   WINDOWS_GDRIVE_ENABLED=true
   GDRIVE_CREDENTIALS_FILE="credentials.json"
   GDRIVE_FOLDER_ID="your-folder-id-here"
   ```
3. Optionally configure email settings
4. Run a test build with `python build_cli.py windows --gdrive-upload`

## Need Help?

- Check the [Google Drive API documentation](https://developers.google.com/drive/api/v3/about-sdk)
- Review the [OAuth 2.0 documentation](https://developers.google.com/identity/protocols/oauth2)
- Create an issue on the [Unity-Python-Build-Automation GitHub repository](https://github.com/angrysharkstudio/Unity-Python-Build-Automation)