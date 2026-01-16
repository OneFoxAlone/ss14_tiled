# CHANGELOG

## [Unreleased] 2025-11-17-2025-01-15

### Added

#### Performance Optimizations
- **Parallel Image Processing**
  - Decals, tiles, and entities now process in parallel using ThreadPoolExecutor (4 concurrent workers)
  - Significant speed improvement on multi-core systems
  - Better CPU utilization during generation

- **PNG Color Profile Caching**
  - Global cache prevents reprocessing of already-fixed PNG files
  - Eliminates duplicate work when same sprites are referenced multiple times
  - `_PNG_FIX_CACHE` tracks processed files in `shared.py`

#### Enhanced Error Handling & Reporting
- **Improved Error Messages**
  - Full Python traceback displayed for debugging
  - Shows exact file paths causing YAML parsing errors

- **YAML File Robustness**
  - Automatic tab-to-space conversion for YAML files with tabs (which are not valid YAML)
  - Better handling of null entries in YAML arrays
  - Better error recovery - skips problematic entries and continues processing

#### Bug Fixes
- **Fixed Directory Creation** 
  - `.data` and `.images` output directories now created properly
  - Fixed `'NoneType' object has no attribute 'write'` error
  - Works with custom output paths from GUI

- **Fixed Image Padding Calculation**
  - Multi-layer entity compositing now handles odd-sized images correctly
  - Resolved `AssertionError` when compositing layers of different dimensions
  - Proper center padding for sprite composition

- **Enhanced Output Path Support**
  - `generate()` function now accepts optional `output_path` parameter
  - GUI passes selected output directory to generation engine
  - Maintains backward compatibility with default `dist/` directory

#### GUI Application
- **PyQt6-based GUI** (`ss14_tiled/gui.py`)
  - Folder browser for selecting SS14 repository
  - Real-time progress logging during tileset generation
  - Visual progress bar during generation
  - Quick access button to open output folder
  - Responsive, threaded design (UI stays responsive during generation)
  - Error handling with user-friendly dialogs
  - Full traceback display for debugging errors

- **GUI Entry Point** (`ss14_tiled/gui_main.py`)
  - Dedicated entry point for running the GUI application
  - Automatic dependency checking and installation on first run
  - Added entry point in `pyproject.toml`: `ss14-tiled-gui`

#### Automatic Dependency Management
- **Dependency Manager** (`ss14_tiled/dependencies.py`)
  - Automatic detection of missing dependencies
  - Automatic installation of required packages on first run
  - Cache system to prevent repeated installation checks
  - Progress feedback during installation
  - Works in both development and packaged environments

#### Standalone EXE Distribution
- **PyInstaller Configuration** (`build.spec`)
  - Complete specification for building standalone Windows EXE
  - Includes data files and hidden imports
  - Optimized for distribution
  
- **Build Script** (`build_exe.py`)
  - Automated build process for creating EXE
  - Automatic PyInstaller installation if needed
  - Clean old builds before new build
  - Clear status messages and output location

#### Testing & Verification
- **Verification Script** (`verify.py`)
  - Tests all dependencies are installed
  - Tests GUI import
  - Tests CLI import
  - Tests CLI functionality
  - Checks PyInstaller availability
  - Provides clear pass/fail summary

## Technical Details

### Dependencies Added
- PyQt6 (modern GUI framework)
- PyQt6-Qt6 (Qt bindings)
- PyInstaller (for EXE building - build-only)

### Python Version
- Requires Python 3.11+
- Tested on Windows 10/11

### Platform Support
- **Primary**: Windows 10/11 (EXE distribution)
- **Secondary**: Linux/macOS (source installation with Python)
- **Development**: All platforms with Python 3.11+

## Contributors

- GUI Implementation: PyQt6 application framework
- Dependency Manager: Custom solution for EXE distribution
- Build System: PyInstaller integration
- Original Code: 
