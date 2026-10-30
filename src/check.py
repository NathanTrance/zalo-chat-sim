#!/usr/bin/env python3
"""QA gate: every label must match what is actually rendered on screen.

    python src/check.py
    python src/check.py --manifest out/manifest.jsonl

Clipping is allowed (a chat screenshot legitimately starts mid-conversation),
but only at the top: a message that is cut must never sit below a fully
visible one, and the transcript must contain exactly the fully visible
messages, so no clipped text leaks into the label.
"""

import argparse
import html as H
import json
import re
import sys
from pathlib import Path

from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
TAG = re.compile(r"<[^>]+>")


def norm(s: str) -> str:
    return re.sub(r"\W+", "", s.lower())


def visible_text(html_path: Path) -> str:
    s = html_path.read_text(encoding="utf-8")
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = TAG.sub(" ", s)
    return re.sub(r"\s+", " ", H.unescape(s))


def label_fragments(transcript: str):
    for line in transcript.splitlines():
        line = line.strip()
        if not line:
            continue
        # bracketed parts are structural placeholders ([Hình ảnh], [Tệp], ...)
        line = re.sub(r"\[[^\]]*\]", " ", line).strip()
        if not line:
            continue
        if ": " in line:
            who, text = line.split(": ", 1)
            yield who
            yield text
        else:
            yield line


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(ROOT / "out" / "manifest.jsonl"))
    ap.add_argument("--data", default=str(ROOT / "dialogues"))
    args = ap.parse_args()

    problems = []

    # 1. schema-validate every scenario file
    try:
        import jsonschema

        schema = json.loads((ROOT / "schema" / "dialogue.schema.json").read_text(encoding="utf-8"))
        for f in sorted(Path(args.data).glob("*.json")):
            dlg = json.loads(f.read_text(encoding="utf-8"))
            for err in jsonschema.Draft7Validator(schema).iter_errors(dlg):
                problems.append(f"{f.name}: schema: {err.message} @ {list(err.absolute_path)}")

        bank = ROOT / "bank.example.jsonl"
        if bank.exists():
            for i, line in enumerate(bank.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                for err in jsonschema.Draft7Validator(schema).iter_errors(json.loads(line)):
                    problems.append(
                        f"bank.example.jsonl:{i}: schema: {err.message} @ {list(err.absolute_path)}"
                    )
    except ImportError:
        print("jsonschema not installed, skipping schema validation")

    manifest = Path(args.manifest)
    base = manifest.parent
    entries = [json.loads(l) for l in manifest.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"checking {len(entries)} rendered images")

    for e in entries:
        img_name = e.get("image") or e.get("image_jpeg") or ""
        stem = Path(img_name).stem or f"{e['id']}__{e['theme']}__{e['device']}"
        name = stem
        html_path = base / "html" / f"{stem}.html"
        images = [base / "screens" / n for n in (e.get("image"), e.get("image_jpeg")) if n]

        if not html_path.exists():
            problems.append(f"{name}: missing html")
            continue
        if not images:
            problems.append(f"{name}: no image recorded")
            continue
        missing = [p.name for p in images if not p.exists()]
        if missing:
            problems.append(f"{name}: missing image(s) {missing}")
            continue

        for img in images:
            with Image.open(img) as im:
                if im.size != (e["width_px"], e["height_px"]):
                    problems.append(f"{name}: {img.name} size {im.size} != {(e['width_px'], e['height_px'])}")

        # clipping is only legitimate at the top of the chat
        boxes = e.get("bboxes_dp") or []
        clipped = e.get("clipped_indices") or []
        visible = [b["message_index"] for b in boxes if b["fully_visible"]]
        if clipped and visible and max(clipped) > min(visible):
            problems.append(f"{name}: clipped message below visible content: {clipped}")
        if len(e["transcript"].splitlines()) != len(visible):
            problems.append(
                f"{name}: transcript has {len(e['transcript'].splitlines())} lines "
                f"but {len(visible)} messages are fully visible"
            )

        text = norm(visible_text(html_path))
        for frag in label_fragments(e["transcript"]):
            if frag and norm(frag) not in text:
                problems.append(f"{name}: label text not found in DOM: {frag[:60]!r}")

        if any(ch in e["transcript"] for ch in "ăâđêôơư") and "ă" not in text and "đ" not in text:
            problems.append(f"{name}: Vietnamese diacritics missing from DOM")

    if problems:
        print(f"\nFAIL ({len(problems)})")
        for p in problems:
            print(" -", p)
        return 1

    print("\nPASS: sizes, labels, clipping and diacritics all consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
