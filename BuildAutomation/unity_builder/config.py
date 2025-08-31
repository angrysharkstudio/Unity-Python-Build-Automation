"""
Configuration and auto-detection module for Unity Build Automation.
Handles project detection, Unity settings parsing, and environment configuration.

MIT License - Copyright (c) 2025 Angry Shark Studio
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class Config:
    """Handles all configuration and auto-detection for Unity builds."""
    
    def __init__(self):
        """Initialize configuration with auto-detected settings."""
        load_dotenv()
        
        # Auto-detect everything
        self.project_root = self._find_project_root()
        self.project_name = self._get_project_name()
        self.company_name = self._get_company_name()
        self.unity_version = self._get_unity_version()
        self.project_version = self._get_project_version()
        self.bundle_identifier = self._get_bundle_identifier()
        self.unity_path = os.getenv('UNITY_PATH')
        
        # Validate Unity path
        if not self.unity_path:
            self._print_unity_path_error()
            sys.exit(1)
        
        if not os.path.exists(self.unity_path):
            console.print(f"[red]Unity executable not found at:[/] {self.unity_path}")
            console.print("[yellow]Please check your path in .env file[/]")
            sys.exit(1)
    
    def print_configuration(self):
        """Display the detected configuration in a nice table."""
        table = Table(title="Unity Build Configuration", show_header=False)
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        table.add_row("Project", self.project_name)
        table.add_row("Root", str(self.project_root))
        table.add_row("Company", self.company_name)
        table.add_row("Version", self.project_version)
        table.add_row("Unity", self.unity_version)
        table.add_row("Bundle ID", self.bundle_identifier)
        
        console.print(table)
    
    def _find_project_root(self) -> Path:
        """Find Unity project root by looking for Assets folder."""
        current = Path(__file__).parent.parent.absolute()
        
        # Go up until we find Assets and ProjectSettings
        while current != current.parent:
            if (current / "Assets").exists() and (current / "ProjectSettings").exists():
                return current
            current = current.parent
        
        console.print("[red]Unity project root not found![/]")
        console.print("Make sure this script is inside your Unity project")
        console.print("Expected structure: YourProject/BuildAutomation/build.py")
        sys.exit(1)
    
    def _get_project_name(self) -> str:
        """Extract project name from ProjectSettings.asset."""
        settings_path = self.project_root / "ProjectSettings" / "ProjectSettings.asset"
        
        try:
            with open(settings_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Find productName: YourProjectName
                match = re.search(r'productName:\s*(.+)', content)
                if match:
                    name = match.group(1).strip()
                    # Remove quotes if present
                    if name.startswith('"') and name.endswith('"'):
                        name = name[1:-1]
                    return name
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read project name: {e}[/]")
        
        # Fallback to folder name
        return self.project_root.name
    
    def _get_company_name(self) -> str:
        """Extract company name from ProjectSettings.asset."""
        settings_path = self.project_root / "ProjectSettings" / "ProjectSettings.asset"
        
        try:
            with open(settings_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Find companyName: YourCompany
                match = re.search(r'companyName:\s*(.+)', content)
                if match:
                    name = match.group(1).strip()
                    if name.startswith('"') and name.endswith('"'):
                        name = name[1:-1]
                    return name
        except:
            pass
        
        return "DefaultCompany"
    
    def _get_unity_version(self) -> str:
        """Get Unity version from ProjectVersion.txt."""
        version_file = self.project_root / "ProjectSettings" / "ProjectVersion.txt"
        
        try:
            with open(version_file, 'r') as f:
                content = f.read()
                match = re.search(r'm_EditorVersion:\s*(.+)', content)
                if match:
                    return match.group(1).strip()
        except:
            pass
        
        return "Unknown"
    
    def _get_project_version(self) -> str:
        """Extract project version from ProjectSettings.asset."""
        settings_path = self.project_root / "ProjectSettings" / "ProjectSettings.asset"
        
        try:
            with open(settings_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Find bundleVersion: 1.0.0
                match = re.search(r'bundleVersion:\s*(.+)', content)
                if match:
                    version = match.group(1).strip()
                    if version.startswith('"') and version.endswith('"'):
                        version = version[1:-1]
                    return version
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read project version: {e}[/]")
        
        # Fallback to default version
        return "1.0.0"
    
    def _get_bundle_identifier(self) -> str:
        """Extract bundle identifier for mobile builds."""
        settings_path = self.project_root / "ProjectSettings" / "ProjectSettings.asset"
        
        try:
            with open(settings_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Find applicationIdentifier
                # Look for patterns like:
                # Standalone: com.YourCompany.YourProduct
                match = re.search(r'Standalone:\s*([^\s\n]+)', content)
                if match:
                    return match.group(1).strip()
        except:
            pass
        
        # Fallback to constructed identifier
        company = self.company_name.replace(" ", "").replace(".", "")
        product = self.project_name.replace(" ", "").replace(".", "")
        return f"com.{company}.{product}"
    
    def _print_unity_path_error(self):
        """Print helpful error message for missing Unity path."""
        console.print("[red]Unity path not found![/]")
        console.print("\n[yellow]Please set UNITY_PATH in .env file[/]")
        console.print("\n[cyan]Example .env contents:[/]")
        
        if sys.platform == "win32":
            console.print('[green]UNITY_PATH="C:/Program Files/Unity/Hub/Editor/2021.3.16f1/Editor/Unity.exe"[/]')
        elif sys.platform == "darwin":
            console.print('[green]UNITY_PATH="/Applications/Unity/Hub/Editor/2021.3.16f1/Unity.app/Contents/MacOS/Unity"[/]')
        else:
            console.print('[green]UNITY_PATH="/home/username/Unity/Hub/Editor/2021.3.16f1/Editor/Unity"[/]')
    
    def get_build_output_path(self, platform: str, extension: str = "") -> Path:
        """Get the output path for a specific platform build with version and timestamp."""
        # Generate timestamp in format: dd-MM-yyyy_HH-mm
        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M")
        
        # Create folder name with version and timestamp
        folder_name = f"{self.project_version}_{timestamp}"
        
        platform_dir = self.project_root / "Builds" / platform.capitalize() / folder_name
        platform_dir.mkdir(parents=True, exist_ok=True)
        
        if extension:
            return platform_dir / f"{self.project_name}{extension}"
        else:
            # For WebGL and other folder-based builds
            return platform_dir / self.project_name