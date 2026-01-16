#!/usr/bin/env python3
"""Build script for creating SS14 Tiled standalone EXE."""

import subprocess
import sys
from pathlib import Path

def main():
    """Build the EXE using PyInstaller."""
    print("=" * 80)
    print("SS14 Tiled - EXE Build Script")
    print("=" * 80)
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed")
    
    print()
    
    # Clean old builds
    build_dir = Path("build")
    dist_dir = Path("dist")
    
    if build_dir.exists():
        print(f"Cleaning old build directory: {build_dir}")
        import shutil
        shutil.rmtree(build_dir)
    
    if dist_dir.exists():
        print(f"Cleaning old dist directory: {dist_dir}")
        import shutil
        shutil.rmtree(dist_dir)
    
    print()
    print("Building EXE with PyInstaller...")
    print()
    
    # Run PyInstaller
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "build.spec",
            "--clean"
        ])
        print()
        print("=" * 80)
        print("Build successful!")
        print("=" * 80)
        print()
        print(f"Output: {dist_dir / 'SS14Tiled.exe'}")
        print()
        print()
        return 0
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 80)
        print("Build failed!")
        print("=" * 80)
        print(f"Error: {e}")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
