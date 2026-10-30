#!/usr/bin/env python3
"""Side-by-side of the real reference screenshot and a generated one."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=str(ROOT.parent / "images" / "zalo_1.jfif"))
    ap.add_argument("--gen", default=str(ROOT / "out" / "refcheck" / "screens" / "zalo_work_ml_01__dark__reference_928__w0.png"))
    ap.add_argument("--out", default=str(ROOT / "out" / "compare_reference.jpg"))
    args = ap.parse_args()

    a, b = Image.open(args.ref).convert("RGB"), Image.open(args.gen).convert("RGB")
    h = 900
    a = a.resize((round(a.width * h / a.height), h), Image.LANCZOS)
    b = b.resize((round(b.width * h / b.height), h), Image.LANCZOS)

    gap, pad, cap = 20, 16, 28
    W = pad * 2 + a.width + gap + b.width
    H = pad * 2 + h + cap
    sheet = Image.new("RGB", (W, H), (18, 20, 24))
    d = ImageDraw.Draw(sheet)
    sheet.paste(a, (pad, pad))
    sheet.paste(b, (pad + a.width + gap, pad))
    d.text((pad, pad + h + 8), "real Zalo (images/zalo_1.jfif)", fill=(200, 205, 212))
    d.text((pad + a.width + gap, pad + h + 8), "generated", fill=(200, 205, 212))
    sheet.save(args.out, quality=92)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
