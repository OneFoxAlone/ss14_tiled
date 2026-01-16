"""Automatic dependency installation system."""
import subprocess
import sys
import json
from pathlib import Path


class DependencyManager:
    """Manages installation of required dependencies."""
    
    REQUIREMENTS_FILE = Path(__file__).parent.parent / "requirements.txt"
    CACHE_FILE = Path.home() / ".ss14_tiled_deps_installed"
    
    @classmethod
    def get_required_packages(cls) -> list[str]:
        """Parse and return required packages from requirements.txt."""
        if not cls.REQUIREMENTS_FILE.exists():
            return []
        
        packages = []
        with open(cls.REQUIREMENTS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    packages.append(line)
        return packages
    
    @classmethod
    def are_dependencies_installed(cls) -> bool:
        """Check if dependencies have been installed."""
        # For development/testing: check if cache file exists
        if cls.CACHE_FILE.exists():
            return True
        
        # Check if key packages are importable
        key_packages = ['cv2', 'PyQt6', 'yaml']  # opencv-python, PyQt6, pyyaml
        for package in key_packages:
            try:
                __import__(package)
            except ImportError:
                return False
        return True
    
    @classmethod
    def install_dependencies(cls) -> bool:
        """Install all required dependencies."""
        packages = cls.get_required_packages()
        
        if not packages:
            return True
        
        try:
            print("Installing required dependencies...")
            for package in packages:
                print(f"  Installing {package}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--quiet", package],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print(f"    Warning: Failed to install {package}")
                    print(f"    {result.stderr}")
            
            # Mark dependencies as installed
            cls.CACHE_FILE.write_text(json.dumps({"installed": True}))
            print("Dependencies installed successfully!")
            return True
        except Exception as e:
            print(f"Error installing dependencies: {e}")
            return False


def ensure_dependencies():
    """Ensure all dependencies are installed before importing."""
    if not DependencyManager.are_dependencies_installed():
        print("First-time setup: Installing required dependencies...")
        success = DependencyManager.install_dependencies()
        if not success:
            print("Warning: Some dependencies may not have installed correctly.")
            print("The application may not work properly.")
