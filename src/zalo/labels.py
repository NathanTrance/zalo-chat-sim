"""Derive ground-truth labels from the same JSON that produced the pixels."""


def name_of(pid, conv) -> str:
    for p in conv.get("participants", []):
        if p.get("id") == pid:
            return p.get("name", pid)
    if pid == conv.get("me"):
        return "Tôi"
    return str(pid or "")


def _line(m: dict, conv: dict) -> str:
    who = name_of(m.get("from"), conv)
    # Only incoming messages in a group chat show the sender's name on screen.
    show_name = conv.get("kind") == "group" and m.get("from") != conv.get("me")
    prefix = f"{who}: " if show_name else ""
    t = m["type"]
    if t == "date":
        return f"[{m['text']}]"
    if t == "text":
        return f"{prefix}{m['text']}"
    if t == "image":
        cap = f" {m['caption']}" if m.get("caption") else ""
        return f"{prefix}[Hình ảnh]{cap}"
    if t == "sticker":
        return f"{prefix}[Nhãn dán]"
    if t == "voice":
        d = int(m.get("duration", 0))
        return f"{prefix}[Tin nhắn thoại {d // 60}:{d % 60:02d}]"
    if t == "file":
        return f"{prefix}[Tệp] {m.get('filename', '')} {m.get('size', '')}".strip()
    if t == "link":
        return f"{prefix}[Liên kết] {m.get('title', '')} {m.get('domain', '')}".strip()
    return f"{prefix}{m.get('text', '')}"


def transcript(dlg: dict, visible=None) -> str:
    conv = dlg["conversation"]
    lines = []
    for i, m in enumerate(dlg["messages"]):
        if visible is not None and i not in visible:
            continue
        lines.append(_line(m, conv))
    return "\n".join(lines)


def scenario_text(dlg: dict, lang: str = "en") -> str:
    sc = dlg.get("scenario", {})
    key = f"summary_{lang}"
    if sc.get(key):
        return sc[key]
    conv = dlg["conversation"]
    people = ", ".join(p["name"] for p in conv.get("participants", []))
    topic = sc.get("topic", "trao đổi chung")
    bits = [f"{people} trao đổi về {topic}."] if lang == "vi" else \
           [f"{people} discuss {topic}."]
    for d in sc.get("decisions", []):
        bits.append(f"Quyết định: {d}." if lang == "vi" else f"Decision: {d}.")
    for a in sc.get("action_items", []):
        bits.append(f"Việc cần làm: {a}." if lang == "vi" else f"Action item: {a}.")
    return " ".join(bits)


def labels(dlg: dict, theme: str, device: str, visible=None) -> dict:
    msgs = dlg["messages"]
    if visible is not None:
        kept = [m for i, m in enumerate(msgs) if i in visible]
    else:
        kept = msgs
    return {
        "id": dlg["id"],
        "theme": theme,
        "device": device,
        "conversation": {
            "kind": dlg["conversation"].get("kind"),
            "title": dlg["conversation"].get("title"),
            "participants": [p["name"] for p in dlg["conversation"].get("participants", [])],
        },
        "transcript": transcript(dlg, visible),
        "summary_en": scenario_text(dlg, "en"),
        "summary_vi": scenario_text(dlg, "vi"),
        "message_types": [m["type"] for m in kept],
        "message_count": sum(1 for m in kept if m["type"] != "date"),
    }
