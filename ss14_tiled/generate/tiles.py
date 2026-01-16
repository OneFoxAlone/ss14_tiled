"""Everything for the "tile"-tiles."""
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import cv2
import yaml

from ..shared import CacheJSON, Image, create_tsx, remove_prefix, fix_png_color_profile, eprint


def create_tiles(root: Path, out: Path):
    """Create the "tile"-tiles. As in the floor."""
    existing_out = out / ".data" / "tiles.json"
    existing = CacheJSON.from_json(existing_out)

    tiles_out = out / ".images" / "tiles"
    tiles_out.mkdir(parents=True, exist_ok=True)

    resources_dir = root / "Resources"
    yml_dir = resources_dir / "Prototypes/Tiles"
    files = [x for x in yml_dir.glob("**/*.yml") if x.is_file()]

    # Collect all tiles to process
    tiles_to_process = []
    for file in files:
        try:
            file_content = file.read_text("UTF-8")
            # Convert tabs to spaces (YAML doesn't allow tabs)
            file_content = file_content.replace('\t', '    ')
            tiles_data = yaml.safe_load(file_content)
        except yaml.YAMLError as e:
            eprint(f"Error parsing YAML file {file}: {str(e)}")
            continue
        
        if not tiles_data:
            continue
        
        for tile in tiles_data:
            if not tile or tile.get("type") != "tile":
                continue  # alias or null entry
            if not "sprite" in tile:
                continue  # space
            if not "variants" in tile:
                tile["variants"] = 1
            tiles_to_process.append((tile, resources_dir, tiles_out))

    # Process tiles in parallel
    def process_tile(args):
        tile, resources_dir, tiles_out = args
        try:
            sprite = resources_dir / remove_prefix(tile["sprite"], "/")
            
            # Fix PNG color profile issues before processing
            fix_png_color_profile(sprite)
            
            dest: Path = tiles_out / (tile["id"] + sprite.suffix)
            img = cv2.imread(str(sprite), cv2.IMREAD_UNCHANGED)
            if img is None:
                eprint(f"Failed to read tile sprite: {sprite}")
                return None
            
            height, width = img.shape[:2]
            width //= tile["variants"]  # only take the first variant
            cv2.imwrite(str(dest), img[0:height, 0:width])
            
            return (tile["id"], width, height, dest.name)
        except Exception as e:
            eprint(f"Error processing tile {tile.get('id', 'unknown')}: {str(e)}")
            return None

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_tile, args) for args in tiles_to_process]
        for future in as_completed(futures):
            result = future.result()
            if result:
                tile_id, width, height, dest_name = result
                if tile_id not in existing.ids:
                    existing.ids.append(tile_id)
                    existing.images.append(
                        Image(f"./.images/tiles/{dest_name}", str(width), str(height)))

    existing_out.write_text(json.dumps(existing, default=vars), "UTF-8")
    create_tsx(existing, "Tiles", out / "tiles.tsx")
