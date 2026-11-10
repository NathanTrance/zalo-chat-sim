"""Design tokens for the Zalo Android chat screen.

All values are in **dp** (density-independent pixels) unless stated otherwise.
The renderer multiplies them by the device DPR via CSS `rem` (1rem == 1dp).

Metrics and colours were sampled from `images/zalo_1.jfif`
(928x2010 px @ 2.25x = 412x893 dp, dark theme).
"""

# --------------------------------------------------------------------- band ---
STATUS_H = 28.0
HEADER_H = 54.0
COMPOSER_H = 98.0
NAV_H = 64.0          # 3-button navigation
NAV_GESTURE_H = 24.0  # gesture bar

# ------------------------------------------------------------------ bubble ---
CHAT_PAD_X = 12.0
CHAT_PAD_TOP = 10.0
CHAT_PAD_BOTTOM = 8.0
AVATAR = 26.0
AVATAR_GAP = 11.0
BUBBLE_MAX_W = 71.0   # percent of the chat content width
BUBBLE_PAD_Y = 8.0
BUBBLE_PAD_X = 12.0
BUBBLE_RADIUS = 11.0
BUBBLE_TAIL_RADIUS = 3.0
MSG_GAP_RUN = 3.0     # consecutive messages from the same sender
MSG_GAP_GROUP = 10.0  # between sender runs

# -------------------------------------------------------------------- fonts ---
FONT_TEXT = 15.0
FONT_TEXT_LH = 21.0
FONT_TIME = 11.5
FONT_NAME = 12.5
FONT_TITLE = 18.0
FONT_STATUS = 14.0
FONT_CHIP = 12.0

# ------------------------------------------------------------------ palette ---
PALETTES = {
    "dark": {
        "bar": "#242424",
        "chat_bg": "#111111",
        "incoming": "#2C2C2C",
        "outgoing": "#3B4755",
        "text": "#E9EAEB",
        "text_muted": "#9AA0A6",
        "time": "#9AA0A6",
        "chip_bg": "#262626",
        "chip_text": "#A6ABB2",
        "icon": "#E9EAEB",
        "icon_muted": "#C2C7CC",
        "input_text": "#8A8F96",
        "status_text": "#F2F3F4",
        "battery": "#F2F3F4",
        "reaction_bg": "#2E3237",
        "reaction_border": "#111111",
        "sender": "#8FB3D9",
        "divider": "#2C2C2C",
        "quote_bg": "#262A2F",
        "quote_bar": "#5A7CA8",
        "gallery_a": "#F6A21E",
        "gallery_b": "#EE5A24",
        "fab_bg": "#2A2A2A",
        "accent": "#0068FF",
    },
    "light": {
        "bar": "#FFFFFF",
        "chat_bg": "#E8ECF2",
        "incoming": "#FFFFFF",
        "outgoing": "#D2E7FF",
        "text": "#111417",
        "text_muted": "#7C838C",
        "time": "#8A9098",
        "chip_bg": "#DDE2E9",
        "chip_text": "#5D646D",
        "icon": "#1A1D21",
        "icon_muted": "#3C4249",
        "input_text": "#8A9098",
        "status_text": "#111417",
        "battery": "#111417",
        "reaction_bg": "#FFFFFF",
        "reaction_border": "#E8ECF2",
        "sender": "#3A6EA5",
        "divider": "#DCE1E8",
        "quote_bg": "#EEF2F7",
        "quote_bar": "#7FA8D4",
        "gallery_a": "#F6A21E",
        "gallery_b": "#EE5A24",
        "fab_bg": "#FFFFFF",
        "accent": "#0068FF",
    },
}

# (width_px, height_px, dpr) -- the dp canvas is derived from these.
DEVICES = {
    # 1440x3200 @3.5 -> 411.4 x 914.3 dp (Galaxy S20 Ultra class panel)
    "screen_1440x3200": {"w": 1440, "h": 3200, "dpr": 3.5, "nav": "3button"},
    "reference_928": {"w": 928, "h": 2010, "dpr": 2.25, "nav": "3button"},
    "pixel_7": {"w": 1080, "h": 2400, "dpr": 2.625, "nav": "gesture"},
    "galaxy_a54": {"w": 1080, "h": 2340, "dpr": 2.8125, "nav": "3button"},
    "budget_720": {"w": 720, "h": 1600, "dpr": 2.0, "nav": "3button"},
    # Pixel 10 Messenger captures in out/pixel10: 1280x2856, ~428x952 dp.
    "pixel_10": {"w": 1280, "h": 2856, "dpr": 3.0, "nav": "gesture"},
}


def dp_canvas(device: str):
    d = DEVICES[device]
    return d["w"] / d["dpr"], d["h"] / d["dpr"]
