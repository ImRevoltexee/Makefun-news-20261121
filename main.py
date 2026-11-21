"""Copy the finished news-image entry to the grader's output directory.

What this script does
---------------------
The entry artwork lives next to this script as ``entry.png``.  When the
grader runs this file it validates that artwork and copies it to the
directory named by the ``MAKEFUN_OUTPUT_DIR`` environment variable
(``/output`` when the variable is not set), creating that directory
first.  On success it prints a short confirmation and exits 0; on any
validation failure it prints the problem to stderr and exits 1.

How the dimension checks work
------------------------------
Only two image formats are accepted, and both are parsed by hand with
the standard library -- no image library is needed:

* PNG: the file must start with the 8-byte PNG signature
  (89 50 4E 47 0D 0A 1A 0A).  The first chunk is always IHDR, and its
  data starts with the width and then the height, each stored as a
  big-endian unsigned 32-bit integer.  So width is read from bytes
  16..20 and height from bytes 20..24 of the file.

* JPEG: the file must start with the SOI marker FF D8.  After that the
  file is a sequence of segments, each introduced by an FF byte plus a
  marker code, followed (for most markers) by a 2-byte big-endian
  length that includes the length field itself.  The script walks
  segment by segment, skipping standalone markers and padding FF
  bytes, until it reaches a Start-Of-Frame marker: 0xC0 (baseline),
  0xC1 (extended sequential) or 0xC2 (progressive).  Inside a frame
  segment the layout is: 1 byte precision, then height as a big-endian
  16-bit integer, then width as a big-endian 16-bit integer -- so the
  dimensions sit 5 bytes past the marker code.  Markers that carry no
  payload (RSTn, SOI, TEM) are stepped over one byte at a time instead
  of being skipped by length.

Limits enforced before copying: the file must exist, must be no larger
than 1 MiB (1_048_576 bytes), and its dimensions must be no larger than
1024 x 1024 pixels.
"""

import os
import shutil
import struct
import sys

MAX_BYTES = 1_048_576
MAX_WIDTH = 1024
MAX_HEIGHT = 1024

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SOI = b"\xff\xd8"
# Start-Of-Frame markers whose segment holds the image dimensions.
SOF_MARKERS = {0xC0, 0xC1, 0xC2}
# Markers with no length field / no payload to skip over.
STANDALONE_MARKERS = {0x01} | set(range(0xD0, 0xD8))


def read_png_dimensions(data):
    """Return (width, height) for PNG bytes, or None if not a PNG."""
    if len(data) < 24 or data[:8] != PNG_SIGNATURE:
        return None
    if data[12:16] != b"IHDR":
        return None
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def read_jpeg_dimensions(data):
    """Return (width, height) for JPEG bytes, or None if not a JPEG."""
    if len(data) < 4 or data[:2] != JPEG_SOI:
        return None
    pos = 2
    while pos + 1 < len(data):
        # Every segment starts with 0xFF; collapse runs of padding 0xFF.
        if data[pos] != 0xFF:
            return None
        while pos < len(data) and data[pos] == 0xFF:
            pos += 1
        if pos >= len(data):
            return None
        marker = data[pos]
        pos += 1
        if marker in STANDALONE_MARKERS:
            continue
        if marker in SOF_MARKERS:
            # 1 byte precision, then height (2 bytes), then width (2 bytes).
            if pos + 7 > len(data):
                return None
            height, width = struct.unpack(">HH", data[pos + 3:pos + 7])
            return width, height
        # Any other marker: skip its segment using its length field.
        if pos + 2 > len(data):
            return None
        (segment_length,) = struct.unpack(">H", data[pos:pos + 2])
        if segment_length < 2:
            return None
        pos += segment_length
    return None


def image_dimensions(path):
    """Return (width, height) of a PNG or JPEG file, else None."""
    with open(path, "rb") as handle:
        blob = handle.read()
    return read_png_dimensions(blob) or read_jpeg_dimensions(blob)


def fail(message):
    """Print an error to stderr and exit non-zero."""
    print("error: %s" % message, file=sys.stderr)
    return 1


def run():
    """Validate entry.png next to this script and copy it to the output dir."""
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")

    if not os.path.isfile(source):
        return fail(
            "entry.png not found next to main.py (looked in %s) -- "
            "make sure the finished artwork is saved as entry.png "
            "in the same folder as this script" % here
        )

    size = os.path.getsize(source)
    if size > MAX_BYTES:
        return fail(
            "entry.png is %d bytes, over the 1 MiB limit" % size
        )

    try:
        dimensions = image_dimensions(source)
    except OSError as exc:
        return fail("could not read entry.png: %s" % exc)
    if dimensions is None:
        return fail("entry.png is not a PNG or JPEG image")

    width, height = dimensions
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        return fail(
            "entry.png is %dx%d, over the %dx%d limit"
            % (width, height, MAX_WIDTH, MAX_HEIGHT)
        )

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(output_dir, exist_ok=True)
    destination = os.path.join(output_dir, "entry.png")
    shutil.copyfile(source, destination)
    print("ok: copied entry.png (%dx%d, %d bytes) to %s"
          % (width, height, size, destination))
    return 0


if __name__ == "__main__":
    sys.exit(run())
