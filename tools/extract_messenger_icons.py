"""Extract the visible Messenger controls from the Pixel 10 emulator captures.

The APK exposes a named thumbs-up resource, but most current controls are
obfuscated or drawn at runtime. These crops preserve the actual rendered shape.
Run from the repository root after placing mess_light_v2.png and
mess_dark_v2.png in out/pixel10/screens.
"""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "out" / "pixel10" / "screens"
DEST = ROOT / "assets" / "messenger"

# Exact Android accessibility button bounds in the 1280x2856 capture.
BOUNDS = {
    "back": (12, 169, 156, 313),
    "phone": (836, 169, 980, 313),
    "video": (980, 169, 1124, 313),
    "info": (1124, 169, 1268, 313),
    "plus": (20, 2650, 100, 2738),
    "camera": (120, 2604, 240, 2784),
    "gallery": (240, 2604, 360, 2784),
    "mic": (360, 2604, 480, 2784),
    "smile": (1061, 2661, 1127, 2727),
    "like": (1170, 2650, 1260, 2738),
}


def extract(source: Image.Image, bounds, background):
    crop = source.crop(bounds).convert("RGBA")
    px = crop.load()
    width, height = crop.size
    active = []
    for y in range(height):
        for x in range(width):
            rgb = px[x, y][:3]
            distance = max(abs(rgb[i] - background[i]) for i in range(3))
            # Screenshots are lossless. Small differences are antialias pixels.
            if distance <= 2:
                px[x, y] = (0, 0, 0, 0)
            else:
                px[x, y] = (*rgb, 255)
                if distance > 20:
                    active.append((x, y))
    if not active:
        raise ValueError(f"empty icon at {bounds}")
    x0 = max(0, min(x for x, _ in active) - 2)
    y0 = max(0, min(y for _, y in active) - 2)
    x1 = min(width, max(x for x, _ in active) + 3)
    y1 = min(height, max(y for _, y in active) + 3)
    return crop.crop((x0, y0, x1, y1))


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    for theme in ("light", "dark"):
        source = Image.open(SOURCE / f"mess_{theme}_v2.png").convert("RGBA")
        if source.size != (1280, 2856):
            raise ValueError(f"unexpected {theme} capture size: {source.size}")
        for name, bounds in BOUNDS.items():
            bg = source.getpixel((700, 2700))[:3] if name == "smile" else (
                (255, 255, 255) if theme == "light" else (0, 0, 0))
            icon = extract(source, bounds, bg)
            target = DEST / f"{name}_{theme}.png"
            icon.save(target)
            print(target.relative_to(ROOT), icon.size)


if __name__ == "__main__":
    main()
