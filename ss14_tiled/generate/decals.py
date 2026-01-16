"""Everything for the "decal"-tiles."""
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import cv2
import yaml

from ..shared import CacheJSON, Image, create_tsx, remove_prefix, fix_png_color_profile, eprint


def create_decals(root: Path, out: Path):
    """Create the "decals"-tiles."""
    _create_decals(root, out)
    for (name, color) in get_colors(root):
        _create_decals(root, out, name, color)


def _create_decals(root: Path, out: Path, name: str = "", color: str = "#FFF"):
    """(Internal) Create the "decals"-tiles."""
    dir_name = "decals"
    title = "Decals"
    if name:
        dir_name = f"decals_{name}"
        title = f"Decals - {name}"

    existing_out = out / ".data" / f"{dir_name}.json"
    existing = CacheJSON.from_json(existing_out)

    decals_out = out / ".images" / dir_name
    decals_out.mkdir(parents=True, exist_ok=True)

    resources_dir = root / "Resources"
    yml_dir = resources_dir / "Prototypes/Decals"
    files = [x for x in yml_dir.glob("**/*.yml") if x.is_file()]

    # Collect all decals to process
    decals_to_process = []
    for file in files:
        try:
            file_content = file.read_text("UTF-8")
            # Convert tabs to spaces (YAML doesn't allow tabs)
            file_content = file_content.replace('\t', '    ')
            data = yaml.safe_load(file_content)
        except yaml.YAMLError as e:
            eprint(f"Error parsing YAML file {file}: {str(e)}")
            continue
        
        if not data:
            continue
        
        for decal in data:
            if not decal or decal.get("type") != "decal":
                continue  # alias or null entry?
            decals_to_process.append((decal, resources_dir, decals_out, color, dir_name))

    # Process decals in parallel
    def process_decal(args):
        decal, resources_dir, decals_out, color, dir_name = args
        try:
            sprite: Path = resources_dir / "Textures" / \
                remove_prefix(decal["sprite"]["sprite"], "/Textures/") / \
                (str(decal["sprite"]["state"]) + ".png")
            dest: Path = decals_out / (str(decal["id"]) + sprite.suffix)
            
            # Fix PNG color profile issues before processing
            fix_png_color_profile(sprite)
            
            img = cv2.imread(str(sprite), cv2.IMREAD_UNCHANGED)
            if img is None:
                eprint(f"Failed to read decal sprite: {sprite}")
                return None
            
            height, width, dim = img.shape
            if dim == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
                dim = 4

            img = decal_colors(img, color)
            cv2.imwrite(str(dest), img)
            
            return (decal["id"], width, height, dir_name, dest.name)
        except Exception as e:
            eprint(f"Error processing decal {decal.get('id', 'unknown')}: {str(e)}")
            return None

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_decal, args) for args in decals_to_process]
        for future in as_completed(futures):
            result = future.result()
            if result:
                decal_id, width, height, dir_name, dest_name = result
                if decal_id not in existing.ids:
                    existing.ids.append(decal_id)
                    existing.images.append(
                        Image(f"./.images/{dir_name}/{dest_name}", str(width), str(height)))

    existing_out.write_text(json.dumps(existing, default=vars), "UTF-8")
    create_tsx(existing, title, out /
               f"{dir_name}.tsx", {"color_name": name, "color_value": color})


def parse_hex(color: str):
    """Parse a hex string to RGBA uint8."""
    if len(color) == 4:
        r = int(color[1], 16)
        r = r + (r << 4)
        g = int(color[2], 16)
        g = g + (g << 4)
        b = int(color[3], 16)
        b = b + (b << 4)
        return (r, g, b, 255)
    if len(color) == 5:
        (r, g, b, _) = parse_hex(color[:-1])
        a = int(color[4], 16)
        a = a + (a << 4)
        return (r, g, b, a)
    if len(color) == 7:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return (r, g, b, 255)
    if len(color) == 9:
        (r, g, b, _) = parse_hex(color[:-2])
        a = int(color[7:9], 16)
        return (r, g, b, a)
    raise ValueError("Unknown hex format.")


def decal_colors(img: cv2.Mat, color: str):
    """Scale the colors of an image."""
    (red, green, blue, alpha) = parse_hex(color)
    b, g, r, a = cv2.split(img)
    b = b * (blue / 255)
    g = g * (green / 255)
    r = r * (red / 255)
    a = a * (alpha / 255)
    return cv2.merge((b, g, r, a))


def get_colors(root: Path) -> list[(str, str)]:
    """Get all color names and values (for decals).

    Returns [("palette_color", "#value")]
    """
    resources_dir = root / "Resources"
    yml_dir = resources_dir / "Prototypes/Palettes"
    glob = yml_dir.glob("**/*")
    files = [x for x in glob if x.is_file()]

    results = []
    for file in files:
        data = yaml.safe_load(file.read_text("UTF-8"))
        for palette in data:
            if palette["type"] != "palette":
                continue  # alias?
            for color in palette["colors"]:
                results.append((
                    palette["name"] + "_" + color,
                    palette["colors"][color]
                ))

    return results
