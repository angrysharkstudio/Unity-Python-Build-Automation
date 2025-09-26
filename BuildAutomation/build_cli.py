#!/usr/bin/env python3
"""
Unity Build Automation - Command Line Interface
Professional CLI using Click for better argument handling

Usage examples:
  python build_cli.py windows
  python build_cli.py android webgl
  python build_cli.py --all
  python build_cli.py --help

MIT License - Copyright (c) 2025 Angry Shark Studio
"""

import click
import sys
from typing import Tuple, Optional, List, Any
from unity_builder import UnityAutoBuilder
from rich.console import Console

console = Console()

PLATFORMS: List[str] = ['windows', 'mac', 'android', 'webgl', 'ios']

@click.command()
@click.argument('platforms', nargs=-1, type=click.Choice(PLATFORMS))
@click.option('--all', '-a', is_flag=True, help='Build for all available platforms')
@click.option('--report/--no-report', default=True, help='Generate HTML report after build')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed build output')
@click.option('--upload', '-u', is_flag=True, help='Upload build after building (WebGL to FTP, Windows to Google Drive)')
@click.option('--upload-only', is_flag=True, help='Upload existing build without building')
@click.option('--gdrive-upload', is_flag=True, help='Upload Windows build to Google Drive after building')
@click.option('--hook', '-h', help='Pre-build hook to execute (e.g., BuildHooks.SwitchToProduction)')
@click.option('--no-hook', is_flag=True, help='Skip pre-build hook even if configured in .env')
def build(platforms: Tuple[str, ...], all: bool, report: bool, verbose: bool, upload: bool, upload_only: bool, gdrive_upload: bool, hook: Optional[str], no_hook: bool) -> None:
    """
    Unity Build Automation CLI - Build for one or more platforms.
    
    Examples:
        python build_cli.py windows
        python build_cli.py android webgl
        python build_cli.py --all
        python build_cli.py webgl --upload
        python build_cli.py windows --gdrive-upload
        python build_cli.py windows --upload  # Also uploads to Google Drive
        python build_cli.py webgl --hook "BuildHooks.PrepareWebGL"
        python build_cli.py --upload-only
    """
    try:
        # Initialize builder (suppress banner for CLI)
        builder = UnityAutoBuilder()
        
        # Handle upload-only mode
        if upload_only:
            # Detect which platform to upload based on available builds
            if builder.platform_builder.get_latest_build_path("webgl"):
                click.echo("Uploading existing WebGL build...")
                success, message = builder.upload_webgl_build()
            elif builder.platform_builder.get_latest_build_path("windows"):
                click.echo("Uploading existing Windows build...")
                success, message = builder.upload_windows_build()
            else:
                click.echo("No builds found to upload")
                sys.exit(1)
            
            click.echo(message)
            sys.exit(0 if success else 1)
        
        # Determine what to build
        if all:
            click.echo("Building for all platforms...")
            results = builder.build_all_platforms()
        elif platforms:
            # Special handling for single platform builds with upload
            if len(platforms) == 1:
                platform = platforms[0]
                
                # Windows with Google Drive upload
                if platform == 'windows' and (gdrive_upload or upload):
                    success, message = builder.build_windows_with_upload(
                        pre_build_hook=hook,
                        skip_hook=no_hook
                    )
                    click.echo(message)
                    
                    if report:
                        builder.generate_report()
                    
                    sys.exit(0 if success else 1)
                
                # WebGL with FTP upload
                elif platform == 'webgl' and upload:
                    success, message = builder.build_webgl_with_upload(
                        pre_build_hook=hook,
                        skip_hook=no_hook
                    )
                    click.echo(message)
                    
                    if report:
                        builder.generate_report()
                    
                    sys.exit(0 if success else 1)
            
            # Multi-platform or no upload
            click.echo(f"Building for: {', '.join(platforms)}")
            results = builder.build_custom_platforms(
                list(platforms),
                pre_build_hook=hook,
                skip_hook=no_hook
            )
            
            # Handle post-build uploads
            if upload or gdrive_upload:
                # Upload Windows if built and gdrive enabled
                if (gdrive_upload or upload) and 'windows' in platforms:
                    windows_result = next((r for r in results if r.get('platform') == 'windows' and r.get('status') == 'success'), None)
                    if windows_result:
                        click.echo("\nUploading Windows build to Google Drive...")
                        upload_success, upload_message = builder.upload_windows_build()
                        click.echo(upload_message)
                
                # Upload WebGL if built and upload flag set
                if upload and 'webgl' in platforms:
                    webgl_result = next((r for r in results if r.get('platform') == 'webgl' and r.get('status') == 'success'), None)
                    if webgl_result:
                        click.echo("\nUploading WebGL build to FTP...")
                        upload_success, upload_message = builder.upload_webgl_build()
                        click.echo(upload_message)
        else:
            click.echo("Error: No platforms specified. Use --help for usage.")
            sys.exit(1)
        
        # Generate report if requested
        if report:
            builder.generate_report(results)
        
        # Summary
        success_count = sum(1 for r in results if r['status'] == 'success')
        total_count = len(results)
        
        if verbose:
            click.echo(f"\nBuild Summary: {success_count}/{total_count} successful")
        
        # Exit with appropriate code
        sys.exit(0 if success_count > 0 else 1)
        
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    build()