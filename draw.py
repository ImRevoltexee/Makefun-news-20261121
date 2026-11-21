#!/usr/bin/env python3
"""Draw entry.png for make.fun bounty news-image-20261121.

Newspaper-style infographic, 1024x1024, drawn from scratch with Pillow.
No AI image generator, no network, no randomness, no timestamps:
running this script twice produces byte-identical output.

    python3 draw.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

PAPER = (253, 248, 238)      # warm newsprint
INK = (20, 24, 38)           # near-black
NAVY = (20, 33, 61)          # masthead band
GOLD = (212, 175, 55)        # masthead accent
RED = (178, 34, 34)          # rule / accents
CARD = (255, 255, 255)
CARD_EDGE = (205, 198, 182)
MUTED = (90, 86, 76)
STRIP = (32, 48, 80)         # ALSO TODAY band

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_TITLE = font("DejaVuSerif-Bold.ttf", 62)
F_DATE = font("DejaVuSans-Bold.ttf", 30)
F_TAG = font("DejaVuSans.ttf", 20)
F_SUB = font("DejaVuSans.ttf", 21)
F_KICK = font("DejaVuSans-Bold.ttf", 17)
F_HEAD = font("DejaVuSans-Bold.ttf", 25)
F_CAP = font("DejaVuSans.ttf", 19)
F_STRIP_HEAD = font("DejaVuSans-Bold.ttf", 19)
F_STRIP = font("DejaVuSans.ttf", 18)
F_FOOT = font("DejaVuSans.ttf", 15)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_icon(d, kind, x, y, s, color):
    """Simple glyph drawn with primitives inside a s x s box."""
    cx, cy = x + s // 2, y + s // 2
    if kind == "missile":  # starburst
        pts = []
        import math
        for i in range(16):
            ang = math.pi * i / 8
            r = s * 0.48 if i % 2 == 0 else s * 0.20
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        d.polygon(pts, fill=color)
        d.ellipse([cx - s * 0.13, cy - s * 0.13, cx + s * 0.13, cy + s * 0.13],
                  fill=PAPER)
    elif kind == "chart":  # falling line chart
        pts = [(x + 6, y + 12), (x + s * 0.35, y + s * 0.35),
               (x + s * 0.55, y + s * 0.28), (x + s - 8, y + s - 10)]
        d.line(pts, fill=color, width=6, joint="curve")
        d.polygon([(x + s - 8, y + s - 10), (x + s - 22, y + s - 12),
                   (x + s - 10, y + s - 24)], fill=color)
        d.line([(x + 6, y + s - 8), (x + s - 6, y + s - 8)],
               fill=MUTED, width=3)
    elif kind == "scales":  # balance scales
        d.line([(cx, y + 8), (cx, y + s - 10)], fill=color, width=5)
        d.line([(x + 8, y + 18), (x + s - 8, y + 18)], fill=color, width=5)
        d.polygon([(x + 4, y + 20), (x + 22, y + 20), (x + 13, y + s - 14)],
                  outline=color, width=3)
        d.polygon([(x + s - 22, y + 20), (x + s - 4, y + 20),
                   (x + s - 13, y + s - 14)], outline=color, width=3)
        d.line([(x + 10, y + s - 8), (x + s - 10, y + s - 8)],
               fill=color, width=5)
    elif kind == "quake":  # seismograph zigzag
        pts = [(x + 4, cy), (x + s * 0.22, cy), (x + s * 0.30, cy - 18),
               (x + s * 0.38, cy + 20), (x + s * 0.48, cy - 26),
               (x + s * 0.58, cy + 22), (x + s * 0.66, cy - 10),
               (x + s * 0.74, cy), (x + s - 4, cy)]
        d.line(pts, fill=color, width=5, joint="curve")
        d.line([(x + 4, y + s - 8), (x + s - 4, y + s - 8)],
               fill=MUTED, width=3)
    elif kind == "globe":  # globe with meridians
        d.ellipse([x + 4, y + 4, x + s - 4, y + s - 4], outline=color, width=5)
        d.ellipse([cx - 12, y + 4, cx + 12, y + s - 4], outline=color, width=3)
        d.line([(x + 4, cy), (x + s - 4, cy)], fill=color, width=3)
        d.arc([x + 4, y + 4, x + s - 4, y + s - 4], 200, 340, fill=color, width=3)
    elif kind == "pill":  # capsule
        d.rounded_rectangle([x + 8, y + s // 2 - 13, x + s - 8, y + s // 2 + 13],
                            radius=13, outline=color, width=5)
        d.line([(cx, y + s // 2 - 13), (cx, y + s // 2 + 13)],
               fill=color, width=4)


STORIES = [
    ("CONFLICT", "missile", (178, 34, 34),
     "Russian missiles land in Poland",
     "400+ drones and 110 missiles hit Ukraine overnight; two "
     "missiles and a drone came down in Poland. PM Tusk calls it "
     "a deliberate provocation."),
    ("ECONOMY", "chart", (196, 90, 0),
     "AI sell-off drags S&P into correction",
     "US stocks fell about 3.7% as AI and chip shares plunged, "
     "pushing the S&P 500 and the Dow into correction territory."),
    ("JUSTICE", "scales", (38, 84, 124),
     "World court: Myanmar committed genocide",
     "The ICJ ruled Myanmar's forces committed state-sponsored "
     "genocide against the Rohingya - a first for the court."),
    ("DISASTER", "quake", (120, 72, 20),
     "Magnitude 6.8 quake shakes Peru",
     "The tremor struck the Junin region and rattled Lima, 320 km "
     "away. No casualties or major damage were reported."),
    ("CLIMATE", "globe", (34, 120, 70),
     "COP31 talks spill into overtime",
     "Fossil-fuel language was stripped from the draft deal in "
     "Antalya, and negotiators work on through the weekend."),
    ("HEALTH", "pill", (0, 128, 128),
     "Cancer pill makes tumours vanish",
     "Daraxonrasib plus chemo made tumours undetectable in 1 in 12 "
     "patients in a pancreatic cancer trial."),
]

ALSO_TODAY = [
    "Trump, Xi and Putin end their first trilateral summit with a "
    "joint vow against nuclear war.",
    "UK and EU sign deals on food trade, carbon markets and youth "
    "mobility in Brussels.",
    "New York mayor sets 2032 as the new date to close the Rikers "
    "Island jail complex.",
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 148], fill=NAVY)
    d.rectangle([0, 148, W, 154], fill=RED)
    title = "THE WORLD IN ONE DAY"
    tw = d.textlength(title, font=F_TITLE)
    d.text(((W - tw) / 2, 18), title, font=F_TITLE, fill=(255, 255, 255))
    date = "SATURDAY, 21 NOVEMBER 2026"
    dw = d.textlength(date, font=F_DATE)
    d.text(((W - dw) / 2, 92), date, font=F_DATE, fill=GOLD)
    tag = "make.fun  ·  news-image-20261121"
    d.text((28, 118), tag, font=F_TAG, fill=(180, 190, 210))
    d.text((W - 28 - d.textlength("SIX STORIES + THREE MORE", font=F_TAG),
            118), "SIX STORIES + THREE MORE", font=F_TAG,
           fill=(180, 190, 210))

    # ---- sub-headline ----
    sub = "Six stories that defined Saturday, 21 November 2026 - in one image."
    d.text((28, 168), sub, font=F_SUB, fill=MUTED)

    # ---- story grid: 2 columns x 3 rows ----
    mx, my = 28, 200
    gap = 16
    cw = (W - 2 * mx - gap) // 2
    ch = 196
    for i, (kick, icon, color, head, cap) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = mx + col * (cw + gap)
        y = my + row * (ch + gap)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=10,
                            fill=CARD, outline=CARD_EDGE, width=2)
        d.rectangle([x + 10, y, x + cw - 10, y + 6], fill=color)
        # icon tile
        ix, iy, s = x + 16, y + 22, 62
        d.rounded_rectangle([ix, iy, ix + s, iy + s], radius=8,
                            outline=color, width=3)
        draw_icon(d, icon, ix + 4, iy + 4, s - 8, color)
        # kicker + headline
        tx = ix + s + 14
        tw_max = x + cw - 16 - tx
        d.text((tx, y + 20), kick, font=F_KICK, fill=color)
        lines = wrap(d, head, F_HEAD, tw_max)[:2]
        ly = y + 44
        for line in lines:
            d.text((tx, ly), line, font=F_HEAD, fill=INK)
            ly += 28
        # caption
        cap_lines = wrap(d, cap, F_CAP, cw - 32)[:3]
        cy = y + 108
        for line in cap_lines:
            d.text((x + 16, cy), line, font=F_CAP, fill=(52, 50, 44))
            cy += 24

    # ---- ALSO TODAY strip ----
    # Three short items side by side; each column is (W - margins) / 3 wide
    # and wraps to at most 4 lines so the strip stays a fixed height.
    sy = my + 3 * ch + 2 * gap + 14
    d.rounded_rectangle([mx, sy, W - mx, sy + 118], radius=10, fill=STRIP)
    d.text((mx + 16, sy + 12), "ALSO TODAY", font=F_STRIP_HEAD, fill=GOLD)
    col_w = (W - 2 * mx - 32) // 3
    for j, item in enumerate(ALSO_TODAY):
        ax = mx + 16 + j * col_w
        lines = wrap(d, item, F_STRIP, col_w - 18)[:4]
        ay = sy + 42
        for line in lines:
            d.text((ax, ay), line, font=F_STRIP, fill=(235, 238, 245))
            ay += 21

    # ---- footer ----
    fy = sy + 118 + 12
    d.line([(mx, fy + 4), (W - mx, fy + 4)], fill=CARD_EDGE, width=2)
    d.text((mx, fy + 14),
           "Sources: Reuters, OneTurn, CNN, WSJ, NY Post, ecancer, OncLive, "
           "UN News, AP, The Daily Short.",
           font=F_FOOT, fill=MUTED)
    d.text((mx, fy + 36),
           "Drawn with code (Pillow) - no AI images  ·  news-image-20261121",
           font=F_FOOT, fill=MUTED)

    img.save(OUT, format="PNG")
    print("wrote %s (%dx%d)" % (OUT, W, H))


if __name__ == "__main__":
    main()
