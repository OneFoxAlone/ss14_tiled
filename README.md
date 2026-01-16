<p align="center">
  <img width="600" height="136" alt="outsetlogo" src="https://github.com/user-attachments/assets/38853c61-9245-426d-b66c-c8b1184f9bea" />
</p>

<p align="center">
  A Tiled converter for Space Station 14
</p>

<p align="center">
  <a href="QUICKSTART.md">Quickstart Guide</a>
</p>

## Prerequisites

Only necessary if you want to build the tile sets yourself.

- [Git](https://git-scm.com/)
- [Python >= 3.11](https://www.python.org/)
- Source code of SS14 (or a fork) somewhere on your system.
  - `git clone https://github.com/space-wizards/space-station-14/`

## Usage

### Windows Standalone EXE

Download the latest release from the [releases page](https://github.com/OneFoxAlone/ss14_tiled/releases) and run `Outset.exe`. On first run, it will automatically install required dependencies.

### CLI (Requires Python)

<table>
<tr>
<th>Linux</th>
<th>Windows</th>
</tr>
<tr>
<td>

```sh
# Setup
git clone https://github.com/OneFoxAlone/ss14_tiled
cd ss14_tiled
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Generate or update the tile sets.
python3 -m ss14_tiled /path/to/space-station-14/
```

</td>
<td>

```powershell
# Setup
git clone https://github.com/OneFoxAlone/ss14_tiled
cd ss14_tiled
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# CLI mode
python -m ss14_tiled /path/to/space-station-14/

# GUI mode
python -m ss14_tiled.gui_main
```

</td>
</tr>
</table>

- This creates a `dist` directory with all the tile sets..
- Once you got the tile sets (the `.tsx` files),
  you can create a new map in Tiled and drag them into "Tilesets" tab.
  - Make sure the tile size is set to 32x32 (default), as that's what SS14 uses.

## TODO

- [x] Import (SS14 -> Tiled)
  - [x] Decals
  - [x] Entities
  - [x] Tiles
- [ ] Export (Tiled -> SS14)
- [x] Easy-To-Use GUI
- [x] Performace Improvements & Fixes
</p>
