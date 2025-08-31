"""
Main Unity Auto Builder class that orchestrates the build process.
Coordinates between config, platforms, and reporting modules.

MIT License - Copyright (c) 2025 Angry Shark Studio
"""

from typing import List, Optional
from rich.console import Console
from .config import Config
from .platforms import PlatformBuilder
from .reporter import Reporter
from .utils import show_welcome_banner, format_time_duration

console = Console()


class UnityAutoBuilder:
    """Main class that orchestrates Unity builds."""
    
    def __init__(self):
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
    
    def build_windows(self) -> bool:
        """Build for Windows platform only."""
        return self.platform_builder.build_platform("windows")
    
    def build_all_platforms(self) -> List[dict]:
        """Build for all available platforms."""
        results = self.platform_builder.build_all_platforms()
        return results
    
    def build_custom_platforms(self, platforms: List[str]) -> List[dict]:
        """Build for custom selection of platforms."""
        results = self.platform_builder.build_selected_platforms(platforms)
        return results
    
    def generate_report(self, build_results: Optional[List[dict]] = None):
        """Generate HTML report for build results."""
        if build_results is None:
            build_results = self.platform_builder.build_results
        
        if not build_results:
            console.print("[yellow]No build results to report.[/]")
            return
        
        self.reporter.generate_report(build_results)
    
    def get_build_results(self) -> List[dict]:
        """Get the current build results."""
        return self.platform_builder.build_results