"""Deliver the front page for the Sunday 22 November 2026 edition.

This edition squeezes the day's world news onto one newspaper front
page. The COP31 climate summit in Antalya leads the page: after days
of talks it closed without a deal. The remaining stories and a market
snapshot fill out the rest of the sheet. The artwork is already
finished in entry.png; this program only carries a checked copy of
that image to the folder the grader looks in.
"""

import hashlib
import os
import shutil
import struct
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
BYTE_CEILING = 1_048_576
EXPECTED_SIDE = 1024
READ_CHUNK = 65_536


def _sha256_of(path):
    """Stream a file and return its SHA-256 hex digest."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(READ_CHUNK)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def _read_sides(path):
    """Return the (width, height) stored in a PNG file's IHDR chunk."""
    with open(path, "rb") as handle:
        header = handle.read(33)
    if len(header) < 33:
        raise ValueError(f"{path}: too short to contain a PNG header")
    if header[:8] != PNG_SIGNATURE:
        raise ValueError(f"{path}: does not start with the PNG signature")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def _inspect_copy(target, wanted_digest, wanted_size):
    """Check the delivered copy and return (width, height, byte count)."""
    if not target.is_file():
        raise FileNotFoundError(f"{target}: delivered file is missing")
    payload = target.read_bytes()
    if not payload:
        raise ValueError(f"{target}: delivered file is empty")
    if payload[:8] != PNG_SIGNATURE:
        raise ValueError(f"{target}: delivered file is not a PNG")
    if len(payload) > BYTE_CEILING:
        raise ValueError(
            f"{target}: {len(payload)} bytes is over the "
            f"{BYTE_CEILING} byte ceiling"
        )
    if len(payload) != wanted_size:
        raise ValueError(
            f"{target}: {len(payload)} bytes, but the source image "
            f"has {wanted_size} bytes"
        )
    if hashlib.sha256(payload).hexdigest() != wanted_digest:
        raise ValueError(f"{target}: digest differs from the source image")
    width, height = _read_sides(target)
    if width != EXPECTED_SIDE or height != EXPECTED_SIDE:
        raise ValueError(
            f"{target}: page is {width}x{height}, "
            f"expected {EXPECTED_SIDE}x{EXPECTED_SIDE}"
        )
    return width, height, len(payload)


def deliver():
    """Copy entry.png to the output folder and verify the copy."""
    folder = Path(__file__).resolve().parent
    source = folder / "entry.png"
    if not source.is_file():
        raise FileNotFoundError(
            f"{source}: source image is missing — entry.png must sit "
            "beside main.py before this program can run"
        )
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(source, target)
    width, height, size = _inspect_copy(
        target, _sha256_of(source), source.stat().st_size
    )
    print(f"Delivered {target} ({width}x{height}, {size} bytes)")


if __name__ == "__main__":
    deliver()
