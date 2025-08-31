"""
Unity Build Automation - Zero Configuration Edition
A modular Python package for automating Unity builds across multiple platforms.

MIT License - Copyright (c) 2025 Angry Shark Studio
"""

from .builder import UnityAutoBuilder
from .config import Config

__version__ = "1.0.0"
__all__ = ["UnityAutoBuilder", "Config"]