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
@click.option('--upload', '-u', is_flag=True, help='Upload WebGL build to FTP after building')
@click.option('--upload-only', is_flag=True, help='Upload existing WebGL build without building')
@click.option('--hook', '-h', help='Pre-build hook to execute (e.g., BuildHooks.SwitchToProduction)')
@click.option('--no-hook', is_flag=True, help='Skip pre-build hook even if configured in .env')
def build(platforms: Tuple[str, ...], all: bool, report: bool, verbose: bool, upload: bool, upload_only: bool, hook: Optional[str], no_hook: bool) -> None:
    """
    Unity Build Automation CLI - Build for one or more platforms.
    
    Examples:
        python build_cli.py windows
        python build_cli.py android webgl
        python build_cli.py --all
        python build_cli.py webgl --upload
        python build_cli.py webgl --hook "BuildHooks.PrepareWebGL"
        python build_cli.py --upload-only
    """
    try:
        # Initialize builder (suppress banner for CLI)
        builder = UnityAutoBuilder()
        
        # Handle upload-only mode
        if upload_only:
            click.echo("Uploading existing WebGL build...")
            success, message = builder.upload_webgl_build()
            click.echo(message)
            sys.exit(0 if success else 1)
        
        # Determine what to build
        if all:
            click.echo("Building for all platforms...")
            results = builder.build_all_platforms()
        elif platforms:
            # Special handling for WebGL with upload
            if 'webgl' in platforms and upload and len(platforms) == 1:
                # Build and upload WebGL
                success, message = builder.build_webgl_with_upload(
                    pre_build_hook=hook,
                    skip_hook=no_hook
                )
                click.echo(message)
                
                # Generate report if requested
                if report:
                    builder.generate_report()
                
                sys.exit(0 if success else 1)
            else:
                # Regular multi-platform build
                click.echo(f"Building for: {', '.join(platforms)}")
                results = builder.build_custom_platforms(
                    list(platforms),
                    pre_build_hook=hook,
                    skip_hook=no_hook
                )
                
                # If WebGL was built and upload flag is set, upload it
                if upload and 'webgl' in platforms:
                    webgl_result = next((r for r in results if r.get('platform') == 'webgl' and r.get('status') == 'success'), None)
                    if webgl_result:
                        click.echo("\nUploading WebGL build...")
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