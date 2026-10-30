"""Inline SVG icons (stroke-based, sized in dp via `rem`)."""

from .theme import dp_canvas  # noqa: F401  (kept for symmetry / future use)


def _svg(body: str, size: float, vb: int = 24, extra: str = "") -> str:
    return (
        f'<svg width="{size}rem" height="{size}rem" viewBox="0 0 {vb} {vb}" '
        f'fill="none" stroke="currentColor" stroke-width="1.7" '
        f'stroke-linecap="round" stroke-linejoin="round" {extra}>{body}</svg>'
    )


def back(size=24):
    return _svg('<path d="M15 4.5 7.5 12 15 19.5"/>', size)


def phone(size=23):
    return _svg(
        '<path d="M6.2 3.6h2.3l1.5 3.7-1.9 1.4a13.2 13.2 0 0 0 6.2 6.2l1.4-1.9 3.7 1.5v2.3c0 .9-.7 1.6-1.6 1.6A16.1 16.1 0 0 1 4.6 5.2c0-.9.7-1.6 1.6-1.6z"/>',
        size,
    )


def video(size=25):
    return _svg(
        '<rect x="2.6" y="6.2" width="12.4" height="11.6" rx="2.6"/>'
        '<path d="M15 10.8 21 7.6v8.8l-6-3.2z"/>',
        size,
    )


def menu(size=23):
    dots = '<circle cx="20.2" cy="7" r="1.15" fill="currentColor" stroke="none"/>' \
           '<circle cx="20.2" cy="12" r="1.15" fill="currentColor" stroke="none"/>' \
           '<circle cx="20.2" cy="17" r="1.15" fill="currentColor" stroke="none"/>'
    return _svg('<path d="M3.5 7h13M3.5 12h13M3.5 17h13"/>' + dots, size)


def smile(size=26):
    return _svg(
        '<circle cx="12" cy="12" r="8.9"/>'
        '<circle cx="9.1" cy="10.1" r="1.05" fill="currentColor" stroke="none"/>'
        '<circle cx="14.9" cy="10.1" r="1.05" fill="currentColor" stroke="none"/>'
        '<path d="M8.4 14.1c.9 1.5 2.1 2.2 3.6 2.2s2.7-.7 3.6-2.2"/>',
        size,
    )


def more(size=24):
    return _svg(
        '<circle cx="5" cy="12" r="1.35" fill="currentColor" stroke="none"/>'
        '<circle cx="12" cy="12" r="1.35" fill="currentColor" stroke="none"/>'
        '<circle cx="19" cy="12" r="1.35" fill="currentColor" stroke="none"/>',
        size,
    )


def mic(size=25):
    return _svg(
        '<rect x="9.2" y="2.8" width="5.6" height="10.4" rx="2.8"/>'
        '<path d="M5.8 11.4a6.2 6.2 0 0 0 12.4 0M12 17.6v3.4"/>',
        size,
    )


def gallery(size=21):
    return (
        f'<svg width="{size}rem" height="{size}rem" viewBox="0 0 24 24" fill="none" '
        'stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="3.2" y="4.4" width="17.6" height="15.2" rx="3.2"/>'
        '<circle cx="9" cy="10" r="1.9"/>'
        '<path d="M3.6 16.4 9.6 11l5.4 5.4 2.8-2.6 2.7 2.6"/>'
        "</svg>"
    )


def play(size=14, filled=True):
    fill = "currentColor" if filled else "none"
    return (
        f'<svg width="{size}rem" height="{size}rem" viewBox="0 0 24 24" fill="{fill}" '
        'stroke="none"><path d="M7.5 4.6 19.6 12 7.5 19.4z"/></svg>'
    )


def file_icon(size=22):
    return _svg(
        '<path d="M13.4 2.8H6.6a2 2 0 0 0-2 2v14.4a2 2 0 0 0 2 2h10.8a2 2 0 0 0 2-2V8.8z"/>'
        '<path d="M13.4 2.8v6h6"/>',
        size,
    )


def link_icon(size=20):
    return _svg(
        '<path d="M10.2 13.8a4.2 4.2 0 0 0 6 0l2.3-2.3a4.2 4.2 0 0 0-6-6l-1.3 1.3"/>'
        '<path d="M13.8 10.2a4.2 4.2 0 0 0-6 0l-2.3 2.3a4.2 4.2 0 0 0 6 6l1.3-1.3"/>',
        size,
    )


def heart_outline(size=15):
    return _svg(
        '<path d="M12 20.1S3.9 15.2 3.9 9.6a4.4 4.4 0 0 1 8.1-2.4 4.4 4.4 0 0 1 8.1 2.4c0 5.6-8.1 10.5-8.1 10.5z"/>',
        size,
    )


def chevrons_down(size=22):
    return _svg('<path d="M6.5 9.5 12 15l5.5-5.5M6.5 14.5 12 20l5.5-5.5"/>', size)


# --------------------------------------------------------------- status bar ---
def wifi(size=15):
    return _svg(
        '<path d="M2.4 8.4a14 14 0 0 1 19.2 0M5.9 11.9a9 9 0 0 1 12.2 0M9.4 15.4a4 4 0 0 1 5.2 0"/>'
        '<circle cx="12" cy="18.9" r="1.15" fill="currentColor" stroke="none"/>',
        size,
    )


def signal(size=15, bars=4):
    out = []
    for i in range(4):
        h = 3.4 + i * 3.1
        y = 19.6 - h
        fill = "currentColor" if i < bars else "none"
        op = "1" if i < bars else "0.45"
        out.append(
            f'<rect x="{2.4 + i * 4.4}" y="{y}" width="2.9" height="{h}" rx="0.9" '
            f'fill="{fill}" stroke="none" opacity="{op}"/>'
        )
    return (
        f'<svg width="{size}rem" height="{size}rem" viewBox="0 0 20 21" fill="none">'
        + "".join(out)
        + "</svg>"
    )


def battery(size=15, pct=43):
    w = 31.0
    return (
        f'<svg width="{w * size / 21:.2f}rem" height="{size}rem" viewBox="0 0 31 21" fill="none">'
        '<rect x="1" y="3.1" width="26.4" height="14.8" rx="4.4" stroke="currentColor" '
        'stroke-width="1.5" stroke-opacity="0.85"/>'
        f'<text x="13.6" y="14.4" font-family="Roboto" font-size="10.2" font-weight="600" '
        f'text-anchor="middle" fill="currentColor">{pct}</text>'
        '<path d="M28.6 8.2v4.6a2.9 2.9 0 0 0 0-4.6z" fill="currentColor" fill-opacity="0.75"/>'
        "</svg>"
    )


def bell_off(size=14):
    return _svg(
        '<path d="M17.4 10.9V8.8a5.4 5.4 0 0 0-8.3-4.5M6.4 7.6a5.4 5.4 0 0 0 1.2 8.1L5.9 18h12.2"/>'
        '<path d="M10 20.4a2.4 2.4 0 0 0 4 0M3.4 3.4l17.2 17.2"/>',
        size,
    )


def speaker(size=13):
    return _svg(
        '<path d="M4 9.4h3.1L11.6 5v14l-4.5-4.4H4z"/>'
        '<path d="M15 8.6a4.8 4.8 0 0 1 0 6.8M17.8 6a8.5 8.5 0 0 1 0 12"/>',
        size,
    )


# ---------------------------------------------------------------- nav icons ---
def nav_recents(size=16):
    return (
        f'<svg width="{size}rem" height="{size}rem" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2.2" stroke-linecap="round">'
        '<path d="M6 5v14M12 5v14M18 5v14"/></svg>'
    )


def nav_home(size=16):
    return (
        f'<svg width="{size}rem" height="{size}rem" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" ><circle cx="12" cy="12" r="7.4"/></svg>'
    )


def nav_back(size=16):
    return (
        f'<svg width="{size}rem" height="{size}rem" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
        'stroke-linejoin="round"><path d="M15.5 4.8 8 12l7.5 7.2"/></svg>'
    )
