#!/usr/bin/env python3
"""Render Zalo chat screenshots from dialogue JSON / JSONL.

One dialogue, one image:
    python src/generate.py --input dialogues/01_work_ml.json \
        --themes dark --devices screen_1440x3200 --out out/one

One dialogue, all variants (default 2 themes x 1 device = 2 images):
    python src/generate.py --input dialogues/01_work_ml.json --out out/one

A bank of 50k dialogues (one JSON object per line), 8 parallel browsers:
    python src/generate.py --input bank.jsonl --out out/bank \
        --formats jpg --workers 8

Sharding across machines / processes:
    python src/generate.py --input bank.jsonl --out out/bank --shard 0/8 --workers 8
    ... --shard 1/8 ... etc.

Every image gets a label record in <out>/manifest.jsonl. Pass --formats png,jpg,json
to also keep the lossless master and a per-image sidecar.
"""

import argparse
import itertools
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

DEFAULTS = {
    "in": str(ROOT / "dialogues"),
    "out": str(ROOT / "out"),
    "themes": "dark,light",
    "devices": "screen_1440x3200",
    "formats": "jpg,json",
}


def iter_dialogues(paths):
    for p in paths:
        p = Path(p)
        if not p.exists():
            raise SystemExit(f"input not found: {p}")
        if p.is_dir():
            files = sorted(itertools.chain(p.rglob("*.json"), p.rglob("*.jsonl")))
        else:
            files = [p]
        for f in files:
            if f.suffix.lower() == ".jsonl":
                with f.open(encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if line:
                            d = json.loads(line)
                            d.setdefault("_source", f"{f.name}:{d.get('id', '')}")
                            yield d
            else:
                d = json.loads(f.read_text(encoding="utf-8"))
                d.setdefault("_source", str(f))
                yield d


def anchors(total, windows):
    """End indices (exclusive) for N windows, newest first."""
    if windows <= 1:
        return [(total, 0)]
    return [(max(4, round(total * (k + 1) / windows)), k) for k in range(windows)]


def expand(dialogues, themes, devices, out, windows=1):
    for dlg in dialogues:
        ends = anchors(len(dlg["messages"]), windows)
        for theme in themes:
            for device in devices:
                for end, widx in ends:
                    yield (dlg, theme, device, out, (0, end), widx)


# ------------------------------------------------------------------ workers ---
_R = None


def _init():
    global _R
    from zalo.render import Renderer

    _R = Renderer()


def _run(task):
    dlg, theme, device, out, window, widx, formats = task
    return _R.render(dlg, theme, device, out, formats=formats,
                     window=window, window_index=widx)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--input", "--data", dest="input", nargs="+", default=[DEFAULTS["in"]])
    ap.add_argument("--out", default=DEFAULTS["out"])
    ap.add_argument("--themes", default=DEFAULTS["themes"])
    ap.add_argument("--devices", default=DEFAULTS["devices"])
    ap.add_argument("--formats", default=DEFAULTS["formats"], help="jpg, png, json")
    ap.add_argument("--workers", type=int, default=1, help="parallel browsers (1-8)")
    ap.add_argument("--windows", type=int, default=1,
                    help="screenshots per dialogue per theme/device at different scroll points")
    ap.add_argument("--limit", type=int, default=0, help="max images, 0 = all")
    ap.add_argument("--shard", default="0/1", help="i/n: render only tasks where idx %% n == i")
    ap.add_argument("--only", default=None, help="comma separated id substrings")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--append", action="store_true", help="append to the manifest")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    themes = [t.strip() for t in args.themes.split(",") if t.strip()]
    devices = [d.strip() for d in args.devices.split(",") if d.strip()]
    formats = tuple(f.strip() for f in args.formats.split(",") if f.strip())

    try:
        si, sn = (int(x) for x in args.shard.split("/"))
    except ValueError:
        raise SystemExit("--shard must look like 0/8")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = Path(args.manifest) if args.manifest else out / "manifest.jsonl"

    dialogues = iter_dialogues(args.input)
    if args.only:
        wanted = [x.strip() for x in args.only.split(",") if x.strip()]
        dialogues = (d for d in dialogues if any(w in str(d.get("id", "")) for w in wanted))

    tasks = expand(dialogues, themes, devices, out, windows=max(1, args.windows))
    if sn > 1:
        tasks = itertools.islice(
            (t for i, t in enumerate(tasks) if i % sn == si), None
        )
    if args.limit:
        tasks = itertools.islice(tasks, args.limit)

    started = time.time()
    done = 0
    failures = []

    mode = "a" if args.append else "w"
    with manifest.open(mode, encoding="utf-8") as mf:
        if args.workers <= 1:
            _init()
            for task in tasks:
                try:
                    meta = _run(task + (formats,))
                except Exception as e:  # keep the batch alive
                    failures.append((task[0].get("id"), repr(e)))
                    continue
                mf.write(json.dumps(meta, ensure_ascii=False) + "\n")
                mf.flush()
                done += 1
                if not args.quiet:
                    print(f"[{done}] {meta['id']} {meta['theme']} {meta['device']}", flush=True)
        else:
            with ProcessPoolExecutor(max_workers=args.workers, initializer=_init) as pool:
                futures = {pool.submit(_run, task + (formats,)): task for task in tasks}
                for fut in as_completed(futures):
                    task = futures[fut]
                    try:
                        meta = fut.result()
                    except Exception as e:
                        failures.append((task[0].get("id"), repr(e)))
                        continue
                    mf.write(json.dumps(meta, ensure_ascii=False) + "\n")
                    done += 1
                    if not args.quiet and (done % 25 == 0 or args.workers <= 2):
                        rate = done / max(1e-6, time.time() - started)
                        print(f"[{done}] {rate:.2f} img/s", flush=True)

    elapsed = time.time() - started
    print(
        f"\n{done} images in {elapsed:.1f}s "
        f"({done / max(elapsed, 1e-6):.2f} img/s) -> {out}",
        flush=True,
    )
    print(f"manifest: {manifest}", flush=True)
    if failures:
        print(f"FAILED: {len(failures)}", flush=True)
        for fid, err in failures[:10]:
            print(f"  {fid}: {err}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
