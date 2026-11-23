#!/usr/bin/env python3
"""news-image-20261124: draw Tuesday 24 November 2026's world news as a
1024x1024 front page and write it to /output/entry.png.

Python 3.13 standard library only. The PNG encoder and the 5x7 bitmap font
are written from scratch in this file; nothing is read from disk except the
output directory. The program is fully deterministic: same bytes every run.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# --- palette ---------------------------------------------------------------
PAPER = (246, 241, 231)   # warm newsprint
INK = (27, 27, 27)        # near-black text
NAVY = (20, 33, 61)       # masthead band
GOLD = (201, 162, 39)     # masthead rule
GREY = (120, 116, 104)    # secondary text
WHITE = (255, 255, 255)
RED = (180, 35, 24)
BLUE = (29, 78, 216)
TEAL = (15, 118, 110)
PURPLE = (109, 40, 217)
ORANGE = (194, 65, 12)
GREEN = (21, 128, 61)
SKY = (186, 220, 240)

# --- 5x7 bitmap font -------------------------------------------------------
# Each glyph: 7 rows of 5 pixels, '#' on, '.' off. Uppercase + digits + the
# punctuation the front page needs. Hand-drawn in this file.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10011", "10101", "11001", "10001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00010", "00100", "00100", "00100"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "'": ("00100", "00100", "00100", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    '/': ("00001", "00001", "00010", "00010", "00100", "01000", "10000"),
    '(': ("00011", "00100", "01000", "01000", "01000", "00100", "00011"),
    ')': ("11000", "00100", "00010", "00010", "00010", "00100", "11000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10010", "01000", "10101", "10010", "01101"),
    '*': ("00000", "01010", "00100", "11111", "00100", "01010", "00000"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (1px gap between glyphs)."""
    return len(text) * 6 * scale - scale


def draw_text(img, x, y, text, scale, color):
    """Draw uppercase text; unknown chars render as blanks."""
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    for dy in range(scale):
                        for dx in range(scale):
                            px, py = cx + col * scale + dx, y + row * scale + dy
                            if 0 <= px < W and 0 <= py < H:
                                img[py][px] = color
        cx += 6 * scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap into lines no wider than max_width pixels."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_centered(img, y, text, scale, color):
    draw_text(img, (W - text_width(text, scale)) // 2, y, text, scale, color)


# --- canvas primitives -----------------------------------------------------
def new_canvas():
    return [[PAPER for _ in range(W)] for _ in range(H)]


def rect(img, x, y, w, h, color):
    for py in range(max(0, y), min(H, y + h)):
        row = img[py]
        for px in range(max(0, x), min(W, x + w)):
            row[px] = color


def hline(img, x, y, w, color, thick=1):
    rect(img, x, y, w, thick, color)


def vline(img, x, y, h, color, thick=1):
    rect(img, x, y, thick, h, color)


def circle(img, cx, cy, r, color):
    for py in range(cy - r, cy + r + 1):
        for px in range(cx - r, cx + r + 1):
            if (px - cx) ** 2 + (py - cy) ** 2 <= r * r:
                if 0 <= px < W and 0 <= py < H:
                    img[py][px] = color


def line(img, x0, y0, x1, y1, color, thick=1):
    """Bresenham line with square thickness."""
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err, x, y = dx - dy, x0, y0
    while True:
        rect(img, x - thick // 2, y - thick // 2, thick, thick, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def triangle(img, pts, color):
    """Filled triangle from three (x, y) points, scanline fill."""
    (x0, y0), (x1, y1), (x2, y2) = sorted(pts, key=lambda p: p[1])
    for y in range(y0, y2 + 1):
        xs = []
        for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                   ((x1, y1), (x2, y2)),
                                   ((x0, y0), (x2, y2))):
            if ay <= y <= by and by != ay:
                xs.append(ax + (bx - ax) * (y - ay) / (by - ay))
            elif ay == by == y:
                xs += [ax, bx]
        if len(xs) >= 2:
            xa, xb = int(min(xs)), int(max(xs))
            rect(img, xa, y, xb - xa + 1, 1, color)


# --- PNG encoder -----------------------------------------------------------
def png_bytes(img):
    raw = bytearray()
    for row in img:
        raw.append(0)  # filter: none
        for (r, g, b) in row:
            raw += bytes((r, g, b))

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))

# --- pictograms (48x48 boxes, simple geometric shapes) ----------------------
def draw_icon(img, kind, x, y, color):
    if kind == "ship":
        rect(img, x + 4, y + 30, 40, 8, INK)                    # hull
        triangle(img, [(x + 44, y + 30), (x + 44, y + 38), (x + 48, y + 34)], INK)
        vline(img, x + 24, y + 8, 22, INK, 2)                  # mast
        triangle(img, [(x + 24, y + 10), (x + 24, y + 28), (x + 40, y + 28)], color)
        hline(img, x + 2, y + 44, 44, color, 2)                # waves
        hline(img, x + 10, y + 47, 28, color, 1)
    elif kind == "building":
        rect(img, x + 14, y + 8, 20, 36, INK)                  # tower
        for wy in (14, 22, 30, 38):
            for wx in (18, 25, 32):
                rect(img, x + wx, y + wy, 3, 3, PAPER)         # windows
        vline(img, x + 24, y + 2, 6, INK, 2)                   # flagpole
        rect(img, x + 24, y + 2, 11, 5, color)                 # flag
    elif kind == "shield":
        rect(img, x + 12, y + 6, 24, 20, color)                # shield top
        triangle(img, [(x + 12, y + 26), (x + 36, y + 26), (x + 24, y + 44)], color)
        line(img, x + 16, y + 20, x + 22, y + 28, WHITE, 3)    # check
        line(img, x + 22, y + 28, x + 34, y + 12, WHITE, 3)
    elif kind == "mic":
        circle(img, x + 24, y + 16, 9, color)                  # head
        rect(img, x + 22, y + 24, 4, 12, INK)                  # stem
        rect(img, x + 14, y + 36, 20, 4, INK)                  # base
        hline(img, x + 18, y + 12, 12, PAPER, 2)               # grille
        hline(img, x + 18, y + 18, 12, PAPER, 2)
    elif kind == "helmet":
        circle(img, x + 24, y + 24, 14, color)                 # dome
        rect(img, x + 8, y + 24, 32, 20, PAPER)                # cut lower half
        rect(img, x + 8, y + 24, 32, 4, color)                 # brim
        vline(img, x + 24, y + 8, 16, PAPER, 2)                # ridge
    elif kind == "wall":
        for row, off in ((0, 0), (1, 8), (2, 0)):
            for i in range(3):
                rect(img, x + 4 + off + i * 16, y + 8 + row * 12, 14, 10, color)
        line(img, x + 24, y + 8, x + 20, y + 44, INK, 2)       # crack


# --- the day's stories (verified from BBC / Reuters / AP / CNN / WSJ) ------
LEAD = {
    "tag": "TECH - MARKETS",
    "headline": "NVIDIA REINSTATES CEO HUANG",
    "summary": ("Trump says he made the deal as the chipmaker brings back its "
                "co-founder after his affair with an alleged spy. Shares surge "
                "and Congress objects."),
    "stat": "NASDAQ +6% - S&P +5% - CHIP INDEX +12% ON MONDAY",
    "accent": BLUE,
}

GRID = [
    {"tag": "WAR AT SEA", "icon": "ship", "accent": RED,
     "headline": "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA",
     "summary": ("Seven sea drones sank the corvette Merkury in Benghazi and hit "
                 "the cargo ship Angara."),
     "stat": "HELICOPTER DESTROYED - 10 WOUNDED"},
    {"tag": "ASIA", "icon": "building", "accent": TEAL,
     "headline": "NORTH KOREA MAY SHUT SWISS OFFICE",
     "summary": ("Pyongyang condemned Swiss sanctions on a children's camp linked "
                 "to Russia and may close the Swiss office."),
     "stat": "KCNA - TUESDAY"},
    {"tag": "BUSINESS", "icon": "shield", "accent": PURPLE,
     "headline": "CROWDSTRIKE BUYS ZSCALER IN $44BN DEAL",
     "summary": ("The cybersecurity firm agreed an all-stock takeover of its rival "
                 "as cyber threats mount."),
     "stat": "$43.9BN - ALL STOCK"},
    {"tag": "MIDDLE EAST", "icon": "mic", "accent": ORANGE,
     "headline": "IRAN FLOGS SINGER WHO SANG WITHOUT HIJAB",
     "summary": ("Authorities flogged a singer who performed without a hijab, her "
                 "lawyers said, defying the dress rules."),
     "stat": "LAWYERS CONFIRM THE FLOGGING"},
    {"tag": "MIDDLE EAST", "icon": "helmet", "accent": GREEN,
     "headline": "US WEIGHS TRAINING SYRIAN TROOPS",
     "summary": ("Washington is discussing plans to train Syrian soldiers in "
                 "demining, the first such mission since 2024."),
     "stat": "FIRST MISSION SINCE 2024"},
    {"tag": "AID - GAZA", "icon": "wall", "accent": RED,
     "headline": "GAZA NOW A TOXIC WASTELAND, OXFAM SAYS",
     "summary": ("Israeli attacks have turned Gaza into a toxic wasteland, Oxfam "
                 "said, poisoning its water, soil and air."),
     "stat": "OXFAM - TUESDAY"},
]


def draw_lead(img):
    x, y = 36, 136
    draw_text(img, x, y, LEAD["tag"], 1, LEAD["accent"])
    draw_text(img, x, y + 18, LEAD["headline"], 3, INK)
    lines = wrap_text(LEAD["summary"], 604, 2)
    for i, ln in enumerate(lines[:3]):
        draw_text(img, x, y + 56 + i * 16, ln, 2, INK)
    draw_text(img, x, y + 108, LEAD["stat"], 1, GREY)
    # chart panel: Wall Street roars back
    px, py, pw, ph = 660, 136, 328, 190
    rect(img, px, py, pw, ph, SKY)
    rect(img, px, py, pw, 2, INK)
    rect(img, px, py + ph - 2, pw, 2, INK)
    rect(img, px, py, 2, ph, INK)
    rect(img, px + pw - 2, py, 2, ph, INK)
    draw_text(img, px + 14, py + 12, "WALL ST ROARS BACK", 1, INK)
    draw_text(img, px + 14, py + 30, "NASDAQ +6%", 2, RED)
    rect(img, px + 30, py + 124, 44, 50, NAVY)
    rect(img, px + 100, py + 79, 44, 95, NAVY)
    rect(img, px + 170, py + 34, 44, 140, NAVY)
    line(img, px + 25, py + 119, px + 260, py + 29, RED, 4)
    hline(img, px, py + ph - 2, pw, INK, 2)


def draw_cell(img, story, x, y, w=466, h=196):
    rect(img, x, y, w, 6, story["accent"])
    draw_text(img, x, y + 14, story["tag"], 1, story["accent"])
    draw_icon(img, story["icon"], x, y + 30, story["accent"])
    lines = wrap_text(story["headline"], w - 60, 3)
    for i, ln in enumerate(lines[:3]):
        draw_text(img, x + 60, y + 30 + i * 24, ln, 3, INK)
    sy = y + 30 + len(lines[:3]) * 24 + 10
    slines = wrap_text(story["summary"], w, 2)
    for i, ln in enumerate(slines[:3]):
        draw_text(img, x, sy + i * 16, ln, 2, INK)
    draw_text(img, x, sy + len(slines[:3]) * 16 + 8, story["stat"], 1, GREY)
    hline(img, x, y + 188, w, (205, 199, 182), 1)


def build():
    img = new_canvas()
    # masthead
    rect(img, 0, 0, W, 118, NAVY)
    draw_centered(img, 24, "THE WORLD IN ONE DAY", 4, WHITE)
    draw_centered(img, 76, "TUESDAY 24 NOVEMBER 2026", 2, GOLD)
    rect(img, 0, 118, W, 6, GOLD)
    # lead story + chart
    draw_lead(img)
    hline(img, 36, 332, 952, INK, 2)
    # six stories in a 2x3 grid
    for i, story in enumerate(GRID):
        cx = 36 + (i % 2) * 486
        cy = 348 + (i // 2) * 212
        draw_cell(img, story, cx, cy)
    # footer
    hline(img, 36, 978, 952, GREY, 1)
    draw_centered(img, 986, "SOURCES: BBC - REUTERS - AP - CNN - WSJ  |  SEVEN STORIES",
                  1, GREY)
    return img


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(path, len(data), "bytes")


if __name__ == "__main__":
    main()
