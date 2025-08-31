"""
Platform-specific build methods and validation for Unity Build Automation.
Handles Windows, Mac, Android, and WebGL build configurations.

MIT License - Copyright (c) 2025 Angry Shark Studio
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table

console = Console()


class PlatformBuilder:
    """Handles platform-specific build operations."""
    
    PLATFORMS = {
        'windows': {
            'method': 'CommandLineBuild.BuildWindows',
            'extension': '.exe',
            'name': 'Windows'
        },
        'mac': {
            'method': 'CommandLineBuild.BuildMac',
            'extension': '.app',
            'name': 'macOS'
        },
        'android': {
            'method': 'CommandLineBuild.BuildAndroid',
            'extension': '.apk',
            'name': 'Android'
        },
        'webgl': {
            'method': 'CommandLineBuild.BuildWebGL',
            'extension': '',  # WebGL creates a folder
            'name': 'WebGL'
        }
    }
    
    def __init__(self, config):
        """Initialize with configuration object."""
        self.config = config
        self.build_results = []
    
    def _get_unity_output_path(self, platform: str, extension: str = "") -> Path:
        """Get the path where Unity will output the build (without timestamp)."""
        platform_dir = self.config.project_root / "Builds" / platform.capitalize() / self.config.project_version
        if extension:
            return platform_dir / f"{self.config.project_name}{extension}"
        else:
            # For WebGL and other folder-based builds
            return platform_dir / self.config.project_name
    
    def check_platform_available(self, platform: str) -> Tuple[bool, Optional[str]]:
        """Check if platform build support is available."""
        if platform == 'android':
            # Check for Android SDK
            if not os.environ.get('ANDROID_HOME'):
                return False, "ANDROID_HOME environment variable not set"
        
        elif platform == 'mac':
            # Mac builds only work on macOS
            if sys.platform != 'darwin':
                return False, "Mac builds only available on macOS"
        
        elif platform == 'webgl':
            # WebGL builds require more memory
            console.print("[yellow]Note: WebGL builds require significant memory (8GB+ recommended)[/]")
        
        return True, None
    
    def build_platform(self, platform_name: str) -> bool:
        """Build for a specific platform with progress indication."""
        platform_info = self.PLATFORMS.get(platform_name)
        if not platform_info:
            console.print(f"[red]Unknown platform: {platform_name}[/]")
            return False
        
        # Check if platform is available
        available, reason = self.check_platform_available(platform_name)
        if not available:
            console.print(f"[yellow]Skipping {platform_info['name']}: {reason}[/]")
            self.build_results.append({
                'platform': platform_name,
                'status': 'skipped',
                'reason': reason
            })
            return False
        
        # Unity will build to a simple version folder
        # We'll move it to our timestamped folder after build completes
        unity_output_path = self._get_unity_output_path(platform_name, platform_info['extension'])
        final_output_path = self.config.get_build_output_path(
            platform_name, 
            platform_info['extension']
        )
        
        console.print(f"\n[cyan]Building for {platform_info['name']}...[/]")
        console.print(f"[dim]Output: {final_output_path.relative_to(self.config.project_root)}[/]")
        
        start_time = time.time()
        
        # Build command
        cmd = [
            str(self.config.unity_path),
            '-batchmode',
            '-quit',
            '-nographics',
            '-projectPath', str(self.config.project_root),
            '-executeMethod', platform_info['method'],
            '-logFile', str(self.config.project_root / 'BuildAutomation' / f'build_{platform_name}.log')
        ]
        
        # Run build with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task(
                f"Building {platform_info['name']}...", 
                total=None  # Indeterminate progress
            )
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                build_time = time.time() - start_time
                
                # Check if build succeeded
                console.print(f"[dim]Unity exit code: {result.returncode}[/]")
                console.print(f"[dim]Checking for output at: {unity_output_path}[/]")
                
                if result.returncode == 0 and unity_output_path.exists():
                    # Move build to timestamped folder
                    import shutil
                    if unity_output_path != final_output_path:
                        if final_output_path.exists():
                            if final_output_path.is_dir():
                                shutil.rmtree(final_output_path)
                            else:
                                final_output_path.unlink()
                        
                        # Move the build to the timestamped folder
                        shutil.move(str(unity_output_path), str(final_output_path))
                    
                    # Calculate size
                    if final_output_path.is_file():
                        size_mb = final_output_path.stat().st_size / (1024 * 1024)
                    else:
                        # For folders (WebGL)
                        size_mb = sum(f.stat().st_size for f in final_output_path.rglob('*')) / (1024 * 1024)
                    
                    progress.update(task, completed=100)
                    
                    console.print(f"[green]{platform_info['name']} build completed![/]")
                    console.print(f"   [dim]Time: {build_time:.1f} seconds[/]")
                    console.print(f"   [dim]Size: {size_mb:.1f} MB[/]")
                    console.print(f"   [dim]Version: {self.config.project_version}[/]")
                    
                    self.build_results.append({
                        'platform': platform_name,
                        'status': 'success',
                        'time': build_time,
                        'size_mb': size_mb,
                        'output_path': final_output_path
                    })
                    return True
                else:
                    progress.stop()
                    console.print(f"[red]{platform_info['name']} build failed![/]")
                    
                    if result.returncode != 0:
                        console.print(f"[red]Unity exited with error code: {result.returncode}[/]")
                    
                    if not unity_output_path.exists():
                        console.print(f"[red]Expected output not found at: {unity_output_path}[/]")
                        console.print(f"[yellow]Unity may have built to a different location.[/]")
                        
                        # Check if version folder exists without timestamp
                        version_dir = unity_output_path.parent
                        if version_dir.exists():
                            console.print(f"[yellow]Found version directory: {version_dir}[/]")
                            files = list(version_dir.iterdir())
                            if files:
                                console.print("[yellow]Contents:[/]")
                                for f in files[:5]:  # Show first 5 files
                                    console.print(f"  - {f.name}")
                    
                    console.print(f"[yellow]Check log: BuildAutomation/build_{platform_name}.log[/]")
                    
                    # Try to show error from log
                    self._show_build_errors(platform_name)
                    
                    self.build_results.append({
                        'platform': platform_name,
                        'status': 'failed',
                        'time': build_time
                    })
                    return False
                    
            except Exception as e:
                progress.stop()
                console.print(f"[red]Build error: {str(e)}[/]")
                self.build_results.append({
                    'platform': platform_name,
                    'status': 'error',
                    'error': str(e)
                })
                return False
    
    def build_all_platforms(self) -> List[Dict]:
        """Build for all available platforms."""
        console.print(f"\n[bold cyan]Starting multi-platform build[/]")
        console.print(f"[dim]Project: {self.config.project_name} v{self.config.project_version}[/]")
        
        total_start = time.time()
        success_count = 0
        
        # Build each platform
        for platform_name in self.PLATFORMS:
            if self.build_platform(platform_name):
                success_count += 1
        
        total_time = time.time() - total_start
        
        # Show summary
        self._show_build_summary(success_count, total_time)
        
        return self.build_results
    
    def build_selected_platforms(self, platforms: List[str]) -> List[Dict]:
        """Build only selected platforms."""
        console.print(f"\n[bold cyan]Building selected platforms[/]")
        console.print(f"[dim]Project: {self.config.project_name} v{self.config.project_version}[/]")
        
        total_start = time.time()
        success_count = 0
        
        for platform_name in platforms:
            if platform_name in self.PLATFORMS:
                if self.build_platform(platform_name):
                    success_count += 1
            else:
                console.print(f"[yellow]Unknown platform: {platform_name}[/]")
        
        total_time = time.time() - total_start
        self._show_build_summary(success_count, total_time)
        
        return self.build_results
    
    def _show_build_errors(self, platform: str):
        """Try to show relevant errors from build log."""
        log_path = self.config.project_root / 'BuildAutomation' / f'build_{platform}.log'
        
        if log_path.exists():
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    error_lines = []
                    
                    for line in lines[-20:]:  # Last 20 lines
                        if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed']):
                            error_lines.append(line.strip())
                    
                    if error_lines:
                        console.print("[yellow]Recent errors from build log:[/]")
                        for error in error_lines[-5:]:  # Show last 5 errors
                            console.print(f"[red]  {error}[/]")
            except:
                pass
    
    def _show_build_summary(self, success_count: int, total_time: float):
        """Display build summary table."""
        table = Table(title="Build Summary")
        table.add_column("Platform", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Time", style="dim")
        table.add_column("Size", style="dim")
        
        for result in self.build_results:
            platform = self.PLATFORMS[result['platform']]['name']
            
            if result['status'] == 'success':
                status = "[green]Success[/]"
                time_str = f"{result.get('time', 0):.1f}s"
                size_str = f"{result.get('size_mb', 0):.1f} MB"
            elif result['status'] == 'failed':
                status = "[red]Failed[/]"
                time_str = f"{result.get('time', 0):.1f}s"
                size_str = "N/A"
            elif result['status'] == 'skipped':
                status = f"[yellow]Skipped[/]"
                time_str = "N/A"
                size_str = "N/A"
            else:
                status = "[red]Error[/]"
                time_str = "N/A"
                size_str = "N/A"
            
            table.add_row(platform, status, time_str, size_str)
        
        console.print("\n")
        console.print(table)
        
        console.print(f"\n[bold]Total platforms:[/] {len(self.build_results)}")
        console.print(f"[bold]Successful:[/] [green]{success_count}[/]")
        console.print(f"[bold]Total time:[/] {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
        console.print(f"[bold]Output version:[/] {self.config.project_version}")