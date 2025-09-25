"""
Utility functions for Unity Build Automation.
Common helpers and tools used across modules.

MIT License - Copyright (c) 2025 Angry Shark Studio
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Dict
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

console = Console()


def show_welcome_banner() -> None:
    """Display welcome banner with project info."""
    banner_text = """
    [bold cyan]Unity Build Automation[/bold cyan]
    [dim]Zero Configuration Edition[/dim]
    
    [yellow]Automate your Unity builds with style![/yellow]
    """
    
    console.print(Panel(banner_text, border_style="cyan", padding=(1, 2)))


def prompt_build_selection() -> str:
    """Interactive menu for build selection."""
    choices = {
        "1": "windows",
        "2": "all",
        "3": "custom",
        "4": "webgl_upload",
        "5": "exit"
    }
    
    console.print("\n[bold]What would you like to build?[/bold]")
    console.print("  [cyan]1.[/cyan] Windows only")
    console.print("  [cyan]2.[/cyan] All platforms")
    console.print("  [cyan]3.[/cyan] Custom selection")
    console.print("  [cyan]4.[/cyan] WebGL build and upload")
    console.print("  [cyan]5.[/cyan] Exit")
    
    while True:
        choice = Prompt.ask("\nEnter your choice", choices=list(choices.keys()))
        return choices.get(choice, "exit")


def prompt_custom_platforms() -> List[str]:
    """Let user select specific platforms to build."""
    available_platforms = {
        "1": "windows",
        "2": "mac",
        "3": "android",
        "4": "webgl",
        "5": "ios"
    }
    
    console.print("\n[bold]Select platforms to build:[/bold]")
    console.print("  [cyan]1.[/cyan] Windows")
    console.print("  [cyan]2.[/cyan] macOS")
    console.print("  [cyan]3.[/cyan] Android") 
    console.print("  [cyan]4.[/cyan] WebGL")
    console.print("  [cyan]5.[/cyan] iOS (Xcode project - macOS only)")
    
    selections = Prompt.ask(
        "\nEnter platform numbers separated by commas",
        default="1"
    )
    
    # Parse selections
    selected = []
    for num in selections.split(','):
        num = num.strip()
        if num in available_platforms:
            selected.append(available_platforms[num])
    
    if not selected:
        console.print("[yellow]No valid platforms selected. Defaulting to Windows.[/]")
        return ["windows"]
    
    return selected


def format_time_duration(seconds: float) -> str:
    """Format time duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    else:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes ({seconds:.0f} seconds)"


def ensure_directory_exists(path: Path) -> None:
    """Ensure a directory exists, create if it doesn't."""
    path.mkdir(parents=True, exist_ok=True)


def get_file_size_mb(path: Path) -> float:
    """Get file or directory size in MB."""
    if path.is_file():
        return path.stat().st_size / (1024 * 1024)
    elif path.is_dir():
        total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        return total_size / (1024 * 1024)
    return 0.0


def validate_unity_executable(unity_path: str) -> bool:
    """Validate that the Unity executable exists and is accessible."""
    if not unity_path:
        return False
    
    path = Path(unity_path)
    
    # Check if file exists
    if not path.exists():
        return False
    
    # On Windows, check for .exe
    if sys.platform == "win32" and not unity_path.endswith('.exe'):
        return False
    
    # On Mac, check for .app structure
    if sys.platform == "darwin" and not unity_path.endswith('/Unity'):
        return False
    
    return True


def find_unity_installations() -> List[Dict[str, str]]:
    """Try to find Unity installations on the system."""
    installations = []
    
    if sys.platform == "win32":
        # Common Windows paths
        common_paths = [
            "C:/Program Files/Unity/Hub/Editor",
            "C:/Program Files (x86)/Unity/Hub/Editor",
            os.path.expanduser("~/Unity/Hub/Editor")
        ]
    elif sys.platform == "darwin":
        # Common macOS paths
        common_paths = [
            "/Applications/Unity/Hub/Editor",
            os.path.expanduser("~/Applications/Unity/Hub/Editor")
        ]
    else:
        # Common Linux paths
        common_paths = [
            os.path.expanduser("~/Unity/Hub/Editor"),
            "/opt/Unity/Hub/Editor"
        ]
    
    # Search for Unity installations
    for base_path in common_paths:
        if os.path.exists(base_path):
            # Look for version folders
            try:
                for version_dir in os.listdir(base_path):
                    version_path = os.path.join(base_path, version_dir)
                    if os.path.isdir(version_path):
                        # Construct executable path
                        if sys.platform == "win32":
                            exe_path = os.path.join(version_path, "Editor", "Unity.exe")
                        elif sys.platform == "darwin":
                            exe_path = os.path.join(version_path, "Unity.app", "Contents", "MacOS", "Unity")
                        else:
                            exe_path = os.path.join(version_path, "Editor", "Unity")
                        
                        if os.path.exists(exe_path):
                            installations.append({
                                'version': version_dir,
                                'path': exe_path
                            })
            except:
                pass
    
    return installations


def show_unity_installation_help() -> None:
    """Show help for finding Unity installation."""
    console.print("\n[yellow]Unity Installation Help[/yellow]")
    
    installations = find_unity_installations()
    
    if installations:
        console.print("\n[green]Found Unity installations:[/green]")
        for install in installations:
            console.print(f"  • {install['version']}: [dim]{install['path']}[/dim]")
        
        console.print("\n[cyan]Copy one of the paths above and add it to your .env file.[/cyan]")
    else:
        console.print("\n[red]No Unity installations found in common locations.[/red]")
        console.print("\nPlease check Unity Hub and copy the installation path.")
        
        if sys.platform == "win32":
            console.print("\n[cyan]Windows:[/cyan] Look in Unity Hub > Installs > Show in Explorer")
        elif sys.platform == "darwin":
            console.print("\n[cyan]macOS:[/cyan] Look in Unity Hub > Installs > Reveal in Finder")
        else:
            console.print("\n[cyan]Linux:[/cyan] Look in Unity Hub > Installs for the path")


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask for confirmation with Rich prompt."""
    return Confirm.ask(message, default=default)