#!/usr/bin/env python3
"""
Unity Build Automation - Setup Verification Script
Helps diagnose common configuration issues.

MIT License - Copyright (c) 2025 Angry Shark Studio
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def main():
    """Run verification checks for Unity build automation setup."""
    console.print("\n[bold cyan]Unity Build Automation - Setup Verification[/bold cyan]\n")
    
    # Load environment
    load_dotenv()
    
    # Check results
    checks = []
    
    # 1. Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    python_ok = sys.version_info >= (3, 8)
    checks.append({
        "check": "Python Version",
        "status": "✓" if python_ok else "✗",
        "details": f"{python_version} {'(OK)' if python_ok else '(Requires 3.8+)'}"
    })
    
    # 2. Unity path
    unity_path = os.getenv('UNITY_PATH')
    unity_exists = unity_path and os.path.exists(unity_path)
    checks.append({
        "check": "Unity Path",
        "status": "✓" if unity_exists else "✗",
        "details": unity_path if unity_path else "Not set in .env file"
    })
    
    if unity_exists:
        checks.append({
            "check": "Unity Executable",
            "status": "✓",
            "details": "Found"
        })
    
    # 3. Project structure
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    assets_exists = (project_root / "Assets").exists()
    settings_exists = (project_root / "ProjectSettings").exists()
    
    checks.append({
        "check": "Unity Project Root",
        "status": "✓" if assets_exists and settings_exists else "✗",
        "details": str(project_root)
    })
    
    checks.append({
        "check": "Assets Folder",
        "status": "✓" if assets_exists else "✗",
        "details": "Found" if assets_exists else "Not found"
    })
    
    checks.append({
        "check": "ProjectSettings Folder",
        "status": "✓" if settings_exists else "✗",
        "details": "Found" if settings_exists else "Not found"
    })
    
    # 4. CommandLineBuild.cs - Search broadly in Unity project
    build_script_found = False
    build_script_location = None
    
    # Search in common Editor script locations
    search_paths = [
        project_root / "Assets" / "Scripts" / "Editor",
        project_root / "Assets" / "Editor",
        project_root / "Assets" / "Scripts",
    ]
    
    # Also search recursively in any Editor folder
    if assets_exists:
        for editor_folder in (project_root / "Assets").rglob("Editor"):
            if editor_folder.is_dir():
                search_paths.append(editor_folder)
    
    # Look for CommandLineBuild.cs in all these locations
    for search_path in search_paths:
        script_path = search_path / "CommandLineBuild.cs"
        if script_path.exists():
            build_script_found = True
            build_script_location = str(script_path.relative_to(project_root))
            break
    
    checks.append({
        "check": "CommandLineBuild.cs",
        "status": "✓" if build_script_found else "✗",
        "details": f"Found at: {build_script_location}" if build_script_found else "Not found in Unity Editor folders"
    })
    
    # 5. Python dependencies
    try:
        import dotenv
        import rich
        import click
        deps_ok = True
    except ImportError:
        deps_ok = False
    
    checks.append({
        "check": "Python Dependencies",
        "status": "✓" if deps_ok else "✗",
        "details": "All installed" if deps_ok else "Run: pip install -r requirements.txt"
    })
    
    # 6. Android SDK (optional)
    android_home = os.environ.get('ANDROID_HOME')
    android_exists = android_home and os.path.exists(android_home)
    checks.append({
        "check": "Android SDK",
        "status": "✓" if android_exists else "⚠",
        "details": android_home if android_home else "Not set (required for Android builds)"
    })
    
    # 7. Try to read project settings
    try:
        settings_file = project_root / "ProjectSettings" / "ProjectSettings.asset"
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Extract some info
                import re
                product_match = re.search(r'productName:\s*(.+)', content)
                version_match = re.search(r'bundleVersion:\s*(.+)', content)
                
                if product_match:
                    product_name = product_match.group(1).strip()
                    checks.append({
                        "check": "Product Name",
                        "status": "✓",
                        "details": product_name
                    })
                
                if version_match:
                    version = version_match.group(1).strip()
                    checks.append({
                        "check": "Bundle Version",
                        "status": "✓",
                        "details": version
                    })
    except Exception as e:
        pass
    
    # Display results
    table = Table(title="Setup Verification Results")
    table.add_column("Check", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Details", style="dim")
    
    for check in checks:
        status_style = "green" if check["status"] == "✓" else "red" if check["status"] == "✗" else "yellow"
        table.add_row(
            check["check"],
            f"[{status_style}]{check['status']}[/{status_style}]",
            check["details"]
        )
    
    console.print(table)
    
    # Summary
    errors = sum(1 for c in checks if c["status"] == "✗")
    warnings = sum(1 for c in checks if c["status"] == "⚠")
    
    if errors == 0 and warnings == 0:
        console.print("\n[green]✓ All checks passed! Your setup is ready.[/green]")
    elif errors == 0:
        console.print(f"\n[yellow]⚠ Setup is functional with {warnings} warning(s).[/yellow]")
    else:
        console.print(f"\n[red]✗ Found {errors} error(s) that need to be fixed.[/red]")
    
    # Additional tips
    if not build_script_found:
        console.print("\n[yellow]Tip: Copy CommandLineBuild.cs to your Unity project:[/yellow]")
        console.print("  1. Create folder: Assets/Scripts/Editor/ (if it doesn't exist)")
        console.print("  2. Copy script: cp CommandLineBuild.cs Assets/Scripts/Editor/")
        console.print("  3. Script must be in an 'Editor' folder to work with Unity's command line")
    
    if not unity_exists:
        console.print("\n[yellow]Tip: Set your Unity path in .env file:[/yellow]")
        console.print("  cp .env.example .env")
        console.print("  Then edit .env and add your Unity installation path")
    
    # Check for build logs
    console.print("\n[cyan]Checking for recent build logs...[/cyan]")
    log_dir = script_dir
    log_files = list(log_dir.glob("build_*.log"))
    
    if log_files:
        console.print(f"Found {len(log_files)} build log(s):")
        for log_file in log_files:
            size = log_file.stat().st_size
            console.print(f"  - {log_file.name} ({size} bytes)")
            
            # Show last few lines if there are errors
            if size > 0:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    error_lines = [l for l in lines if 'error' in l.lower() or 'failed' in l.lower()]
                    if error_lines:
                        console.print(f"    [red]Found errors in {log_file.name}:[/red]")
                        for error in error_lines[-3:]:  # Show last 3 errors
                            console.print(f"    {error.strip()}")
    else:
        console.print("No build logs found yet.")

if __name__ == "__main__":
    main()