#!/usr/bin/env python3
"""Deprecated alias for generate.py (kept so old commands keep working)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
