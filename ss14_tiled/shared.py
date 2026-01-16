"""Shared stuffs and utility functions."""
import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

try:
    from PIL import Image as PILImage
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Global cache for fixed PNG files to avoid reprocessing
_PNG_FIX_CACHE = set()


def eprint(*args, **kwargs):
    """Print to std-error."""
    print(*args, file=sys.stderr, **kwargs)


def fix_png_color_profile(image_path: Path) -> None:
    """Fix PNG color profile issues by removing problematic iCCP chunks.
    
    Rewrites PNG files to remove incorrect color profile metadata that causes
    libpng warnings without affecting the actual image data.
    Uses caching to avoid reprocessing the same file.
    """
    if not HAS_PIL:
        return
    
    # Check cache first
    if str(image_path) in _PNG_FIX_CACHE:
        return
    
    try:
        if image_path.suffix.lower() != '.png':
            return
        
        # Open the PNG file
        img = PILImage.open(image_path)
        
        # Create a clean image without ICC profiles
        # Save with default parameters which won't include problematic profiles
        data = list(img.getdata())
        
        if img.mode == 'RGBA':
            clean_img = PILImage.new('RGBA', img.size)
        elif img.mode == 'RGB':
            clean_img = PILImage.new('RGB', img.size)
        elif img.mode == 'LA':
            clean_img = PILImage.new('LA', img.size)
        elif img.mode == 'L':
            clean_img = PILImage.new('L', img.size)
        elif img.mode == 'P':
            # Palette mode - keep palette but remove iCCP
            clean_img = PILImage.new('P', img.size)
            if img.palette:
                clean_img.putpalette(img.palette.getdata()[1])
        else:
            clean_img = PILImage.new(img.mode, img.size)
        
        clean_img.putdata(data)
        
        # Save without any color profiles, strips iCCP chunks
        clean_img.save(image_path, 'PNG', icc_profile=None)
        
        # Mark as fixed in cache
        _PNG_FIX_CACHE.add(str(image_path))
    except Exception:
        # Silently fail - file is still usable even if profile isn't fixed
        pass


@dataclass
class Image:
    """Image inside a tsx file."""
    source: str
    width: str
    height: str


@dataclass
class CacheJSON:
    """Cache file content."""
    ids: list[str]
    images: list[Image]

    @staticmethod
    def from_dict(d: dict) -> "CacheJSON":
        """Build this object recursively from a dict."""
        images = [Image(x["source"], x["width"], x["height"])
                  for x in d["images"]]
        return CacheJSON(d["ids"], images)

    @staticmethod
    def from_json(path: Path) -> "CacheJSON":
        """Build this object recursively from a given file."""
        path.parent.mkdir(exist_ok=True)
        existing: CacheJSON = CacheJSON([], [])
        if path.exists():
            existing = CacheJSON.from_dict(
                json.loads(path.read_text("UTF-8")))
            assert len(existing.ids) == len(existing.images)
        return existing


def create_tsx(cache: CacheJSON, name: str, output: Path, extra: dict = None):
    """All the XML writing."""
    root_element = ET.Element("tileset", name=name)

    if extra:
        properties = ET.SubElement(root_element, "properties")
        for (key, value) in extra.items():
            ET.SubElement(properties, "property", name=key, value=value)

    for i, image in enumerate(cache.images):
        ET.SubElement(
            ET.SubElement(root_element, "tile", id=str(i+1)),
            "image", source=image.source,
            width=str(image.width), height=str(image.height))
    ET.ElementTree(root_element).write(output,
                                       encoding="UTF-8", xml_declaration=True)


def add_transparent_image(background, foreground):
    """https://stackoverflow.com/a/59211216"""
    bg_h, bg_w, bg_channels = background.shape
    fg_h, fg_w, fg_channels = foreground.shape

    assert bg_h == fg_h
    assert bg_w == fg_w
    assert bg_channels == 4
    assert fg_channels == 4

    alpha_background = background[:, :, 3] / 255.0
    alpha_foreground = foreground[:, :, 3] / 255.0

    # set adjusted colors
    for color in range(0, 3):
        background[:, :, color] = alpha_foreground * foreground[:, :, color] + \
            alpha_background * background[:, :, color] * (1 - alpha_foreground)

    # set adjusted alpha and denormalize back to 0-255
    background[:, :, 3] = (1 - (1 - alpha_foreground)
                           * (1 - alpha_background)) * 255


def remove_prefix(string: str, prefix: str):
    """Remove a prefix from a string if it exists."""
    if string.startswith(prefix):
        return string[len(prefix):]
    return string
