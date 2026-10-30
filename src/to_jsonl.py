#!/usr/bin/env python3
"""Pack per-file dialogue JSONs into a one-dialogue-per-line JSONL bank.

    python src/to_jsonl.py dialogues -o bank.jsonl
    python src/to_jsonl.py a.json b.json more/ -o bank.jsonl
    python src/to_jsonl.py bank.jsonl -o merged.jsonl     # merge existing banks

Each output line is a complete scenario object (the same shape as one
dialogues/*.json file), which is what `generate.py --input bank.jsonl` reads.
Compact separators are used so a line stays a line.
"""

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def iter_records(inputs):
    for p in inputs:
        p = Path(p)
        if not p.exists():
            raise SystemExit(f"input not found: {p}")
        if p.is_dir():
            files = sorted(p.rglob("*.json"))
            for f in files:
                yield json.loads(f.read_text(encoding="utf-8")), f
        elif p.suffix.lower() == ".jsonl":
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    yield json.loads(line), p
        else:
            yield json.loads(p.read_text(encoding="utf-8")), p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="json files, jsonl files or folders")
    ap.add_argument("-o", "--out", default="bank.jsonl")
    ap.add_argument("--pretty", action="store_true", help="keep spaces in the JSON (bigger file)")
    args = ap.parse_args()

    seen = set()
    written = 0
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for rec, src in iter_records(args.inputs):
            did = rec.get("id")
            if not did:
                print(f"[skip] {src}: no id", file=sys.stderr)
                continue
            if did in seen:
                print(f"[skip] {src}: duplicate id {did}", file=sys.stderr)
                continue
            if not rec.get("messages"):
                print(f"[skip] {src}: no messages", file=sys.stderr)
                continue
            seen.add(did)
            sep = (", ", ": ") if args.pretty else (",", ":")
            fh.write(json.dumps(rec, ensure_ascii=False, separators=sep) + "\n")
            written += 1

    print(f"{written} dialogues -> {out} ({out.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
