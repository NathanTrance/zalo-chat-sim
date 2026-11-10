"""Messenger chat skin based on the Pixel 10 captures in out/pixel10."""

from pathlib import Path

from . import icons as device_icons
from . import theme as T
from .screen import _annotate, _initials, _row, esc
from .theme import DEVICES

ICON_SIZES = {
    "back": (58, 52), "phone": (60, 60), "video": (74, 50),
    "info": (64, 64), "plus": (68, 68), "camera": (68, 58),
    "gallery": (64, 58), "mic": (50, 64), "smile": (64, 64),
    "like": (64, 66),
}
ASSETS = Path(__file__).resolve().parents[2] / "assets" / "messenger"


def _asset_icon(name: str, theme: str) -> str:
    width, height = ICON_SIZES[name]
    uri = (ASSETS / f"{name}_{theme}.png").as_uri()
    return (f'<img src="{uri}" alt="" style="width:{width / 3:.3f}rem;'
            f'height:{height / 3:.3f}rem">')


def build_messenger_html(dlg: dict, theme_name: str, device: str, font_uri: str) -> str:
    if theme_name not in ("light", "dark"):
        raise ValueError(f"unsupported Messenger theme: {theme_name}")
    dev = DEVICES[device]
    dpr = dev["dpr"]
    pal = T.PALETTES[theme_name]
    conv = dlg["conversation"]
    ui = dlg.get("ui", {})
    sb = dlg.get("status_bar", {})
    nav_mode = ui.get("nav") or dev["nav"]
    nav_h = T.NAV_GESTURE_H if nav_mode == "gesture" else T.NAV_H
    if nav_mode == "gesture":
        nav_html = '<div class="nav gesture"><i class="pill"></i></div>'
    else:
        nav_html = (
            '<div class="nav">'
            f'<span class="nv">{device_icons.nav_recents(15)}</span>'
            f'<span class="nv">{device_icons.nav_home(15)}</span>'
            f'<span class="nv">{device_icons.nav_back(15)}</span>'
            '</div>'
        )
    messages = [dict(m) for m in dlg["messages"]]
    _annotate(messages, conv)
    # Messenger anchors the sender portrait to the final bubble of a run.
    for m in messages:
        if m["type"] != "date":
            m["_avatar"] = m["_last_in_run"]
    rows = "\n".join(_row(m, {}, conv, show_reaction_count=False) for m in messages)
    title = esc(conv.get("title", ""))
    avatar = esc(_initials(conv.get("title", "")))
    placeholder = esc(ui.get("messenger_placeholder") or "Nhắn tin")
    light = theme_name == "light"
    bg = "#fff" if light else "#000"
    fg = "#000" if light else "#fff"
    incoming = "#f2f4f7" if light else "#333334"
    field = "#f2f4f7" if light else "#333334"
    muted = "#737373" if light else "#aaa"
    reaction = "#f2f4f7" if light else "#333334"
    accent = "#071ab9" if light else "#3b60ff"
    outgoing = ("linear-gradient(to bottom,#1671ff 0%,#0865f8 30%,#0010b6 100%) fixed"
                if light else
                "linear-gradient(to bottom,#156dff 0%,#206bff 45%,#3b60ff 100%) fixed")
    icons = {name: _asset_icon(name, theme_name) for name in ICON_SIZES}
    media = sb.get("media")
    media_html = ""
    if media:
        media_html = (f'<div class="smedia">{device_icons.speaker(12)}'
                      f'<span>{esc(media)}</span></div><i class="sdot"></i>')
    wifi = device_icons.wifi(15) if sb.get("wifi", True) else ""
    bell = device_icons.bell_off(14) if sb.get("muted") else ""
    signal = device_icons.signal(15, sb.get("signal", 4))
    battery = device_icons.battery(15, sb.get("battery", 62))
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8">
<title>{esc(dlg.get("id", "messenger"))}</title><style>
@font-face {{font-family:Roboto;src:url("{font_uri}") format("truetype");font-weight:100 900;font-style:normal}}
* {{box-sizing:border-box}} html {{font-size:{dpr}px}} body {{margin:0;width:{dev['w']}px;height:{dev['h']}px;overflow:hidden;background:{pal['bar']};font-family:Roboto,"Segoe UI","Noto Sans",sans-serif;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}}
.screen {{height:100%;display:flex;flex-direction:column;background:{bg};color:{fg};overflow:hidden}}
.status {{height:{T.STATUS_H}rem;flex:none;background:{pal['bar']};display:flex;align-items:center;justify-content:space-between;padding:0 12rem 0 14rem;color:{pal['status_text']};font-size:{T.FONT_STATUS}rem;font-weight:600;letter-spacing:.01em}}
.sb-left,.sb-right {{display:flex;align-items:center}} .sb-left {{gap:7rem}} .sb-right {{gap:7rem}} .clock {{padding-top:.5rem}}
.smedia {{display:inline-flex;align-items:center;gap:4rem;background:#8C3B3B;color:#F7EDEA;border-radius:10rem;padding:1.5rem 8rem 1.5rem 6rem;font-size:11rem;font-weight:700;letter-spacing:.03em;margin-left:4rem}}
.smedia svg {{opacity:.95}} .sdot {{width:3.2rem;height:3.2rem;border-radius:50%;background:{pal['status_text']};opacity:.85}} .sb-right .i {{display:inline-flex;align-items:center;opacity:.95}}
.header {{height:56.67rem;flex:none;display:flex;align-items:center;gap:8rem;padding:0 12rem;background:{bg};box-shadow:0 1rem 3rem rgba(0,0,0,.12);z-index:2}}
.hbtn {{display:flex;align-items:center;justify-content:center;color:#5d4bff;flex:none}} .back {{width:28rem}}
.head-avatar {{height:36rem;width:36rem;border-radius:50%;background:linear-gradient(135deg,#658b74,#355a9c);color:white;display:grid;place-items:center;font-size:13rem;font-weight:700;position:relative;flex:none}}
.head-avatar:after,.av:not(.ghost):after {{content:"";position:absolute;right:-1rem;bottom:-1rem;width:9rem;height:9rem;border:2rem solid {bg};background:#31a64b;border-radius:50%}}
.titlebox {{min-width:0;flex:1;line-height:1.15}} .title {{font-size:{T.FONT_TITLE}rem;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}} .subtitle {{font-size:14rem;color:{muted};margin-top:3rem}}
.actions {{display:flex;align-items:center;gap:19rem;margin-left:6rem}} .actions .hbtn {{width:26rem}}
.chat {{flex:1;min-height:0;background:{bg};display:flex;flex-direction:column;justify-content:flex-end;overflow:hidden;padding:0 8rem 12rem 12rem}}
.row {{display:flex;align-items:flex-end;margin-top:2rem;gap:12rem}} .row.gap {{margin-top:14rem}} .row.out {{justify-content:flex-end}}
.row .av {{border-radius:50%;display:flex;align-items:center;justify-content:center;position:relative;flex:none;color:#fff;font-weight:600;letter-spacing:.02em;width:28rem!important;height:28rem!important}}
.row .av.ghost {{background:transparent}} .stack {{position:relative;max-width:74%}} .sender {{color:{muted};font-size:12rem;margin:0 0 3rem 6rem}}
.bubble {{background:{incoming};color:{fg};padding:8rem 12rem;border-radius:19rem;font-size:{T.FONT_TEXT}rem;line-height:{T.FONT_TEXT_LH}rem;word-break:break-word;overflow-wrap:anywhere}}
.out .bubble {{background:{outgoing};color:#fff}}
.txt {{white-space:pre-wrap}} .stamp {{display:none}} .bubble.media {{padding:0;overflow:visible;background:transparent}} .photo img {{display:block;width:299rem;height:224rem;max-width:100%;object-fit:cover;border-radius:19rem}} .bubble.media .cap {{display:table;background:{incoming};color:{fg};margin-top:2rem;padding:8rem 12rem;border-radius:19rem;max-width:299rem}}
.sticker {{font-family:"Segoe UI Emoji",sans-serif;font-size:65rem}} .reaction {{position:absolute;right:0;bottom:-14rem;min-width:32rem;height:21rem;display:flex;align-items:center;justify-content:center;background:{reaction};border:2rem solid {bg};border-radius:14rem;padding:0 5rem;font-size:13rem;line-height:17rem;z-index:1}}
.date-row {{display:flex;justify-content:center;margin:10rem 0}} .date {{color:{muted};font-size:12rem;font-weight:600}}
.quote {{display:flex;gap:6rem;background:rgba(127,127,127,.13);border-radius:8rem;padding:5rem;margin-bottom:5rem}} .qbar {{width:3rem;border-radius:3rem;background:#5d4bff;flex:none}} .qname {{font-size:11rem;font-weight:700}} .qtext {{font-size:12rem;line-height:15rem}}
.voice,.file {{display:flex;align-items:center;gap:8rem;min-width:160rem}} .vplay,.ficon {{display:grid;place-items:center}} .wave {{display:flex;align-items:center;gap:2rem;flex:1}} .wave i {{width:2rem;background:currentColor}} .vdur,.fsize {{font-size:11rem}} .fname,.ltitle {{font-size:14rem;font-weight:600}} .linkbox {{min-width:180rem}} .ldomain,.lurl {{font-size:11rem;opacity:.8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.composer {{height:60rem;flex:none;display:flex;align-items:center;gap:10rem;padding:0 9rem;background:{bg};color:{accent}}} .composer .cbtn {{display:grid;place-items:center;flex:none}} .plus {{width:23rem;height:23rem}}
.field {{height:42rem;border-radius:24rem;background:{field};display:flex;align-items:center;flex:1;min-width:0;padding:0 10rem;font-size:16rem;color:{muted}}} .field span {{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}} .field .cbtn {{color:{accent}}} .like {{margin-left:1rem}}
.nav {{height:{nav_h}rem;flex:none;background:{pal['bar']};display:flex;align-items:center;justify-content:space-around;padding:0 40rem;color:{pal['icon_muted']}}}
.nav .nv {{display:flex;align-items:center;justify-content:center;opacity:.9}}
.nav.gesture {{align-items:flex-start;padding-top:6rem}}
.nav.gesture .pill {{width:122rem;height:4rem;border-radius:4rem;background:{pal['icon']};opacity:.55}}
</style></head><body><div class="screen">
<div class="status"><div class="sb-left"><span class="clock">{esc(dlg.get('clock','9:41'))}</span>{media_html}</div><div class="sb-right"><span class="i">{bell}</span><span class="i">{wifi}</span><span class="i">{signal}</span><span class="i">{battery}</span></div></div>
<div class="header"><span class="hbtn back">{icons['back']}</span><div class="head-avatar">{avatar}</div><div class="titlebox"><div class="title">{title}</div><div class="subtitle">{esc(ui.get('subtitle','Đang hoạt động'))}</div></div><div class="actions"><span class="hbtn">{icons['phone']}</span><span class="hbtn">{icons['video']}</span><span class="hbtn">{icons['info']}</span></div></div>
<div class="chat">{rows}</div>
<div class="composer"><span class="cbtn plus">{icons['plus']}</span><span class="cbtn">{icons['camera']}</span><span class="cbtn">{icons['gallery']}</span><span class="cbtn">{icons['mic']}</span><div class="field"><span>{placeholder}</span><span class="cbtn">{icons['smile']}</span></div><span class="cbtn like">{icons['like']}</span></div>
{nav_html}</div></body></html>'''
