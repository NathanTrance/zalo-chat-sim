#!/usr/bin/env python3
"""Build a contact sheet of the rendered screenshots for quick visual review."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(ROOT / "out" / "manifest.jsonl"))
    ap.add_argument("--screens", default=str(ROOT / "out" / "screens"))
    ap.add_argument("--theme", default="dark")
    ap.add_argument("--device", default="screen_1440x3200")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--out", default=str(ROOT / "out" / "contact_sheet.jpg"))
    args = ap.parse_args()

    entries = [json.loads(l) for l in Path(args.manifest).read_text(encoding="utf-8").splitlines() if l.strip()]
    entries = [e for e in entries if e["theme"] == args.theme and e["device"] == args.device]
    if not entries:
        raise SystemExit("no matching entries")

    thumb_w, gap, label_h = 300, 24, 34
    src_w = entries[0]["width_px"]
    src_h = entries[0]["height_px"]
    scale = thumb_w / src_w
    thumb_h = round(src_h * scale)
    cols = args.cols
    rows = (len(entries) + cols - 1) // cols
    pad = 24
    W = pad * 2 + cols * thumb_w + (cols - 1) * gap
    H = pad * 2 + rows * (thumb_h + label_h) + (rows - 1) * gap

    sheet = Image.new("RGB", (W, H), (18, 20, 24))
    d = ImageDraw.Draw(sheet)

    for i, e in enumerate(entries):
        name = e.get("image") or e.get("image_jpeg")
        img = Image.open(Path(args.screens) / name).convert("RGB")
        img = img.resize((thumb_w, thumb_h), Image.LANCZOS)
        r, c = divmod(i, cols)
        x = pad + c * (thumb_w + gap)
        y = pad + r * (thumb_h + label_h + gap)
        sheet.paste(img, (x, y))
        d.text((x + 2, y + thumb_h + 8), e["id"], fill=(210, 214, 220))
        d.text((x + 2, y + thumb_h + 20), f"{e['theme']} / {e['device']}", fill=(130, 136, 146))

    sheet.save(args.out, quality=90)
    print(f"wrote {args.out} ({len(entries)} thumbs, {W}x{H})")


if __name__ == "__main__":
    main()
