"""Build the static HTML for one Zalo chat screenshot."""

import html as H
import math

from . import icons
from . import theme as T

FONT_UI = '"Roboto", "Segoe UI", "Noto Sans", sans-serif'
EMOJI_UI = '"Segoe UI Emoji", "Noto Color Emoji", sans-serif'


def esc(s) -> str:
    return H.escape(str(s), quote=True)


def _initials(name: str) -> str:
    parts = [p for p in str(name).split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


_AVATAR_COLORS = [
    ("#5B7C6E", "#8FB3A1"), ("#6B5B7C", "#A894C0"), ("#7C6B4F", "#C4AE82"),
    ("#4F6B7C", "#88A9C4"), ("#7C4F4F", "#C48C8C"), ("#4F7C5B", "#8FC4A0"),
]


def _avatar_style(name: str, explicit=None) -> str:
    if explicit:
        return f"background:{esc(explicit)}"
    col = _AVATAR_COLORS[sum(name.encode()) % len(_AVATAR_COLORS)][0]
    return f"background:{col}"


def _avatar(name: str, size: float, explicit=None, text=None) -> str:
    return (
        f'<div class="av" style="{_avatar_style(name, explicit)};'
        f'width:{size}rem;height:{size}rem;font-size:{size * 0.42:.2f}rem">'
        f"{esc(text or _initials(name))}</div>"
    )


def _stamp(m: dict) -> str:
    t = m.get("time")
    if not t:
        return ""
    # Zalo stamps the last bubble of a run; media bubbles always carry a time.
    if not m.get("_last_in_run", True) and m["type"] not in ("image", "voice", "file", "link", "sticker"):
        return ""
    return f'<div class="stamp">{esc(t)}</div>'


def _reaction(m: dict, show_count: bool = True) -> str:
    r = m.get("reaction")
    if not r:
        return ""
    count = (f'<span class="rc">{esc(r.get("count", 1))}</span>'
             if show_count and r.get("count") else "")
    emoji = r.get("emoji", "\u2764\ufe0f")
    return f'<div class="reaction"><span class="re">{esc(emoji)}</span>{count}</div>'


def _quote(m: dict) -> str:
    q = m.get("quote")
    if not q:
        return ""
    return (
        f'<div class="quote"><div class="qbar"></div><div class="qbody">'
        f'<div class="qname">{esc(q.get("name", ""))}</div>'
        f'<div class="qtext">{esc(q.get("text", ""))}</div></div></div>'
    )


def _waveform(seed: str, bars: int = 22) -> str:
    base = sum(seed.encode())
    out = []
    for i in range(bars):
        v = 0.28 + 0.72 * abs(math.sin((base % 97 + i * 37) * 0.7))
        h = max(1.6, v * 17)
        out.append(f'<i style="height:{h:.1f}rem"></i>')
    return "".join(out)


def _bubble_inner(m: dict, pal: dict) -> str:
    t = m["type"]
    if t == "text":
        body = f'<div class="txt">{esc(m["text"])}</div>'
    elif t == "image":
        cap = f'<div class="txt cap">{esc(m["caption"])}</div>' if m.get("caption") else ""
        body = (
            f'<div class="photo"><img src="{esc(m["asset"])}" alt=""></div>{cap}'
        )
    elif t == "voice":
        dur = m.get("duration", 0)
        body = (
            '<div class="voice">'
            f'<div class="vplay">{icons.play(15)}</div>'
            f'<div class="wave">{_waveform(m.get("seed", str(dur)))}</div>'
            f'<div class="vdur">{dur // 60}:{dur % 60:02d}</div>'
            "</div>"
        )
    elif t == "file":
        body = (
            '<div class="file">'
            f'<div class="ficon">{icons.file_icon(21)}</div>'
            f'<div class="fmeta"><div class="fname">{esc(m.get("filename", "tep.pdf"))}</div>'
            f'<div class="fsize">{esc(m.get("size", ""))}</div></div>'
            "</div>"
        )
    elif t == "link":
        body = (
            '<div class="linkbox">'
            f'<div class="ltitle">{esc(m.get("title", ""))}</div>'
            f'<div class="ldomain">{icons.link_icon(13)}<span>{esc(m.get("domain", ""))}</span></div>'
            f'<div class="lurl">{esc(m.get("url", ""))}</div>'
            "</div>"
        )
    else:
        body = f'<div class="txt">{esc(m.get("text", ""))}</div>'

    inner = _quote(m) + body + _stamp(m)
    cls = "bubble"
    if t == "image":
        cls += " media"
    if t in ("voice", "file", "link"):
        cls += " wide"
    return f'<div class="{cls}">{inner}</div>'


def _row(m: dict, pal: dict, conv: dict, show_reaction_count: bool = True) -> str:
    t = m["type"]
    if t == "date":
        return (f'<div class="date-row" data-idx="{m.get("_idx", 0)}">'
                f'<span class="date">{esc(m["text"])}</span></div>')

    side = "out" if m.get("from") == conv.get("me") else "in"
    name = m.get("name") or _name_of(m.get("from"), conv)
    gap = " gap" if m.get("_first_in_run") else ""
    idx = m.get("_idx", 0)

    if t == "sticker":
        left = ""
        if side == "in":
            if m.get("_avatar"):
                left = _avatar(name, T.AVATAR, m.get("color"))
            else:
                left = f'<div class="av ghost" style="width:{T.AVATAR}rem;height:{T.AVATAR}rem"></div>'
        sender = ""
        if side == "in" and conv.get("kind") == "group" and m.get("_first_in_run"):
            sender = f'<div class="sender">{esc(name)}</div>'
        return (
            f'<div class="row {side}{gap}" data-idx="{idx}">{left}'
            f'<div class="stack">{sender}<div class="sticker">{esc(m.get("emoji", "\U0001F60A"))}</div>'
            f"{_stamp(m)}</div></div>"
        )

    left = ""
    if side == "in":
        if m.get("_avatar"):
            left = _avatar(name, T.AVATAR, m.get("color"))
        else:
            left = f'<div class="av ghost" style="width:{T.AVATAR}rem;height:{T.AVATAR}rem"></div>'

    sender = ""
    if side == "in" and conv.get("kind") == "group" and m.get("_first_in_run"):
        sender = f'<div class="sender">{esc(name)}</div>'

    return (
        f'<div class="row {side}{gap}" data-idx="{idx}">{left}'
        f'<div class="stack">{sender}{_bubble_inner(m, pal)}'
        f'{_reaction(m, show_reaction_count)}</div></div>'
    )


def _name_of(pid, conv):
    for p in conv.get("participants", []):
        if p["id"] == pid:
            return p["name"]
    return pid or "?"


def _annotate(messages, conv):
    """Mark first/last-in-run flags used by the layout (avatar, name, timestamp)."""
    for i, m in enumerate(messages):
        m["_idx"] = i
        m["_first_in_run"] = False
        m["_avatar"] = False
        m["_last_in_run"] = True

    prev = None
    for i, m in enumerate(messages):
        if m["type"] == "date":
            prev = None
            continue
        sender = m.get("from")
        m["_first_in_run"] = prev != sender
        m["_avatar"] = m["_first_in_run"]
        if prev is not None:
            # the previous message is not the last of its run
            messages[i - 1]["_last_in_run"] = sender != messages[i - 1].get("from")
        prev = sender
    if messages:
        messages[-1]["_last_in_run"] = True


def build_html(dlg: dict, theme_name: str, device: str, font_uri: str) -> str:
    pal = T.PALETTES[theme_name]
    dev = T.DEVICES[device]
    W, H = dev["w"], dev["h"]
    dpr = dev["dpr"]
    conv = dlg["conversation"]
    sb = dlg.get("status_bar", {})
    ui = dlg.get("ui", {})
    nav = ui.get("nav") or dev["nav"]

    messages = [dict(m) for m in dlg["messages"]]
    _annotate(messages, conv)

    rows = "\n".join(_row(m, pal, conv) for m in messages)

    media = sb.get("media")
    media_html = ""
    if media:
        media_html = (
            f'<div class="smedia">{icons.speaker(12)}<span>{esc(media)}</span></div>'
            '<i class="sdot"></i>'
        )

    wifi = icons.wifi(15) if sb.get("wifi", True) else ""
    bell = icons.bell_off(14) if sb.get("muted") else ""
    sig = icons.signal(15, sb.get("signal", 4))
    batt = icons.battery(15, sb.get("battery", 62))

    nav_h = T.NAV_GESTURE_H if nav == "gesture" else T.NAV_H
    if nav == "gesture":
        nav_html = f'<div class="nav gesture"><i class="pill"></i></div>'
    else:
        nav_html = (
            '<div class="nav">'
            f'<span class="nv">{icons.nav_recents(15)}</span>'
            f'<span class="nv">{icons.nav_home(15)}</span>'
            f'<span class="nv">{icons.nav_back(15)}</span>'
            "</div>"
        )

    fab = ""
    if ui.get("scroll_fab"):
        fab = f'<div class="fab">{icons.chevrons_down(20)}</div>'

    css = f"""
@font-face {{ font-family: "Roboto"; src: url("{font_uri}") format("truetype");
             font-weight: 100 900; font-style: normal; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ font-size: {dpr}px; }}
body {{
  width: {W}px; height: {H}px; overflow: hidden;
  font-family: {FONT_UI}; background: {pal['bar']};
  -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
}}
.screen {{ display: flex; flex-direction: column; width: 100%; height: 100%; }}

/* ---------------------------------------------------------------- status */
.status {{
  height: {T.STATUS_H}rem; flex: 0 0 auto; background: {pal['bar']};
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 12rem 0 14rem; color: {pal['status_text']};
  font-size: {T.FONT_STATUS}rem; font-weight: 600; letter-spacing: .01em;
}}
.sb-left, .sb-right {{ display: flex; align-items: center; }}
.sb-left {{ gap: 7rem; }}
.sb-right {{ gap: 7rem; }}
.clock {{ padding-top: .5rem; }}
.smedia {{
  display: inline-flex; align-items: center; gap: 4rem;
  background: #8C3B3B; color: #F7EDEA; border-radius: 10rem;
  padding: 1.5rem 8rem 1.5rem 6rem; font-size: 11rem; font-weight: 700;
  letter-spacing: .03em; margin-left: 4rem;
}}
.smedia svg {{ opacity: .95; }}
.sdot {{ width: 3.2rem; height: 3.2rem; border-radius: 50%;
        background: {pal['status_text']}; opacity: .85; }}
.sb-right .i {{ display: inline-flex; align-items: center; opacity: .95; }}

/* ---------------------------------------------------------------- header */
.header {{
  height: {T.HEADER_H}rem; flex: 0 0 auto; background: {pal['bar']};
  display: flex; align-items: center; padding: 0 8rem 0 8rem; color: {pal['icon']};
}}
.hbtn {{ display: flex; align-items: center; justify-content: center;
        width: 40rem; height: 40rem; flex: 0 0 auto; }}
.header .title {{
  flex: 1 1 auto; font-size: {T.FONT_TITLE}rem; font-weight: 600;
  margin-left: 6rem; letter-spacing: .005em; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis;
}}
.actions {{ display: flex; align-items: center; gap: 13rem; padding-right: 4rem; }}
.actions .hbtn {{ width: 30rem; height: 40rem; }}

/* ------------------------------------------------------------------ chat */
.chat {{
  flex: 1 1 auto; background: {pal['chat_bg']};
  display: flex; flex-direction: column; justify-content: flex-end;
  overflow: hidden; padding: {T.CHAT_PAD_TOP}rem {T.CHAT_PAD_X}rem {T.CHAT_PAD_BOTTOM}rem;
}}
.row {{ display: flex; align-items: flex-end; margin-top: {T.MSG_GAP_RUN}rem; }}
.row.gap {{ margin-top: {T.MSG_GAP_GROUP}rem; }}
.row.out {{ justify-content: flex-end; }}
.row .av {{
  flex: 0 0 auto; border-radius: 50%; margin-right: {T.AVATAR_GAP}rem;
  display: flex; align-items: center; justify-content: center;
  color: #E8EDEA; font-weight: 600; letter-spacing: .02em;
  text-transform: uppercase; user-select: none;
}}
.row .av.ghost {{ background: transparent; }}
.stack {{ position: relative; max-width: {T.BUBBLE_MAX_W}%; }}
.sender {{
  font-size: {T.FONT_NAME}rem; font-weight: 500; color: {pal['sender']};
  margin: 0 0 3rem 2rem;
}}
.bubble {{
  background: {pal['incoming']}; color: {pal['text']};
  padding: {T.BUBBLE_PAD_Y}rem {T.BUBBLE_PAD_X}rem;
  border-radius: {T.BUBBLE_RADIUS}rem {T.BUBBLE_RADIUS}rem {T.BUBBLE_RADIUS}rem {T.BUBBLE_TAIL_RADIUS}rem;
  font-size: {T.FONT_TEXT}rem; line-height: {T.FONT_TEXT_LH}rem;
  word-break: break-word; overflow-wrap: anywhere;
}}
.out .bubble {{
  background: {pal['outgoing']};
  border-radius: {T.BUBBLE_RADIUS}rem {T.BUBBLE_RADIUS}rem {T.BUBBLE_TAIL_RADIUS}rem {T.BUBBLE_RADIUS}rem;
}}
.txt {{ white-space: pre-wrap; }}
.stamp {{
  font-size: {T.FONT_TIME}rem; line-height: 1.45; color: {pal['time']};
  margin-top: 1.5rem; font-variant-numeric: tabular-nums;
}}
.bubble .cap {{ margin-top: 5rem; }}
.bubble.media {{ padding: 3rem 3rem 5rem 3rem; }}
.photo img {{
  display: block; width: 100%; max-width: 232rem; max-height: 158rem;
  border-radius: 8rem; object-fit: cover;
}}
.sticker {{ font-family: {EMOJI_UI}; font-size: 74rem; line-height: 1.1; }}

.voice {{ display: flex; align-items: center; gap: 9rem; min-width: 190rem; }}
.vplay {{
  width: 30rem; height: 30rem; border-radius: 50%; flex: 0 0 auto;
  background: {pal['icon']}; color: {pal['chat_bg']};
  display: flex; align-items: center; justify-content: center; padding-left: 1rem;
}}
.wave {{ display: flex; align-items: center; gap: 2.2rem; flex: 1 1 auto; height: 20rem; }}
.wave i {{ width: 2.4rem; border-radius: 2rem; background: currentColor; opacity: .55; }}
.vdur {{ font-size: 11.5rem; color: {pal['time']}; font-variant-numeric: tabular-nums; }}

.file {{ display: flex; align-items: center; gap: 9rem; min-width: 170rem; }}
.ficon {{
  width: 38rem; height: 38rem; border-radius: 9rem; flex: 0 0 auto;
  background: rgba(127,127,127,.18); display: flex; align-items: center;
  justify-content: center; color: {pal['icon']};
}}
.fname {{ font-size: 14rem; font-weight: 500; }}
.fsize {{ font-size: 11.5rem; color: {pal['time']}; margin-top: 1.5rem; }}

.linkbox {{ min-width: 190rem; }}
.ltitle {{ font-size: 14rem; font-weight: 500; line-height: 18rem; }}
.ldomain {{ display: flex; align-items: center; gap: 3rem; font-size: 11rem;
           color: {pal['time']}; margin-top: 4rem; }}
.lurl {{ font-size: 11rem; color: {pal['accent']}; margin-top: 2rem;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 210rem; }}

.quote {{
  display: flex; gap: 7rem; background: {pal['quote_bg']};
  border-radius: 7rem; padding: 5rem 8rem; margin-bottom: 5rem; max-width: 100%;
}}
.qbar {{ width: 2.4rem; border-radius: 2rem; background: {pal['quote_bar']}; flex: 0 0 auto; }}
.qname {{ font-size: 11.5rem; font-weight: 600; color: {pal['sender']}; }}
.qtext {{ font-size: 12rem; line-height: 16rem; color: {pal['text_muted']};
         display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
         overflow: hidden; }}

.reaction {{
  position: absolute; right: -5rem; bottom: -9rem; z-index: 2;
  display: flex; align-items: center; gap: 3rem;
  background: {pal['reaction_bg']}; border: 2rem solid {pal['reaction_border']};
  border-radius: 12rem; padding: 1rem 6rem 1rem 4rem; height: 22rem;
  font-family: {EMOJI_UI}; font-size: 11rem; color: {pal['text']};
}}
.reaction .rc {{ font-family: {FONT_UI}; font-size: 11rem; font-weight: 500; }}
.out .reaction {{ right: 2rem; }}

.date-row {{ display: flex; justify-content: center; margin: 13rem 0 9rem; }}
.date {{
  background: {pal['chip_bg']}; color: {pal['chip_text']};
  font-size: {T.FONT_CHIP}rem; padding: 2.5rem 10rem; border-radius: 12rem;
  font-variant-numeric: tabular-nums;
}}

/* -------------------------------------------------------------- composer */
.composer {{
  height: {T.COMPOSER_H}rem; flex: 0 0 auto; background: {pal['bar']};
  display: flex; align-items: center; gap: 6rem; padding: 0 12rem 0 14rem;
  color: {pal['icon_muted']}; position: relative;
}}
.composer .cbtn {{ display: flex; align-items: center; justify-content: center;
                  width: 38rem; height: 40rem; flex: 0 0 auto; }}
.field {{
  flex: 1 1 auto; font-size: 16rem; color: {pal['input_text']};
  padding: 0 4rem; white-space: nowrap; overflow: hidden;
}}
.field.hint-active {{ color: {pal['time']}; }}
.gallery {{
  width: 36rem; height: 36rem; border-radius: 10rem; flex: 0 0 auto;
  background: linear-gradient(150deg, {pal['gallery_a']}, {pal['gallery_b']});
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 1rem 3rem rgba(0,0,0,.18);
}}
.fab {{
  position: absolute; right: 14rem; top: -22rem;
  width: 42rem; height: 42rem; border-radius: 50%;
  background: {pal['fab_bg']}; color: {pal['icon']};
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2rem 8rem rgba(0,0,0,.28);
}}

/* ------------------------------------------------------------------- nav */
.nav {{
  height: {nav_h}rem; flex: 0 0 auto; background: {pal['bar']};
  display: flex; align-items: center; justify-content: space-around;
  padding: 0 40rem; color: {pal['icon_muted']};
}}
.nav .nv {{ display: flex; align-items: center; justify-content: center; opacity: .9; }}
.nav.gesture {{ align-items: flex-start; padding-top: 6rem; }}
.nav.gesture .pill {{
  width: 122rem; height: 4rem; border-radius: 4rem;
  background: {pal['icon']}; opacity: .55;
}}
"""

    return f"""<!doctype html>
<html lang="vi">
<head><meta charset="utf-8"><title>{esc(dlg.get('id','zalo'))}</title>
<style>{css}</style></head>
<body><div class="screen">
  <div class="status">
    <div class="sb-left"><span class="clock">{esc(dlg.get('clock','9:41'))}</span>{media_html}</div>
    <div class="sb-right"><span class="i">{bell}</span><span class="i">{wifi}</span>
      <span class="i">{sig}</span><span class="i">{batt}</span></div>
  </div>
  <div class="header">
    <span class="hbtn">{icons.back(24)}</span>
    <div class="title">{esc(conv.get('title',''))}</div>
    <div class="actions">
      <span class="hbtn">{icons.phone(22)}</span>
      <span class="hbtn">{icons.video(24)}</span>
      <span class="hbtn">{icons.menu(22)}</span>
    </div>
  </div>
  <div class="chat">
    {rows}
  </div>
  <div class="composer">
    {fab}
    <span class="cbtn">{icons.smile(26)}</span>
    <div class="field">{esc(ui.get('placeholder','Tin nhắn'))}</div>
    <span class="cbtn">{icons.more(23)}</span>
    <span class="cbtn">{icons.mic(24)}</span>
    <span class="gallery">{icons.gallery(21)}</span>
  </div>
  {nav_html}
</div></body></html>
"""
