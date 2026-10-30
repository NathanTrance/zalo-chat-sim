"""Generate a few photo-like assets used by image messages (no network needed)."""

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "photos"
FONT = ROOT / "assets" / "fonts" / "Roboto.ttf"
W, H = 640, 480


def _font(size):
    try:
        return ImageFont.truetype(str(FONT), size)
    except Exception:
        return ImageFont.load_default()


def doc_scan(path: Path):
    """A photographed receipt / printed page: the most OCR-useful asset."""
    img = Image.new("RGB", (W, H), (246, 245, 241))
    d = ImageDraw.Draw(img)
    # paper shadow + slight tilt illusion via margins
    d.rectangle([18, 12, W - 18, H - 12], fill=(252, 251, 248))
    y = 44
    d.text((42, y), "HOÁ ĐƠN THANH TOÁN", font=_font(28), fill=(25, 25, 28))
    y += 52
    d.text((42, y), "Cửa hàng: Minh Anh Mart", font=_font(21), fill=(40, 40, 45))
    y += 34
    d.text((42, y), "Địa chỉ: 128 Nguyễn Trãi, Q.1, TP.HCM", font=_font(19), fill=(55, 55, 60))
    y += 46
    rows = [
        ("Sữa tươi TH 1L", "32.000"),
        ("Bánh mì sandwich", "18.500"),
        ("Cà phê rang xay 250g", "95.000"),
        ("Nước suối Aquafina", "6.000"),
    ]
    for name, price in rows:
        d.text((42, y), name, font=_font(19), fill=(45, 45, 50))
        tw = d.textlength(price, font=_font(19))
        d.text((W - 52 - tw, y), price, font=_font(19), fill=(45, 45, 50))
        y += 30
    d.line([42, y + 6, W - 42, y + 6], fill=(180, 178, 172), width=2)
    y += 22
    d.text((42, y), "TỔNG CỘNG", font=_font(22), fill=(20, 20, 24))
    tw = d.textlength("151.500 đ", font=_font(22))
    d.text((W - 52 - tw, y), "151.500 đ", font=_font(22), fill=(20, 20, 24))
    y += 46
    d.text((42, y), "Ngày 12/10/2026  17:32", font=_font(18), fill=(70, 70, 76))
    d.text((42, y + 26), "Cảm ơn quý khách!", font=_font(18), fill=(70, 70, 76))
    img.save(path, quality=92)


def landscape(path: Path):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(250 - 120 * t)
        g = int(180 - 60 * t)
        b = int(140 + 40 * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))
    d.ellipse([430, 70, 520, 160], fill=(255, 236, 190))
    d.polygon([(0, 330), (170, 190), (330, 330)], fill=(96, 84, 74))
    d.polygon([(200, 340), (400, 175), (610, 340)], fill=(72, 62, 54))
    d.rectangle([0, 330, W, H], fill=(58, 62, 48))
    rnd = random.Random(7)
    for _ in range(160):
        x, y = rnd.randrange(W), rnd.randrange(345, H)
        d.line([(x, y), (x, y - rnd.randrange(4, 12))], fill=(88, 104, 62), width=2)
    img.save(path, quality=90)


def meal(path: Path):
    img = Image.new("RGB", (W, H), (196, 162, 128))
    d = ImageDraw.Draw(img)
    d.ellipse([120, 80, 520, 440], fill=(238, 233, 224))          # plate
    d.ellipse([170, 125, 470, 395], fill=(206, 150, 84))          # noodles
    d.ellipse([215, 170, 330, 270], fill=(120, 62, 44))           # meat
    d.ellipse([350, 200, 425, 275], fill=(88, 128, 60))           # herbs
    d.ellipse([330, 280, 420, 350], fill=(224, 196, 96))          # egg
    d.ellipse([240, 300, 300, 355], fill=(190, 70, 52))           # chili
    for i, (x, y, r) in enumerate([(470, 330, 26), (430, 380, 18), (500, 260, 14)]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 150, 80))
    img.save(path, quality=90)


def whiteboard(path: Path):
    img = Image.new("RGB", (W, H), (236, 240, 238))
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, W - 10, H - 10], outline=(150, 158, 154), width=6)
    y = 46
    d.text((44, y), "SPRINT 24 — CHECKLIST", font=_font(27), fill=(34, 62, 96))
    y += 54
    for line in [
        "1. Fix lỗi đăng nhập Zalo OA",
        "2. Test luồng thanh toán QR",
        "3. Viết báo cáo tuần 42",
        "4. Họp review thứ 6 lúc 15:00",
    ]:
        d.text((52, y), line, font=_font(22), fill=(48, 52, 58))
        y += 40
    d.line([50, y + 10, 320, y + 10], fill=(200, 60, 60), width=4)
    d.text((52, y + 26), "Deadline: 16/10", font=_font(22), fill=(180, 50, 50))
    img.save(path, quality=92)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    doc_scan(OUT / "doc_scan.jpg")
    landscape(OUT / "landscape.jpg")
    meal(OUT / "meal.jpg")
    whiteboard(OUT / "whiteboard.jpg")
    print(f"wrote 4 assets to {OUT}")


if __name__ == "__main__":
    main()
