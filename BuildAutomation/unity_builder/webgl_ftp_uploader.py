"""
WebGL FTP upload module for Unity Build Automation.
Handles uploading WebGL builds to FTP servers with progress tracking.

MIT License - Copyright (c) 2025 Angry Shark Studio
"""

import os
import ftplib
import ssl
from pathlib import Path
from typing import Tuple, Optional, Any, List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel

console = Console()


class WebGLFTPUploader:
    """Handles FTP uploads for WebGL builds."""
    
    def __init__(self, config: Any) -> None:
        """Initialize with configuration object."""
        self.config = config
        self.ftp_enabled = os.getenv('WEBGL_FTP_ENABLED', 'false').lower() == 'true'
        self.ftp_host = os.getenv('WEBGL_FTP_HOST', '')
        self.ftp_port = int(os.getenv('WEBGL_FTP_PORT', '21'))
        self.ftp_username = os.getenv('WEBGL_FTP_USERNAME', '')
        self.ftp_password = os.getenv('WEBGL_FTP_PASSWORD', '')
        self.ftp_remote_path = os.getenv('WEBGL_FTP_REMOTE_PATH', '/public_html/games')
        self.ftp_use_tls = os.getenv('WEBGL_FTP_USE_TLS', 'false').lower() == 'true'
        self.ftp_overwrite = os.getenv('WEBGL_FTP_OVERWRITE', 'true').lower() == 'true'
        
        self.ftp: Optional[Any] = None
    
    def is_configured(self) -> bool:
        """Check if FTP upload is properly configured."""
        if not self.ftp_enabled:
            return False
        
        if not all([self.ftp_host, self.ftp_username, self.ftp_password]):
            console.print("[yellow]WebGL FTP upload is enabled but not fully configured[/]")
            console.print("Please check WEBGL_FTP_HOST, WEBGL_FTP_USERNAME, and WEBGL_FTP_PASSWORD in .env")
            return False
        
        return True
    
    def connect(self) -> bool:
        """Connect to FTP server."""
        try:
            console.print(f"\n[cyan]Connecting to FTP server:[/] {self.ftp_host}:{self.ftp_port}")
            
            if self.ftp_use_tls:
                # Use FTPS (FTP over TLS)
                context = ssl.create_default_context()
                # Option to disable certificate verification for self-signed certs
                if os.getenv('WEBGL_FTP_VERIFY_CERT', 'true').lower() == 'false':
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    console.print("[yellow]Warning: Certificate verification disabled[/]")
                
                self.ftp = ftplib.FTP_TLS(context=context)
                self.ftp.connect(self.ftp_host, self.ftp_port, timeout=30)
                self.ftp.login(self.ftp_username, self.ftp_password)
                # Secure the data connection
                self.ftp.prot_p()
                console.print("[green]Connected via FTPS (secure)[/]")
            else:
                # Use regular FTP
                self.ftp = ftplib.FTP()
                self.ftp.connect(self.ftp_host, self.ftp_port, timeout=30)
                self.ftp.login(self.ftp_username, self.ftp_password)
                console.print("[yellow]Connected via FTP (consider using FTPS for security)[/]")
            
            # Set binary mode
            self.ftp.set_pasv(True)
            
            return True
            
        except Exception as e:
            console.print(f"[red]FTP connection failed:[/] {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from FTP server."""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                pass
            self.ftp = None
    
    def ensure_remote_directory(self, remote_dir: str) -> None:
        """Create remote directory if it doesn't exist."""
        # Save current directory
        try:
            original_dir = self.ftp.pwd()
        except:
            original_dir = '/'
        
        parts = remote_dir.strip('/').split('/')
        current_path = ''
        
        for part in parts:
            current_path += '/' + part
            try:
                self.ftp.cwd(current_path)
            except ftplib.error_perm:
                # Directory doesn't exist, create it
                try:
                    self.ftp.mkd(current_path)
                    console.print(f"[dim]Created remote directory: {current_path}[/]")
                    self.ftp.cwd(current_path)
                except:
                    pass
        
        # Return to original directory
        try:
            self.ftp.cwd(original_dir)
        except:
            pass
    
    def upload_file(self, local_file: Path, remote_file: str, progress_task: Optional[Any] = None, progress: Optional[Any] = None) -> bool:
        """Upload a single file to FTP server."""
        try:
            file_size = local_file.stat().st_size
            uploaded_size = 0
            
            def callback(data):
                nonlocal uploaded_size
                uploaded_size += len(data)
                if progress and progress_task is not None:
                    progress.update(progress_task, completed=uploaded_size)
            
            # Ensure remote directory exists
            remote_dir = os.path.dirname(remote_file)
            if remote_dir:
                self.ensure_remote_directory(remote_dir)
            
            # Upload the file
            with open(local_file, 'rb') as f:
                if progress and progress_task is not None:
                    self.ftp.storbinary(f'STOR {remote_file}', f, callback=callback)
                else:
                    self.ftp.storbinary(f'STOR {remote_file}', f)
            
            return True
            
        except Exception as e:
            console.print(f"[red]Failed to upload {local_file.name}:[/] {str(e)}")
            return False
    
    def upload_webgl_build(self, build_path: Path) -> Tuple[bool, int]:
        """Upload entire WebGL build directory."""
        if not self.connect():
            return False, 0
        
        try:
            # Ensure the base remote directory exists
            if self.ftp_remote_path:
                self.ensure_remote_directory(self.ftp_remote_path)
            
            # Collect all files to upload
            files_to_upload = []
            for root, dirs, files in os.walk(build_path):
                for file in files:
                    local_file = Path(root) / file
                    relative_path = local_file.relative_to(build_path)
                    # Build full remote path including the base path
                    remote_file = self.ftp_remote_path.rstrip('/') + '/' + str(relative_path).replace('\\', '/')
                    files_to_upload.append((local_file, remote_file))
            
            console.print(f"\n[cyan]Uploading {len(files_to_upload)} files to FTP server...[/]")
            
            # Upload files with progress
            uploaded_count = 0
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                
                for local_file, remote_file in files_to_upload:
                    file_size = local_file.stat().st_size
                    task_desc = f"Uploading {local_file.name}"
                    
                    # Show file being uploaded
                    if file_size > 1024 * 1024:  # Show progress for files > 1MB
                        task = progress.add_task(task_desc, total=file_size)
                        success = self.upload_file(local_file, remote_file, task, progress)
                        progress.remove_task(task)
                    else:
                        console.print(f"[dim]Uploading:[/] {remote_file}")
                        success = self.upload_file(local_file, remote_file)
                    
                    if success:
                        uploaded_count += 1
                    elif not self.ftp_overwrite:
                        console.print(f"[yellow]Skipping existing file:[/] {remote_file}")
                        uploaded_count += 1
            
            # Show upload summary
            if uploaded_count == len(files_to_upload):
                console.print(f"\n[green]Successfully uploaded all {uploaded_count} files![/]")
                
                # Show the URL where the game can be accessed
                if self.ftp_host and self.ftp_remote_path:
                    likely_url = f"https://{self.ftp_host}{self.ftp_remote_path}"
                    console.print(f"\n[cyan]Your WebGL build is likely accessible at:[/]")
                    console.print(f"[green]{likely_url}[/]")
            else:
                console.print(f"\n[yellow]Uploaded {uploaded_count} of {len(files_to_upload)} files[/]")
            
            return uploaded_count == len(files_to_upload), uploaded_count
            
        except Exception as e:
            console.print(f"\n[red]Upload error:[/] {str(e)}")
            return False, 0
        
        finally:
            self.disconnect()
    
    def upload_build_from_path(self, webgl_build_path: Path) -> Tuple[bool, Optional[str]]:
        """Upload a WebGL build from the specified path."""
        if not self.is_configured():
            return False, "FTP not configured"
        
        if not webgl_build_path.exists():
            return False, f"Build path not found: {webgl_build_path}"
        
        # Check if it's a valid WebGL build
        index_file = webgl_build_path / "index.html"
        if not index_file.exists():
            return False, "Not a valid WebGL build (index.html not found)"
        
        # Show upload info panel
        panel = Panel(
            f"[cyan]Source:[/] {webgl_build_path}\n"
            f"[cyan]Target:[/] {self.ftp_host}:{self.ftp_remote_path}\n"
            f"[cyan]Mode:[/] {'FTPS (secure)' if self.ftp_use_tls else 'FTP'}\n"
            f"[cyan]Overwrite:[/] {'Yes' if self.ftp_overwrite else 'No'}",
            title="WebGL FTP Upload",
            border_style="cyan"
        )
        console.print(panel)
        
        # Upload the build
        success, file_count = self.upload_webgl_build(webgl_build_path)
        
        if success:
            return True, f"Uploaded {file_count} files successfully"
        else:
            return False, "Upload failed"