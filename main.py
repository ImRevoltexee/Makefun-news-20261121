#!/usr/bin/env python3
"""Entry point for the make.fun bounty news-image-20261121.

Standard library only. Copies ``entry.png`` (sitting next to this file)
to ``$MAKEFUN_OUTPUT_DIR/entry.png`` (default ``/output``), after
checking it is a real image no bigger than 1 MiB and no larger than
1024x1024 pixels. Both PNG and JPEG inputs are accepted: the size is
read straight out of the file header, so no image library is needed.

PNG: the 8-byte magic 89 50 4E 47 0D 0A 1A 0A is followed by the IHDR
chunk, which stores width and height as big-endian 32-bit integers.

JPEG: the file starts with FF D8. Markers are walked two bytes at a
time; a Start-Of-Frame marker (0xC0 baseline, 0xC1 extended
sequential, or 0xC2 progressive) carries the height and then the width
as big-endian 16-bit integers, five bytes past the marker code.

Run:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import hashlib
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY = os.path.join(HERE, "entry.png")

MAX_BYTES = 1 * 1024 * 1024
MAX_W = 1024
MAX_H = 1024


def fail(msg):
    print("error: " + msg, file=sys.stderr)
    return 1


def png_size(blob):
    """Return (width, height) for a PNG byte string, else None."""
    if len(blob) < 24:
        return None
    if blob[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    if blob[12:16] != b"IHDR":
        return None
    w, h = struct.unpack(">II", blob[16:24])
    return (w, h)


def jpeg_size(blob):
    """Return (width, height) for a JPEG byte string, else None."""
    if len(blob) < 4 or blob[0] != 0xFF or blob[1] != 0xD8:
        return None
    pos = 2
    while pos + 4 <= len(blob):
        if blob[pos] != 0xFF:
            return None
        marker = blob[pos + 1]
        # Padding bytes and the standalone markers carry no length.
        if marker == 0xFF:
            pos += 1
            continue
        if marker == 0x01 or 0xD0 <= marker <= 0xD9:
            pos += 2
            continue
        seg_len = struct.unpack(">H", blob[pos + 2:pos + 4])[0]
        if seg_len < 2 or pos + 2 + seg_len > len(blob):
            return None
        if marker in (0xC0, 0xC1, 0xC2):
            # Segment payload: 1 byte precision, then height, then width.
            h, w = struct.unpack(">HH", blob[pos + 5:pos + 9])
            return (w, h)
        pos += 2 + seg_len
    return None


def image_size(blob):
    """Detect the format and return (kind, width, height), else None."""
    size = png_size(blob)
    if size is not None:
        return ("PNG", size[0], size[1])
    size = jpeg_size(blob)
    if size is not None:
        return ("JPEG", size[0], size[1])
    return None


def main():
    if not os.path.isfile(ENTRY):
        return fail("entry.png not found next to main.py")

    with open(ENTRY, "rb") as fh:
        blob = fh.read()

    if len(blob) > MAX_BYTES:
        return fail("entry.png is %d bytes, over the 1 MiB limit"
                    % len(blob))

    found = image_size(blob)
    if found is None:
        return fail("entry.png is not a PNG or JPEG image")

    kind, width, height = found
    if width > MAX_W or height > MAX_H:
        return fail("%s is %dx%d, over the 1024x1024 limit"
                    % (kind, width, height))

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    with open(dest, "wb") as fh:
        fh.write(blob)

    with open(dest, "rb") as fh:
        copied = fh.read()
    if hashlib.sha256(copied).hexdigest() != \
            hashlib.sha256(blob).hexdigest():
        return fail("copied bytes do not match entry.png")

    print("ok: %s %dx%d, %d bytes -> %s"
          % (kind, width, height, len(blob), dest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
