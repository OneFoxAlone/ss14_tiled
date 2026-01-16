"""Expose a "generate"-function."""
from pathlib import Path

from .decals import create_decals
from .entities import create_entities
from .tiles import create_tiles


def generate(root: Path, progress_callback=None, output_path=None):
    """Create tile-sets for Tiled.
    
    Args:
        root: Path to SS14 repository
        progress_callback: Optional function to call with (current, total) progress updates
        output_path: Optional output directory path (defaults to 'dist')
    """
    if output_path is None:
        out = Path("dist")
    else:
        out = Path(output_path)
    out.mkdir(parents=True, exist_ok=True)
    (out / ".data").mkdir(exist_ok=True)
    (out / ".images").mkdir(exist_ok=True)

    # Each generation step gets ~33% of the progress
    if progress_callback:
        progress_callback(0, 100)
    
    create_decals(root, out)
    if progress_callback:
        progress_callback(33, 100)
    
    create_entities(root, out)
    if progress_callback:
        progress_callback(66, 100)
    
    create_tiles(root, out)
    if progress_callback:
        progress_callback(100, 100)
