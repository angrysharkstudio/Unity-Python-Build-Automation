"""
Platform-specific build methods and validation for Unity Build Automation.
Handles Windows, Mac, Android, and WebGL build configurations.

MIT License - Copyright (c) 2025 Angry Shark Studio
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table

console = Console()


class PlatformBuilder:
    """Handles platform-specific build operations."""
    
    PLATFORMS: Dict[str, Dict[str, str]] = {
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
        },
        'ios': {
            'method': 'CommandLineBuild.BuildiOS',
            'extension': '',  # iOS creates an Xcode project folder
            'name': 'iOS'
        }
    }
    
    # Unity command line build target names
    BUILD_TARGET_MAPPING: Dict[str, str] = {
        'windows': 'Win64',
        'mac': 'OSXUniversal',
        'android': 'Android',
        'webgl': 'WebGL',
        'ios': 'iOS'
    }
    
    # Platform directory names (using lowercase for consistency)
    PLATFORM_DIR_NAMES: Dict[str, str] = {
        'windows': 'windows',
        'mac': 'mac',
        'android': 'android',
        'webgl': 'webgl',
        'ios': 'ios'
    }
    
    def __init__(self, config: Any) -> None:
        """Initialize with configuration object."""
        self.config = config
        self.build_results: List[Dict[str, Any]] = []
    
    def _get_unity_output_path(self, platform: str, extension: str = "") -> Path:
        """Get the path where Unity will output the build (without timestamp)."""
        platform_folder = self.PLATFORM_DIR_NAMES.get(platform, platform.capitalize())
        platform_dir = self.config.project_root / "Builds" / platform_folder / self.config.project_version
        if extension:
            return platform_dir / f"{self.config.project_name}{extension}"
        else:
            # For WebGL and other folder-based builds
            return platform_dir / self.config.project_name
    
    def _get_unity_output_path_with_name(self, platform: str, product_name: str, extension: str = "") -> Path:
        """Get the path where Unity will output the build with a specific product name."""
        platform_folder = self.PLATFORM_DIR_NAMES.get(platform, platform.capitalize())
        platform_dir = self.config.project_root / "Builds" / platform_folder / self.config.project_version
        if extension:
            return platform_dir / f"{product_name}{extension}"
        else:
            # For WebGL and other folder-based builds
            return platform_dir / product_name
    
    def _read_build_summary(self, platform: str) -> Optional[Dict[str, Any]]:
        """Read build summary JSON if available."""
        platform_folder = self.PLATFORM_DIR_NAMES.get(platform, platform.capitalize())
        summary_path = self.config.project_root / "Builds" / platform_folder / self.config.project_version / "build_summary.json"
        
        if summary_path.exists():
            try:
                with open(summary_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not read build_summary.json: {e}[/]")
        return None
    
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
        
        elif platform == 'ios':
            # iOS builds only work on macOS
            if sys.platform != 'darwin':
                return False, "iOS builds only available on macOS (outputs Xcode project)"
        
        elif platform == 'webgl':
            # WebGL builds require more memory
            console.print("[yellow]Note: WebGL builds require significant memory (8GB+ recommended)[/]")
        
        return True, None
    
    def build_platform(self, platform_name: str, pre_build_hook: Optional[str] = None, skip_hook: bool = False) -> bool:
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
        
        # Execute pre-build hook if configured
        hook_to_use = pre_build_hook if pre_build_hook else self.config.pre_build_hook
        if hook_to_use and not skip_hook:
            console.print(f"[cyan]Executing pre-build hook:[/] {hook_to_use}")
            hook_success = self._execute_pre_build_hook(hook_to_use)
            if not hook_success:
                console.print("[red]Pre-build hook failed! Aborting build.[/]")
                self.build_results.append({
                    'platform': platform_name,
                    'status': 'failed',
                    'reason': 'Pre-build hook failed'
                })
                return False
        
        start_time = time.time()
        
        # Build command
        cmd = [
            str(self.config.unity_path),
            '-batchmode',
            '-quit',
            '-nographics',
            '-projectPath', str(self.config.project_root),
            '-buildTarget', self.BUILD_TARGET_MAPPING.get(platform_name, platform_name),
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
                
                # Check if build succeeded - first try build_summary.json, then fall back to old method
                build_summary = self._read_build_summary(platform_name)
                build_succeeded = False
                build_errors = []
                
                if build_summary:
                    # Use build summary if available
                    build_succeeded = build_summary.get('status') == 'success'
                    build_errors = build_summary.get('errors', [])
                    
                    # Check if product name changed during build (e.g., by pre-build hook)
                    if 'product_name' in build_summary:
                        actual_product_name = build_summary['product_name']
                        if actual_product_name != self.config.project_name:
                            console.print(f"[yellow]Note: Product name changed from '{self.config.project_name}' to '{actual_product_name}' during build[/]")
                            # Recalculate unity_output_path with the actual product name
                            unity_output_path = self._get_unity_output_path_with_name(
                                platform_name, 
                                actual_product_name,
                                platform_info['extension']
                            )
                            # Also update final output path to use the new product name
                            timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M")
                            folder_name = f"{self.config.project_version}_{timestamp}"
                            platform_folder = self.PLATFORM_DIR_NAMES.get(platform_name, platform_name.lower())
                            platform_dir = self.config.project_root / "Builds" / platform_folder / folder_name
                            platform_dir.mkdir(parents=True, exist_ok=True)
                            if platform_info['extension']:
                                final_output_path = platform_dir / f"{actual_product_name}{platform_info['extension']}"
                            else:
                                final_output_path = platform_dir / actual_product_name
                    
                    # Update build info if available
                    if build_succeeded and 'build_size_mb' in build_summary:
                        reported_size_mb = build_summary['build_size_mb']
                else:
                    # Fall back to old method
                    build_succeeded = result.returncode == 0 and unity_output_path.exists()
                
                if build_succeeded:
                    # Move build to timestamped folder
                    import shutil
                    if unity_output_path != final_output_path:
                        # Special handling for Windows builds
                        if platform_name == 'windows':
                            # Windows builds create multiple files in the version directory
                            # We need to move all contents, not just the exe
                            version_dir = unity_output_path.parent
                            if version_dir.exists() and version_dir.is_dir():
                                # Create the timestamped directory
                                final_dir = final_output_path.parent
                                final_dir.mkdir(parents=True, exist_ok=True)
                                
                                # Move all contents of version directory to timestamped directory
                                for item in version_dir.iterdir():
                                    dest = final_dir / item.name
                                    if dest.exists():
                                        if dest.is_dir():
                                            shutil.rmtree(dest)
                                        else:
                                            dest.unlink()
                                    shutil.move(str(item), str(dest))
                                
                                # Clean up empty version folder
                                if version_dir.exists() and not any(version_dir.iterdir()):
                                    version_dir.rmdir()
                                    console.print(f"[dim]Cleaned up empty folder: {version_dir}[/]")
                            else:
                                # Fallback: just move the exe if that's all we have
                                if final_output_path.exists():
                                    if final_output_path.is_dir():
                                        shutil.rmtree(final_output_path)
                                    else:
                                        final_output_path.unlink()
                                shutil.move(str(unity_output_path), str(final_output_path))
                        else:
                            # For other platforms, use the original logic
                            if final_output_path.exists():
                                if final_output_path.is_dir():
                                    shutil.rmtree(final_output_path)
                                else:
                                    final_output_path.unlink()
                            
                            # Move the build to the timestamped folder
                            shutil.move(str(unity_output_path), str(final_output_path))
                            
                            # Clean up empty version folder if it exists
                            version_folder = unity_output_path.parent
                            if version_folder.exists() and not any(version_folder.iterdir()):
                                version_folder.rmdir()
                                console.print(f"[dim]Cleaned up empty folder: {version_folder}[/]")
                    
                    # Calculate size
                    if platform_name == 'windows':
                        # Windows builds are now in a directory
                        final_dir = final_output_path.parent
                        size_mb = sum(f.stat().st_size for f in final_dir.rglob('*') if f.is_file()) / (1024 * 1024)
                    elif final_output_path.is_file():
                        size_mb = final_output_path.stat().st_size / (1024 * 1024)
                    else:
                        # For folders (WebGL, iOS)
                        size_mb = sum(f.stat().st_size for f in final_output_path.rglob('*') if f.is_file()) / (1024 * 1024)
                    
                    progress.update(task, completed=100)
                    
                    console.print(f"[green]{platform_info['name']} build completed![/]")
                    console.print(f"   [dim]Time: {build_time:.1f} seconds[/]")
                    console.print(f"   [dim]Size: {size_mb:.1f} MB[/]")
                    console.print(f"   [dim]Version: {self.config.project_version}[/]")
                    
                    # Use reported size from build summary if available
                    if build_summary and 'build_size_mb' in build_summary:
                        size_mb = build_summary['build_size_mb']
                    
                    build_result = {
                        'platform': platform_name,
                        'status': 'success',
                        'time': build_time,
                        'size_mb': size_mb,
                        'output_path': final_output_path
                    }
                    
                    # Add extra info from build summary if available
                    if build_summary:
                        build_result['unity_version'] = build_summary.get('unity_version')
                        build_result['scene_count'] = build_summary.get('scene_count')
                        build_result['warnings_count'] = build_summary.get('warnings_count', 0)
                    
                    self.build_results.append(build_result)
                    return True
                else:
                    progress.stop()
                    console.print(f"[red]{platform_info['name']} build failed![/]")
                    
                    # Show errors from build summary if available
                    if build_errors:
                        console.print(f"[red]Build errors:[/]")
                        for error in build_errors[:5]:  # Show first 5 errors
                            console.print(f"  [red]• {error}[/]")
                        if len(build_errors) > 5:
                            console.print(f"  [dim]... and {len(build_errors) - 5} more errors[/]")
                    
                    if result.returncode != 0:
                        console.print(f"[red]Unity exited with error code: {result.returncode}[/]")
                    
                    if not build_succeeded and not build_summary and not unity_output_path.exists():
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
    
    def build_all_platforms(self) -> List[Dict[str, Any]]:
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
    
    def build_selected_platforms(self, platforms: List[str], pre_build_hook: Optional[str] = None, skip_hook: bool = False) -> List[Dict[str, Any]]:
        """Build only selected platforms."""
        console.print(f"\n[bold cyan]Building selected platforms[/]")
        console.print(f"[dim]Project: {self.config.project_name} v{self.config.project_version}[/]")
        
        total_start = time.time()
        success_count = 0
        
        for platform_name in platforms:
            if platform_name in self.PLATFORMS:
                if self.build_platform(platform_name, pre_build_hook, skip_hook):
                    success_count += 1
            else:
                console.print(f"[yellow]Unknown platform: {platform_name}[/]")
        
        total_time = time.time() - total_start
        self._show_build_summary(success_count, total_time)
        
        return self.build_results
    
    def _show_build_errors(self, platform: str) -> None:
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
    
    def _show_build_summary(self, success_count: int, total_time: float) -> None:
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
    
    def _execute_pre_build_hook(self, hook_method: str) -> bool:
        """Execute a pre-build hook in Unity."""
        console.print(f"[dim]Running hook: {hook_method}[/]")
        
        # Command to execute the hook
        cmd = [
            str(self.config.unity_path),
            '-batchmode',
            '-quit',
            '-nographics',
            '-projectPath', str(self.config.project_root),
            '-executeMethod', 'CommandLineBuild.ExecutePreBuildHook',
            '-preBuildHook', hook_method,
            '-logFile', str(self.config.project_root / 'BuildAutomation' / 'hook.log')
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                console.print("[green]Pre-build hook executed successfully[/]")
                return True
            else:
                console.print(f"[red]Pre-build hook failed with exit code: {result.returncode}[/]")
                
                # Try to show errors from hook log
                log_path = self.config.project_root / 'BuildAutomation' / 'hook.log'
                if log_path.exists():
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        error_lines = [line for line in content.splitlines() if 'error' in line.lower()][:5]
                        if error_lines:
                            console.print("[red]Hook errors:[/]")
                            for line in error_lines:
                                console.print(f"  {line.strip()}")
                
                return False
                
        except subprocess.TimeoutExpired:
            console.print("[red]Pre-build hook timed out after 60 seconds[/]")
            return False
        except Exception as e:
            console.print(f"[red]Error executing pre-build hook: {str(e)}[/]")
            return False
    
    def get_latest_build_path(self, platform: str) -> Optional[Path]:
        """Get the path to the most recent build for a platform."""
        platform_folder = self.PLATFORM_DIR_NAMES.get(platform, platform.capitalize())
        builds_dir = self.config.project_root / "Builds" / platform_folder
        
        if not builds_dir.exists():
            return None
        
        # For WebGL, we need to find directories that actually contain valid builds
        if platform == 'webgl':
            valid_builds = []
            
            # Check each directory for a valid WebGL build
            for dir_path in builds_dir.iterdir():
                if not dir_path.is_dir():
                    continue
                    
                # Check if this directory contains a WebGL build
                # Look for index.html either directly or in subdirectories
                if (dir_path / "index.html").exists():
                    valid_builds.append((dir_path, dir_path))
                else:
                    # Check subdirectories
                    for subdir in dir_path.iterdir():
                        if subdir.is_dir() and (subdir / "index.html").exists():
                            valid_builds.append((dir_path, subdir))
                            break
            
            if not valid_builds:
                console.print("[yellow]No valid WebGL builds found[/]")
                return None
            
            # Get the most recent valid build
            latest_build = max(valid_builds, key=lambda x: x[0].stat().st_mtime)
            console.print(f"[green]Found latest WebGL build: {latest_build[1]}[/]")
            return latest_build[1]
        
        # For other platforms, just get the newest directory
        build_dirs = [d for d in builds_dir.iterdir() if d.is_dir()]
        if not build_dirs:
            return None
            
        return max(build_dirs, key=lambda p: p.stat().st_mtime)