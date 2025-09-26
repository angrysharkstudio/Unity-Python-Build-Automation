"""
Main Unity Auto Builder class that orchestrates the build process.
Coordinates between config, platforms, and reporting modules.

MIT License - Copyright (c) 2025 Angry Shark Studio
"""

from typing import List, Optional, Tuple, Dict, Any
from rich.console import Console
from .config import Config
from .platforms import PlatformBuilder
from .reporter import Reporter
from .utils import show_welcome_banner, format_time_duration
from .webgl_ftp_uploader import WebGLFTPUploader
from .windows_gdrive_uploader import WindowsGDriveUploader

console = Console()


class UnityAutoBuilder:
    """Main class that orchestrates Unity builds."""
    
    def __init__(self) -> None:
        """Initialize the builder with configuration."""
        # Show welcome banner
        show_welcome_banner()
        
        # Initialize configuration
        console.print("\n[cyan]Auto-detecting project configuration...[/cyan]")
        self.config = Config()
        
        # Show detected configuration
        self.config.print_configuration()
        
        # Initialize platform builder and reporter
        self.platform_builder = PlatformBuilder(self.config)
        self.reporter = Reporter(self.config)
        self.webgl_uploader = WebGLFTPUploader(self.config)
        self.windows_uploader = WindowsGDriveUploader(self.config)
    
    def build_windows(self) -> bool:
        """Build for Windows platform only."""
        return self.platform_builder.build_platform("windows")
    
    def build_all_platforms(self) -> List[Dict[str, Any]]:
        """Build for all available platforms."""
        results = self.platform_builder.build_all_platforms()
        return results
    
    def build_custom_platforms(self, platforms: List[str], pre_build_hook: Optional[str] = None, skip_hook: bool = False) -> List[Dict[str, Any]]:
        """Build for custom selection of platforms."""
        results = self.platform_builder.build_selected_platforms(platforms, pre_build_hook, skip_hook)
        return results
    
    def generate_report(self, build_results: Optional[List[Dict[str, Any]]] = None) -> None:
        """Generate HTML report for build results."""
        if build_results is None:
            build_results = self.platform_builder.build_results
        
        if not build_results:
            console.print("[yellow]No build results to report.[/]")
            return
        
        self.reporter.generate_report(build_results)
    
    def get_build_results(self) -> List[Dict[str, Any]]:
        """Get the current build results."""
        return self.platform_builder.build_results
    
    def upload_webgl_build(self) -> Tuple[bool, str]:
        """Upload the latest WebGL build to FTP."""
        # Find the latest WebGL build
        latest_webgl_path = self.platform_builder.get_latest_build_path("webgl")
        
        if not latest_webgl_path:
            return False, "No WebGL build found to upload"
        
        # Upload to FTP
        return self.webgl_uploader.upload_build_from_path(latest_webgl_path)
    
    def build_webgl_with_upload(self, pre_build_hook: Optional[str] = None, skip_hook: bool = False) -> Tuple[bool, Optional[str]]:
        """Build WebGL and upload to FTP if enabled."""
        # Build WebGL
        console.print("\n[bold cyan]WebGL Build with Upload[/]")
        build_success = self.platform_builder.build_platform("webgl", pre_build_hook, skip_hook)
        
        if not build_success:
            return False, "WebGL build failed"
        
        # Check if FTP upload is enabled
        if not self.webgl_uploader.is_configured():
            console.print("[yellow]WebGL FTP upload is not configured[/]")
            return True, "Build succeeded, upload not configured"
        
        # Upload the build
        console.print("\n[cyan]Starting WebGL FTP upload...[/]")
        upload_success, upload_message = self.upload_webgl_build()
        
        if upload_success:
            return True, f"Build and upload succeeded: {upload_message}"
        else:
            return True, f"Build succeeded, upload failed: {upload_message}"
    
    def upload_windows_build(self) -> Tuple[bool, str]:
        """Upload the latest Windows build to Google Drive."""
        # Find the latest Windows build
        latest_windows_path = self.platform_builder.get_latest_build_path("windows")
        
        if not latest_windows_path:
            return False, "No Windows build found to upload"
        
        # Upload to Google Drive
        return self.windows_uploader.upload_windows_build(latest_windows_path)
    
    def build_windows_with_upload(self, pre_build_hook: Optional[str] = None, skip_hook: bool = False) -> Tuple[bool, Optional[str]]:
        """Build Windows and upload to Google Drive if enabled."""
        # Build Windows
        console.print("\n[bold cyan]Windows Build with Google Drive Upload[/]")
        build_success = self.platform_builder.build_platform("windows", pre_build_hook, skip_hook)
        
        if not build_success:
            return False, "Windows build failed"
        
        # Check if Google Drive upload is enabled
        if not self.windows_uploader.is_configured():
            console.print("[yellow]Windows Google Drive upload is not configured[/]")
            return True, "Build succeeded, upload not configured"
        
        # Upload the build
        console.print("\n[cyan]Starting Windows Google Drive upload...[/]")
        upload_success, upload_message = self.upload_windows_build()
        
        if upload_success:
            return True, f"Build and upload succeeded: {upload_message}"
        else:
            return True, f"Build succeeded, upload failed: {upload_message}"