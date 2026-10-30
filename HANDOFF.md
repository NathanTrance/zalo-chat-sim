# HANDOFF — Zalo chat screenshot simulator

> **Audience:** the next agent session, running on a different machine with an
> OpenAI-compatible endpoint (e.g. Qwen3-235B). Your job is to **generate a large
> Vietnamese dialogue bank and render the screenshot dataset** from this folder.
> Everything below is already built and tested; do not redesign the renderer.

Working directory for all commands: the repository root (the folder with
`src/`, `dialogues/`, `schema/`).

---

## 0. TL;DR

```bash
git clone https://github.com/NathanTrance/zalo-chat-sim.git && cd zalo-chat-sim
pip install -r requirements.txt
python -m playwright install chromium        # once per machine

# smoke test: 3 example dialogues -> 3 JPEGs
python src/generate.py --input bank.example.jsonl --out out/smoke \
  --themes dark --devices screen_1440x3200 --formats jpg --workers 4
python src/check.py --manifest out/smoke/manifest.jsonl
```

Expected: 1440×3200 JPEGs in `out/smoke/screens/`, QA prints `PASS`.

---

## 1. What is already done

| Path | What it is |
|---|---|
| `src/generate.py` | **main entry point** (single JSON / folder / JSONL bank, workers, shards, windows) |
| `src/zalo/` | renderer: theme tokens, SVG icons, HTML builder, label derivation, Playwright driver |
| `src/check.py` | QA gate (schema, pixel size, clipping, transcript↔DOM) |
| `src/to_jsonl.py` | pack per-file dialogues into a bank |
| `src/contact_sheet.py`, `src/compare_reference.py` | review helpers |
| `dialogues/*.json` | 8 hand-written Vietnamese scenarios |
| `bank.example.jsonl` | 3 example bank lines (short direct, group with media, 40-message thread) |
| `schema/dialogue.schema.json` | the contract |
| `assets/fonts/Roboto.ttf` | bundled (Apache 2.0) — no network needed at render time |
| `assets/photos/` | 4 generated photo assets used by `image` messages |
| `docs/` | sample contact sheets + reference comparison |
| `out/` | **generated, gitignored** |

Status at handoff: 8 dialogues × dark/light = 16 shots at 1440×3200, `check.py` PASS.
Baseline commit: `6208c3c` (check `git log -1` for the exact hash).

---

## 2. The dialogue contract

One dialogue = one JSON object. A bank = one such object **per line** (`.jsonl`).

```json
{
  "id": "zalo_shop_0042",
  "clock": "17:38",
  "status_bar": {"battery": 43, "signal": 4, "wifi": true, "muted": false, "media": null},
  "ui": {"nav": "3button", "placeholder": "Tin nhắn", "scroll_fab": false},
  "conversation": {
    "kind": "direct",
    "title": "An",
    "me": "minh",
    "participants": [{"id": "minh", "name": "Minh"}, {"id": "an", "name": "An"}]
  },
  "messages": [
    {"type": "text", "from": "an", "text": "em gửi bảng rồi ạ", "time": "13:43"},
    {"type": "date", "text": "15:10 14/10/2026"},
    {"type": "image", "from": "an", "asset": "assets/photos/doc_scan.jpg",
     "caption": "bảng kết quả", "time": "15:12"},
    {"type": "voice", "from": "an", "duration": 14, "time": "15:14"},
    {"type": "text", "from": "minh", "text": "oke nhé", "time": "15:15",
     "reaction": {"emoji": "❤️", "count": 1}}
  ],
  "scenario": {"topic": "...", "summary_en": "...", "summary_vi": "..."}
}
```

Hard requirements (enforced by `check.py`):

- `id` unique, `^[a-z0-9_]+$`
- `conversation.kind` = `direct` or `group`; `me` must be a participant id
- every non-`date` message has `from` (a participant id)
- message `type` ∈ `text`, `date`, `image`, `sticker`, `voice`, `file`, `link`
- `asset` (if present) must exist relative to `simulation/`
- **length:** 10–25 messages for bulk. Shorter chats leave empty space at the top;
  the renderer only fills the screen from ~8 well-filled messages upward.
- **variety per dialogue:** at least one date chip, 1–3 media messages
  (image/voice/file/link/sticker), one reaction, mixed message lengths
  (1 line, 3+ lines), Vietnamese with full diacritics and natural code-switching
  (English tech terms are normal).
- **never** put real people's personal data in `text` — invent names, use
  `0900 000 000`-style phone numbers.

Message options: `reaction {emoji, count}`, `quote {name, text}`.

---

## 3. Running the renderer

```bash
# one dialogue -> 2 images (dark + light)
python src/generate.py --input dialogues/01_work_ml.json --out out/one

# one image, exactly the settings we ship
python src/generate.py --input dialogues/01_work_ml.json \
  --themes dark --devices screen_1440x3200 --out out/one

# a folder
python src/generate.py --input dialogues --out out/set --formats jpg --workers 4

# a bank + N scroll positions per dialogue
python src/generate.py --input bank.jsonl --out out/bank \
  --themes dark,light --devices screen_1440x3200 \
  --windows 3 --formats jpg --workers 4
```

Key flags:

| flag | default | notes |
|---|---|---|
| `--input`, `--data` | `dialogues` | file, folder, `.jsonl`; repeatable |
| `--devices` | `screen_1440x3200` | also `reference_928`, `pixel_7`, `galaxy_a54`, `budget_720` |
| `--themes` | `dark,light` | |
| `--windows` | `1` | scroll positions per dialogue: 1/3, 2/3, end |
| `--formats` | `jpg,json` | use `jpg` for bulk, `png,jpg,json` for masters |
| `--workers` | `1` | **use ~cores/2**; 8 workers was slower than 4 on 8 vCPU |
| `--shard i/n` | `0/1` | round-robin over tasks, for multi-machine runs |
| `--limit` | `0` | max images, for smoke runs |
| `--only` | — | comma-separated id substrings |

Output naming: `<id>__<theme>__<device>__w<window>.jpg`.

Measured (8 vCPU, 1440×3200, JPEG): **~2.7 img/s at 4 workers**, ~0.5 img/s at 1.
Disk: **~285 KB per JPEG** → 50k images ≈ **14 GB**.

---

## 4. Your task

### 4.1 Generate the dialogue bank

Target: **3,000–8,000 dialogues**, then multiply with `--windows 3 --themes dark,light`
(≈6–16 images per dialogue).

Write a generator (e.g. `tools/gen_bank.py`, not shipped yet) that:

1. calls the OpenAI-compatible endpoint once **per dialogue** (JSON object, not JSONL —
   easier to parse/retry);
2. validates the object against `schema/dialogue.schema.json`
   (`jsonschema` is installed) and checks the requirements in §2;
3. appends the compact JSON to `bank.jsonl`, skipping duplicate ids;
4. logs failures and retries up to 3× with a different temperature.

Skeleton:

```python
import os, json, random, jsonschema
from openai import OpenAI

client = OpenAI(base_url=os.environ["OPENAI_BASE_URL"],
                api_key=os.environ["OPENAI_API_KEY"])
MODEL = os.environ.get("MODEL", "qwen3-235b")
schema = json.load(open("schema/dialogue.schema.json"))

def make_one(seed_topic: str) -> dict:
    r = client.chat.completions.create(
        model=MODEL, temperature=0.95, max_tokens=3000,
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": f"Chủ đề: {seed_topic}. Trả về đúng 1 JSON."}],
    )
    d = json.loads(r.choices[0].message.content)
    jsonschema.validate(d, schema)
    return d
```

Prompt the model to answer with **only the JSON object** (no markdown fence).
If the endpoint returns a fence, strip ```json … ``` before parsing.

Topics to cycle (Vietnamese, everyday + work):
gia đình, bạn bè, lớp học/nhóm đồ án, giao hàng, đặt lịch khám, hoá đơn/tiền nhà,
sự cố production, du lịch, mua bán online, tuyển dụng, ngân hàng, bảo hiểm,
thuê trọ, sửa xe, đặt món ăn, hẹn hò, clb thể thao, phụ huynh–giáo viên,
khách hàng–shop, sếp–nhân viên, đồng nghiệp bàn giao ca.

Also vary: `direct` vs `group` (mirror with 3–6 participants), `nav` 3button/gesture,
battery 5–100, `media` chips (`NST VIET`, `Spotify`, `Zalo`, null).

### 4.2 Smoke test before the big run

```bash
python src/generate.py --input bank.jsonl --out out/smoke \
  --themes dark --windows 1 --formats jpg --workers 4 --limit 24
python src/check.py --manifest out/smoke/manifest.jsonl
python src/contact_sheet.py --manifest out/smoke/manifest.jsonl --theme dark
```

Open the contact sheet and reject the bank if you see: truncated bubbles with no
context, empty top half, overlapping reactions, mojibake, or a summary that does
not match the visible messages.

### 4.3 Full run

```bash
python src/generate.py --input bank.jsonl --out out/bank \
  --themes dark,light --devices screen_1440x3200 \
  --windows 3 --formats jpg --workers 4
```

Multi-machine: `--shard 0/5 … 4/5`, each with its own `--out`, then merge
manifests (`cat out/bank*/manifest.jsonl > all.jsonl`).

### 4.4 Labels (later, not this step)

Every manifest row has `"label_source": "synthetic"` and:

| field | meaning |
|---|---|
| `transcript` | text of the fully visible messages (hint) |
| `summary_en`, `summary_vi` | scenario summary (hint — may mention messages just above the cut) |
| `window` | `{index, start, end, total}` message slice on screen |
| `bboxes_dp` | bubble boxes in dp + `visible_ratio` |
| `clipped_indices` | messages cut by the top edge (≤ 1) |

Plan: send each JPEG to a strong VLM with these prompts (worded so train == eval),
and keep the manifest as the join key. The synthetic transcript is a **prior**,
not ground truth: the top message is cut on purpose.

- transcript: *"Transcribe every message in this chat screenshot exactly as
  written, in the original language. Keep the sender names and the order of the
  messages. Output only the transcript, with no commentary or explanation."*
- summary: *"This is a screenshot of a chat conversation. Summarize it: identify
  who is talking, the main topic, and any decisions, requests, or action items.
  Answer in English in a few sentences. Keep proper names as they appear."*

---

## 5. Gotchas

- Playwright must run the full Chromium build: the renderer uses
  `chromium.launch(channel="chromium")`. If it fails, run
  `python -m playwright install chromium`.
- The repo root `.gitignore` ignores `data/`. Put scenario files in `dialogues/`
  or `bank.jsonl`, not `data/`.
- `out/` is gitignored — never commit rendered images (14 GB at 50k).
- The renderer picks the visible **window** automatically and bottom-anchors it;
  the top message is cut by design. Do not "fix" it by trimming dialogues.
- One page is reused per worker; do not add `page.close()` back into `render()`.
- Fonts are bundled; no network is used during rendering.
- Windows and Linux both work; only `channel="chromium"` and the bundled font
  path matter.
- `src/compare_reference.py` expects `../images/zalo_1.jfif`; that real
  screenshot is not part of this repo, so skip the comparison unless you have it.

---

## 6. Definition of done

- [ ] `bank.jsonl` validates (`src/to_jsonl.py` skip-report is empty)
- [ ] 24-image smoke run renders and `check.py` passes
- [ ] contact sheet reviewed, no layout regressions
- [ ] full run completed, manifest merged, image count matches
- [ ] `manifest.jsonl` + `bank.jsonl` archived alongside the images
- [ ] notes on throughput and any failures appended to this file
