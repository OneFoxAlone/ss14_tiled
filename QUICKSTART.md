# SS14 Tiled - Quick Start

## For Users: Running the GUI Application

### Download Pre-built EXE
1. Download `SS14Tiled.exe` from the [releases page](https://github.com/OneFoxAlone/ss14_tiled/releases)
2. Double-click to run
3. On first run, it automatically installs dependencies (internet required)
4. Select your SS14 folder using the "Browse..." button
5. Click "Generate Tileset"
6. Wait for completion, then use the generated files in Tiled

### Build EXE from Source
1. Clone the repository: `git clone https://github.com/OneFoxAlone/ss14_tiled`
2. `cd ss14_tiled`
3. Run: `python build_exe.py`
4. The EXE will be in `dist/SS14Tiled.exe`

### Run from Source (Requires Python)
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run GUI: `python -m ss14_tiled.gui_main`

## GUI Features
- SS14 Folder Selection
- Live Log
- Output Folder Selection

## Using the Generated Tilesets in Tiled
1. Open Tiled Map Editor
2. Go to "Tilesets" panel (usually on the right)
3. Drag and drop `.tsx` files from the `dist` folder
4. Ensure tile size is set to 32x32 (SS14 standard)
5. Create new maps and start editing!

## Troubleshooting

### "Python not found"
- Download Python 3.11+ from [python.org](https://www.python.org/)
- Add Python to PATH during installation

### EXE doesn't start
- Check internet connection (needed for first-run dependency installation)
- Try running from command prompt to see error messages
- Make sure you have write permissions

### Generation fails
- Verify the SS14 folder path is correct
- Check the log for specific error messages
- Ensure SS14 repository has expected structure

### Dependencies won't install
- Check your internet connection
- Try running as Administrator
- Manually delete: `C:\Users\{YourUsername}\.ss14_tiled_deps_installed`

## For Developers

### Development Setup
```powershell
git clone https://github.com/OneFoxAlone/ss14_tiled
cd ss14_tiled
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Running in Development Mode
```powershell
# GUI mode
python -m ss14_tiled.gui_main

# CLI mode
python -m ss14_tiled C:\path\to\ss14
```

### Building for Release
```powershell
python build_exe.py
```

The built EXE is in `dist/SS14Tiled.exe`
