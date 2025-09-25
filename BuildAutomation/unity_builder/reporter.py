"""
HTML report generation module for Unity Build Automation.
Creates beautiful build reports with timing, size, and version information.

MIT License - Copyright (c) 2025 Angry Shark Studio
"""

import webbrowser
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from rich.console import Console

console = Console()


class Reporter:
    """Generates HTML build reports."""
    
    def __init__(self, config: Any) -> None:
        """Initialize with configuration object."""
        self.config = config
    
    def generate_report(self, build_results: List[Dict[str, Any]]) -> Path:
        """Generate HTML build report and return the path."""
        report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = self._generate_html(build_results, report_time)
        
        # Save report
        report_dir = self.config.project_root / "BuildAutomation"
        report_dir.mkdir(exist_ok=True)
        report_path = report_dir / "build_report.html"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        console.print(f"\n[green]Build report saved to:[/] BuildAutomation/build_report.html")
        
        # Try to open in browser
        try:
            webbrowser.open(f"file://{report_path}")
            console.print("[dim]   (Opened in your default browser)[/]")
        except:
            pass
        
        return report_path
    
    def _generate_html(self, build_results: List[Dict[str, Any]], report_time: str) -> str:
        """Generate the HTML content for the report."""
        # Count statistics
        total_builds = len(build_results)
        successful_builds = sum(1 for r in build_results if r['status'] == 'success')
        failed_builds = sum(1 for r in build_results if r['status'] == 'failed')
        skipped_builds = sum(1 for r in build_results if r['status'] == 'skipped')
        
        # Generate build rows
        build_rows = self._generate_build_rows(build_results)
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Unity Build Report - {self.config.project_name} v{self.config.project_version}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .version-badge {{
            background: #4CAF50;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 16px;
            font-weight: normal;
        }}
        .summary {{
            background-color: #f8f9fa;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }}
        .summary-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        .summary-row:last-child {{
            border-bottom: none;
        }}
        .summary-label {{
            font-size: 13px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }}
        .summary-value {{
            font-size: 15px;
            color: #212529;
            font-weight: 500;
        }}
        .stats {{
            display: flex;
            gap: 20px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        .stat-card {{
            flex: 1;
            min-width: 150px;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 2px solid transparent;
        }}
        .stat-card.success {{
            border-color: #4CAF50;
        }}
        .stat-card.failed {{
            border-color: #f44336;
        }}
        .stat-card.skipped {{
            border-color: #ff9800;
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .success {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .failed {{
            color: #f44336;
            font-weight: bold;
        }}
        .skipped {{
            color: #ff9800;
            font-weight: bold;
        }}
        .path {{
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            color: #666;
            word-break: break-all;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
        .footer a {{
            color: #4CAF50;
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
        .icon {{
            width: 20px;
            height: 20px;
            vertical-align: middle;
            margin-right: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>
            Unity Build Report
            <span class="version-badge">v{self.config.project_version}</span>
        </h1>
        
        <div class="summary">
            <div class="summary-row">
                <span class="summary-label">Project</span>
                <span class="summary-value">{self.config.project_name}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Company</span>
                <span class="summary-value">{self.config.company_name}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Build Date</span>
                <span class="summary-value">{report_time}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Unity Version</span>
                <span class="summary-value">{self.config.unity_version}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Bundle ID</span>
                <span class="summary-value">{self.config.bundle_identifier}</span>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_builds}</div>
                <div class="stat-label">Total Builds</div>
            </div>
            <div class="stat-card success">
                <div class="stat-number" style="color: #4CAF50;">{successful_builds}</div>
                <div class="stat-label">Successful</div>
            </div>
            <div class="stat-card failed">
                <div class="stat-number" style="color: #f44336;">{failed_builds}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card skipped">
                <div class="stat-number" style="color: #ff9800;">{skipped_builds}</div>
                <div class="stat-label">Skipped</div>
            </div>
        </div>
        
        <table>
            <tr>
                <th>Platform</th>
                <th>Status</th>
                <th>Build Time</th>
                <th>Size</th>
                <th>Output Path</th>
            </tr>
            {build_rows}
        </table>
        
        <div class="footer">
            Generated by Unity Build Automation - Zero Configuration Edition<br>
            <a href="https://github.com/angrysharkstudio/Unity-Python-Build-Automation">View on GitHub</a> | 
            <a href="https://angrysharkstudio.com/blog/python-unity-build-automation-tutorial">Read the Tutorial</a><br>
            <small>Project Version: {self.config.project_version} | Report Generated: {report_time}</small>
        </div>
    </div>
</body>
</html>
"""
    
    def _generate_build_rows(self, build_results: List[Dict[str, Any]]) -> str:
        """Generate table rows for build results."""
        from .platforms import PlatformBuilder
        
        rows = []
        
        for result in build_results:
            platform = PlatformBuilder.PLATFORMS[result['platform']]['name']
            
            if result['status'] == 'success':
                status_class = 'success'
                status_text = 'Success'
            elif result['status'] == 'failed':
                status_class = 'failed'
                status_text = 'Failed'
            elif result['status'] == 'skipped':
                status_class = 'skipped'
                status_text = f"Skipped"
                if 'reason' in result:
                    status_text += f" ({result['reason']})"
            else:
                status_class = 'failed'
                status_text = 'Error'
            
            time_text = f"{result.get('time', 0):.1f}s" if 'time' in result else 'N/A'
            size_text = f"{result.get('size_mb', 0):.1f} MB" if 'size_mb' in result else 'N/A'
            
            # Format path
            if 'output_path' in result:
                path_obj = Path(result['output_path'])
                try:
                    relative_path = path_obj.relative_to(self.config.project_root)
                    path_text = str(relative_path).replace('\\', '/')
                except:
                    path_text = str(path_obj)
            else:
                path_text = 'N/A'
            
            rows.append(f"""
            <tr>
                <td>{platform}</td>
                <td class="{status_class}">{status_text}</td>
                <td>{time_text}</td>
                <td>{size_text}</td>
                <td class="path">{path_text}</td>
            </tr>
            """)
        
        return ''.join(rows)