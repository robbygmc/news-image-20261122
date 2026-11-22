#!/usr/bin/env python3
"""news-image-20261122 entry: THE WORLD TODAY, Sunday 22 November 2026.

Python 3.13, standard library only. The finished front page ships in
this repository as entry.png; the program copies it to the output
directory (``$MAKEFUN_OUTPUT_DIR`` or ``/output``). The copy is
byte-for-byte identical on every run, so the two grading runs agree.

This edition: Sunday 22 November 2026. Lead story — COP31 collapses
with no deal in Antalya: two weeks of talks and two days of overtime
end with no agreement, the EU rejecting a final draft with no mention
of fossil fuels and the presidency declaring no consensus, the longest
climate summit ever. entry.png is a PIL-drawn front page (masthead,
drawn Antalya dusk scene, lead story, supporting stories and market
line), verified 1024x1024.
"""

import hashlib
import os
import shutil
from pathlib import Path

SOURCE = Path(__file__).resolve().parent / "entry.png"
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUT_DIR / "entry.png"
    shutil.copyfile(SOURCE, target)
    # A failed copy must fail loudly, never ship an empty file.
    assert target.is_file() and target.stat().st_size > 0, "no entry.png written"
    # The gate refuses anything over 1 MiB or not a PNG: check both here.
    data = target.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "entry.png is not a PNG"
    assert len(data) <= 1_048_576, "entry.png is over 1 MiB"
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == \
        hashlib.sha256(data).hexdigest(), "entry.png mismatch"
    # The bounty wants a 1024x1024 front page: verify the PNG's own header.
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    assert (width, height) == (1024, 1024), \
        f"entry.png is {width}x{height}, not 1024x1024"
    print(f"wrote {target} ({width}x{height}, {len(data)} bytes)")


if __name__ == "__main__":
    main()
