#!/usr/bin/env python3
"""
JVM Project Tooling Scanner — backwards-compatible wrapper.

This script delegates to scan_jvm.py. For multi-ecosystem scanning,
use scan_project.py instead.

Usage:
    python3 scan_tooling.py <project_root>
    python3 scan_tooling.py --recursive <project_root>
"""

import sys
from pathlib import Path

# Import the actual scanner
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scan_jvm import main

if __name__ == "__main__":
    main()
