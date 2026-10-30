"""Screenshot the HTML with Chromium and write PNG + JPEG + label sidecar."""

import json
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

from .labels import labels
from .screen import build_html
from .theme import DEVICES

ROOT = Path(__file__).resolve().parents[2]
FONT = ROOT / "assets" / "fonts" / "Roboto.ttf"


def _font_uri() -> str:
    if not FONT.exists():
        raise SystemExit(f"Missing font: {FONT}")
    return FONT.as_uri()


def _resolve_assets(dlg: dict) -> dict:
    """Turn `assets/...` paths into file:// URIs so the page can load them."""
    out = json.loads(json.dumps(dlg))
    for m in out.get("messages", []):
        a = m.get("asset")
        if a and not a.startswith(("file:", "http:", "https:", "data:")):
            m["asset"] = (ROOT / a).resolve().as_uri()
    return out


def _row_metrics(page):
    return page.evaluate(
        """() => {
             const chat = document.querySelector('.chat').getBoundingClientRect();
             const rows = Array.from(document.querySelectorAll('[data-idx]')).map(el => {
               const cs = getComputedStyle(el);
               return {idx:+el.dataset.idx,
                       h: el.getBoundingClientRect().height,
                       mt: parseFloat(cs.marginTop) || 0};
             });
             return {chat_h: chat.height, rows};
           }"""
    )


def choose_window(page, end_exclusive: int):
    """Pick a message window that is slightly taller than the chat area.

    The window is bottom-anchored, so the newest message sits above the composer
    and the oldest one is cut by the top edge -- a normal scrolled screenshot.
    If the requested slice is too short to fill the screen, the end is extended
    towards the newest message so the shot does not end up half empty.
    """
    m = _row_metrics(page)
    rows = m["rows"]
    chat_h = m["chat_h"]
    if not rows:
        return 0, end_exclusive

    heights = {r["idx"]: r["h"] for r in rows}
    margins = {r["idx"]: r["mt"] for r in rows}

    def slice_h(start, end):
        idxs = [i for i in heights if start <= i < end]
        if not idxs:
            return 0.0
        return sum(heights[i] for i in idxs) + sum(margins[i] for i in idxs)

    end = min(max(1, end_exclusive), max(heights) + 1)
    if slice_h(0, end) < chat_h:
        end = max(heights) + 1

    start = 0
    total = 0.0
    for i in range(end - 1, -1, -1):
        if i not in heights:
            continue
        total += heights[i] + margins[i]
        start = i
        if total >= chat_h:
            break
    return start, end


def _apply_window(page, start: int, end: int):
    page.evaluate(
        """([start, end]) => {
             document.querySelectorAll('[data-idx]').forEach(el => {
               const i = +el.dataset.idx;
               el.style.display = (i >= start && i < end) ? '' : 'none';
             });
           }""",
        [start, end],
    )
    page.wait_for_timeout(20)


def _bboxes(page, dpr: float):
    raw = page.evaluate(
        """() => {
             const chat = document.querySelector('.chat').getBoundingClientRect();
             return Array.from(document.querySelectorAll('[data-idx]'))
               .filter(el => el.offsetParent !== null)
               .map(el => {
                 const r = el.getBoundingClientRect();
                 const b = el.querySelector('.bubble, .sticker');
                 const br = b ? b.getBoundingClientRect() : r;
                 const top = Math.max(br.top, chat.top), bot = Math.min(br.bottom, chat.bottom);
                 const vis = br.height ? Math.max(0, bot - top) / br.height : 0;
                 return {idx:+el.dataset.idx, x:br.left, y:br.top, w:br.width, h:br.height,
                         vis: Math.round(vis*1000)/1000,
                         in_chat: br.top >= chat.top - 0.5 && br.bottom <= chat.bottom + 0.5};
               });
           }"""
    )
    return [
        {
            "message_index": b["idx"],
            "x": round(b["x"] / dpr, 1),
            "y": round(b["y"] / dpr, 1),
            "w": round(b["w"] / dpr, 1),
            "h": round(b["h"] / dpr, 1),
            "visible_ratio": b["vis"],
            "fully_visible": b["in_chat"],
        }
        for b in raw
    ]


class Renderer:
    def __init__(self, channel: str = "chromium"):
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(channel=channel)
        self._page = None

    def _get_page(self, dev):
        if self._page is None:
            self._page = self._browser.new_page(
                viewport={"width": dev["w"], "height": dev["h"]},
                device_scale_factor=1,
            )
        else:
            self._page.set_viewport_size({"width": dev["w"], "height": dev["h"]})
        return self._page

    def close(self):
        self._browser.close()
        self._pw.stop()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def render(self, dlg: dict, theme: str, device: str, out_dir: Path,
               formats=("png", "jpg", "json"), window=None, window_index: int = 0) -> dict:
        dlg = _resolve_assets(dlg)
        dev = DEVICES[device]
        stem = f"{dlg['id']}__{theme}__{device}__w{window_index}"
        out_dir = Path(out_dir).resolve()
        (out_dir / "html").mkdir(parents=True, exist_ok=True)
        (out_dir / "screens").mkdir(parents=True, exist_ok=True)

        html_path = out_dir / "html" / f"{stem}.html"
        html_path.write_text(
            build_html(dlg, theme, device, _font_uri()), encoding="utf-8"
        )

        total = len(dlg["messages"])
        # window = (start, end) message indices to show; default: tail of the chat
        if window is None:
            end = total
        else:
            end = max(1, min(total, int(window[1])))
        end = max(1, end)

        page = self._get_page(dev)
        page.goto(html_path.as_uri(), wait_until="load")
        page.evaluate("document.fonts.ready")

        start, end = choose_window(page, end)
        _apply_window(page, start, end)

        png = out_dir / "screens" / f"{stem}.png"
        jpg = out_dir / "screens" / f"{stem}.jpg"
        if "png" in formats:
            page.screenshot(path=str(png))
            if "jpg" in formats:
                Image.open(png).convert("RGB").save(
                    jpg, "JPEG", quality=88, subsampling=2
                )
        elif "jpg" in formats:
            page.screenshot(path=str(jpg), type="jpeg", quality=88)
        boxes = _bboxes(page, dev["dpr"])

        visible = {b["message_index"] for b in boxes if b["fully_visible"]}
        meta = labels(dlg, theme, device, visible)
        meta.update(
            {
                "image": png.name if "png" in formats else None,
                "image_jpeg": jpg.name if "jpg" in formats else None,
                "width_px": dev["w"],
                "height_px": dev["h"],
                "dpr": dev["dpr"],
                "width_dp": round(dev["w"] / dev["dpr"], 1),
                "height_dp": round(dev["h"] / dev["dpr"], 1),
                "window": {"index": window_index, "start": start, "end": end, "total": total},
                "label_source": "synthetic",
                "bboxes_dp": boxes,
                "clipped_indices": sorted(
                    {b["message_index"] for b in boxes if not b["fully_visible"]}
                ),
            }
        )
        if "json" in formats:
            (out_dir / "screens" / f"{stem}.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        return meta
