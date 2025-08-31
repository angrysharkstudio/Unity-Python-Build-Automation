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
from unity_builder import UnityAutoBuilder
from rich.console import Console

console = Console()

PLATFORMS = ['windows', 'mac', 'android', 'webgl']

@click.command()
@click.argument('platforms', nargs=-1, type=click.Choice(PLATFORMS))
@click.option('--all', '-a', is_flag=True, help='Build for all available platforms')
@click.option('--report/--no-report', default=True, help='Generate HTML report after build')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed build output')
def build(platforms, all, report, verbose):
    """
    Unity Build Automation CLI - Build for one or more platforms.
    
    Examples:
        python build_cli.py windows
        python build_cli.py android webgl
        python build_cli.py --all
    """
    try:
        # Initialize builder (suppress banner for CLI)
        builder = UnityAutoBuilder()
        
        # Determine what to build
        if all:
            click.echo("Building for all platforms...")
            results = builder.build_all_platforms()
        elif platforms:
            click.echo(f"Building for: {', '.join(platforms)}")
            results = builder.build_custom_platforms(list(platforms))
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