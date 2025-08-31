#!/usr/bin/env python3
"""
Unity Build Automation - Main Entry Point
Clean, modular approach to automating Unity builds with beautiful console output.

MIT License - Copyright (c) 2025 Angry Shark Studio
See LICENSE file for full license text
"""

import sys
from rich.console import Console
from unity_builder import UnityAutoBuilder
from unity_builder.utils import (
    prompt_build_selection, 
    prompt_custom_platforms,
    format_time_duration
)

console = Console()


def main():
    """Run Unity build automation with interactive menu."""
    try:
        # Initialize the builder
        builder = UnityAutoBuilder()
        
        # Get user choice
        choice = prompt_build_selection()
        
        if choice == "windows":
            # Build Windows only
            success = builder.build_windows()
            if success:
                console.print("\n[green]Windows build completed successfully![/]")
        
        elif choice == "all":
            # Build all platforms
            results = builder.build_all_platforms()
            builder.generate_report(results)
            console.print("\n[green]Multi-platform build completed![/]")
        
        elif choice == "custom":
            # Custom platform selection
            platforms = prompt_custom_platforms()
            console.print(f"\n[cyan]Building platforms:[/] {', '.join(platforms)}")
            
            results = builder.build_custom_platforms(platforms)
            builder.generate_report(results)
            console.print("\n[green]Custom build completed![/]")
        
        elif choice == "exit":
            console.print("\n[yellow]Goodbye![/]")
            sys.exit(0)
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Build cancelled by user.[/]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]An error occurred: {e}[/]")
        console.print("\n[dim]For help, check the documentation or create an issue on GitHub.[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()