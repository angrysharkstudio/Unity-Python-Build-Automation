"""
Windows Google Drive upload module for Unity Build Automation.
Handles zipping Windows builds (excluding debug folders) and uploading to Google Drive.

MIT License - Copyright (c) 2025 Angry Shark Studio
"""

import os
import zipfile
import pickle
import smtplib
from pathlib import Path
from typing import Tuple, Optional, List, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel

console = Console()

# If modifying these scopes, delete the token file.
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class WindowsGDriveUploader:
    """Handles Google Drive uploads for Windows builds."""
    
    # Folders to exclude from zip
    EXCLUDE_PATTERNS = [
        '*_BackUpThisFolder_ButDontShipItWithYourGame',
        '*_DoNotShip',
        '*_BurstDebugInformation_DoNotShip'
    ]
    
    def __init__(self, config: Any) -> None:
        """Initialize with configuration object."""
        self.config = config
        self.gdrive_enabled = os.getenv('WINDOWS_GDRIVE_ENABLED', 'false').lower() == 'true'
        self.credentials_file = os.getenv('GDRIVE_CREDENTIALS_FILE', 'credentials.json')
        self.folder_id = os.getenv('GDRIVE_FOLDER_ID', '')
        
        # Email settings
        self.email_enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
        self.smtp_host = os.getenv('EMAIL_SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.smtp_username = os.getenv('EMAIL_SMTP_USERNAME', '')
        self.smtp_password = os.getenv('EMAIL_SMTP_PASSWORD', '')
        self.email_from = os.getenv('EMAIL_FROM', '')
        self.email_to = os.getenv('EMAIL_TO', '').split(',')
        self.email_subject_prefix = os.getenv('EMAIL_SUBJECT_PREFIX', '')
        
        self.service = None
    
    def is_configured(self) -> bool:
        """Check if Google Drive upload is properly configured."""
        if not self.gdrive_enabled:
            return False
        
        if not self.folder_id:
            console.print("[yellow]Windows Google Drive upload is enabled but GDRIVE_FOLDER_ID is not set[/]")
            return False
        
        # Check if credentials file exists
        creds_path = Path(self.credentials_file)
        if not creds_path.exists():
            creds_path = Path(__file__).parent.parent / self.credentials_file
            if not creds_path.exists():
                console.print(f"[yellow]Credentials file not found: {self.credentials_file}[/]")
                console.print("[yellow]Please follow docs/GoogleCredentialsSetup.md to set up credentials[/]")
                return False
        
        return True
    
    def authenticate(self) -> bool:
        """Authenticate with Google Drive API."""
        try:
            creds = None
            token_file = 'gdrive_token.pickle'
            
            # Load existing token
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    console.print("[cyan]Refreshing Google Drive authentication...[/]")
                    creds.refresh(Request())
                else:
                    console.print("[cyan]Authenticating with Google Drive...[/]")
                    # Find credentials file
                    creds_path = Path(self.credentials_file)
                    if not creds_path.exists():
                        creds_path = Path(__file__).parent.parent / self.credentials_file
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(creds_path), SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('drive', 'v3', credentials=creds)
            console.print("[green]Successfully authenticated with Google Drive[/]")
            return True
            
        except Exception as e:
            console.print(f"[red]Authentication failed:[/] {str(e)}")
            return False
    
    def should_exclude(self, path: Path) -> bool:
        """Check if a file or folder should be excluded from the zip."""
        path_str = str(path)
        
        # Check each exclude pattern
        for pattern in self.EXCLUDE_PATTERNS:
            if pattern.startswith('*'):
                # Suffix pattern
                suffix = pattern[1:]
                if path_str.endswith(suffix):
                    return True
            elif pattern.endswith('*'):
                # Prefix pattern
                prefix = pattern[:-1]
                if path_str.startswith(prefix):
                    return True
            elif '*' in pattern:
                # Wildcard in middle (like *.pdb)
                import fnmatch
                if fnmatch.fnmatch(path.name, pattern):
                    return True
            else:
                # Exact match
                if path.name == pattern:
                    return True
        
        return False
    
    def create_zip(self, build_path: Path, output_path: Path) -> Tuple[bool, Optional[str]]:
        """Create a zip file from the build directory, excluding debug folders."""
        try:
            console.print(f"\n[cyan]Creating zip file:[/] {output_path.name}")
            
            # Collect files to zip (excluding debug folders)
            files_to_zip = []
            total_size = 0
            excluded_count = 0
            
            for root, dirs, files in os.walk(build_path):
                root_path = Path(root)
                
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not self.should_exclude(root_path / d)]
                
                for file in files:
                    file_path = root_path / file
                    if not self.should_exclude(file_path):
                        files_to_zip.append(file_path)
                        total_size += file_path.stat().st_size
                    else:
                        excluded_count += 1
            
            if excluded_count > 0:
                console.print(f"[dim]Excluding {excluded_count} debug files/folders[/]")
            
            # Create zip with progress
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                
                task = progress.add_task("Compressing files...", total=len(files_to_zip))
                
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for file_path in files_to_zip:
                        # Calculate relative path within the build
                        # We want files at the root of the zip, not in a subfolder
                        rel_path = file_path.relative_to(build_path)
                        zf.write(file_path, rel_path)
                        progress.update(task, advance=1)
            
            # Calculate compression ratio
            zip_size = output_path.stat().st_size
            compression_ratio = (1 - zip_size / total_size) * 100 if total_size > 0 else 0
            
            console.print(f"[green]Zip created successfully![/]")
            console.print(f"   [dim]Original size: {total_size / (1024*1024):.1f} MB[/]")
            console.print(f"   [dim]Compressed size: {zip_size / (1024*1024):.1f} MB[/]")
            console.print(f"   [dim]Compression ratio: {compression_ratio:.1f}%[/]")
            
            return True, f"Zip created: {output_path.name}"
            
        except Exception as e:
            console.print(f"[red]Failed to create zip:[/] {str(e)}")
            return False, f"Zip creation failed: {str(e)}"
    
    def upload_to_drive(self, file_path: Path) -> Tuple[bool, Optional[str], Optional[str]]:
        """Upload file to Google Drive and return success status, message, and share link."""
        if not self.service:
            return False, "Not authenticated with Google Drive", None
        
        try:
            console.print(f"\n[cyan]Uploading to Google Drive...[/]")
            
            file_metadata = {
                'name': file_path.name,
                'parents': [self.folder_id]
            }
            
            # Check if file already exists in the folder
            query = f"'{self.folder_id}' in parents and name = '{file_path.name}' and trashed = false"
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            existing_files = results.get('files', [])
            
            if existing_files:
                # Update existing file
                file_id = existing_files[0]['id']
                console.print(f"[yellow]File already exists, updating...[/]")
                media = MediaFileUpload(str(file_path), resumable=True)
                
                # Update the file
                file = self.service.files().update(
                    fileId=file_id,
                    media_body=media,
                    fields='id'
                ).execute()
            else:
                # Create new file
                media = MediaFileUpload(str(file_path), resumable=True)
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                file_id = file.get('id')
            
            # Create shareable link
            console.print("[cyan]Creating shareable link...[/]")
            self.service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            # Get the shareable link
            file = self.service.files().get(
                fileId=file_id,
                fields='webViewLink'
            ).execute()
            
            share_link = file.get('webViewLink')
            
            console.print(f"[green]Upload successful![/]")
            console.print(f"[green]Share link:[/] {share_link}")
            
            return True, "Upload successful", share_link
            
        except HttpError as e:
            console.print(f"[red]Google Drive API error:[/] {str(e)}")
            return False, f"Upload failed: {str(e)}", None
        except Exception as e:
            console.print(f"[red]Upload error:[/] {str(e)}")
            return False, f"Upload failed: {str(e)}", None
    
    def send_email_notification(self, build_info: dict, share_link: str) -> bool:
        """Send email notification with build information and download link."""
        if not self.email_enabled:
            return True
        
        if not all([self.smtp_username, self.smtp_password, self.email_from, self.email_to]):
            console.print("[yellow]Email not configured properly, skipping notification[/]")
            return False
        
        try:
            console.print("\n[cyan]Sending email notification...[/]")
            
            # Create message
            msg = MIMEMultipart('alternative')
            # Build subject with optional prefix
            if self.email_subject_prefix:
                msg['Subject'] = f"{self.email_subject_prefix} - Unity Windows Build Ready - v{build_info['version']}"
            else:
                msg['Subject'] = f"Unity Windows Build Ready - v{build_info['version']}"
            msg['From'] = self.email_from
            msg['To'] = ', '.join(self.email_to)
            
            # Create the HTML content
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>Unity Windows Build Completed</h2>
                
                <p>A new Windows build has been uploaded to Google Drive and is ready for download.</p>
                
                <table style="border-collapse: collapse; margin: 20px 0;">
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Project:</td>
                        <td style="padding: 8px;">{build_info.get('project_name', 'Unknown')}</td>
                    </tr>
                    <tr style="background-color: #f5f5f5;">
                        <td style="padding: 8px; font-weight: bold;">Version:</td>
                        <td style="padding: 8px;">{build_info.get('version', 'Unknown')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Build Time:</td>
                        <td style="padding: 8px;">{build_info.get('build_time', 'Unknown')}</td>
                    </tr>
                    <tr style="background-color: #f5f5f5;">
                        <td style="padding: 8px; font-weight: bold;">File Size:</td>
                        <td style="padding: 8px;">{build_info.get('file_size', 'Unknown')}</td>
                    </tr>
                </table>
                
                <p style="margin-top: 30px;">
                    <a href="{share_link}" style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Download Build
                    </a>
                </p>
                
                <p style="margin-top: 30px; color: #666; font-size: 12px;">
                    This build was automatically generated and uploaded by Unity Python Build Automation.
                </p>
            </body>
            </html>
            """
            
            # Create plain text alternative
            text = f"""Unity Windows Build Completed

A new Windows build has been uploaded to Google Drive.

Project: {build_info.get('project_name', 'Unknown')}
Version: {build_info.get('version', 'Unknown')}
Build Time: {build_info.get('build_time', 'Unknown')}
File Size: {build_info.get('file_size', 'Unknown')}

Download Link: {share_link}

This build was automatically generated by Unity Python Build Automation.
"""
            
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            console.print(f"[green]Email sent to:[/] {', '.join(self.email_to)}")
            return True
            
        except Exception as e:
            console.print(f"[red]Failed to send email:[/] {str(e)}")
            return False
    
    def upload_windows_build(self, build_path: Path) -> Tuple[bool, str]:
        """Main method to zip and upload Windows build to Google Drive."""
        if not self.is_configured():
            return False, "Google Drive not configured"
        
        if not build_path.exists():
            return False, f"Build path not found: {build_path}"
        
        # Authenticate
        if not self.authenticate():
            return False, "Authentication failed"
        
        try:
            # Extract actual product name from the exe file in the directory
            actual_product_name = None
            if build_path.is_dir():
                # Find the main exe file
                exe_files = list(build_path.glob("*.exe"))
                for exe in exe_files:
                    # Skip crash handler
                    if exe.name != "UnityCrashHandler64.exe":
                        actual_product_name = exe.stem
                        break
                
                if not actual_product_name:
                    # Fallback to config name
                    actual_product_name = self.config.project_name
            else:
                # If somehow it's a file path (shouldn't happen with current code)
                actual_product_name = build_path.stem
            
            # Generate clean zip filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            zip_filename = f"{actual_product_name}_Windows_v{self.config.project_version}_{timestamp}.zip"
            zip_path = build_path.parent / zip_filename
            
            # Show upload info panel
            panel = Panel(
                f"[cyan]Build:[/] {build_path}\n"
                f"[cyan]Zip:[/] {zip_filename}\n"
                f"[cyan]Destination:[/] Google Drive/{self.folder_id}",
                title="Windows Build Upload",
                border_style="cyan"
            )
            console.print(panel)
            
            # Create zip
            zip_success, zip_message = self.create_zip(build_path, zip_path)
            if not zip_success:
                return False, zip_message
            
            # Upload to Google Drive
            upload_success, upload_message, share_link = self.upload_to_drive(zip_path)
            
            if upload_success and share_link:
                # Prepare build info for email
                build_info = {
                    'project_name': actual_product_name,  # Use actual product name from build
                    'version': self.config.project_version,
                    'build_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'file_size': f"{zip_path.stat().st_size / (1024*1024):.1f} MB"
                }
                
                # Send email notification
                self.send_email_notification(build_info, share_link)
                
                # Clean up local zip file (optional - uncomment if desired)
                # zip_path.unlink()
                # console.print("[dim]Local zip file deleted[/]")
                
                return True, f"Build uploaded successfully! Share link: {share_link}"
            else:
                # Clean up zip file on failure
                if zip_path.exists():
                    zip_path.unlink()
                return False, upload_message
                
        except Exception as e:
            console.print(f"[red]Unexpected error:[/] {str(e)}")
            return False, f"Upload failed: {str(e)}"