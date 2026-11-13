#!/usr/bin/env python3
"""Draw entry.png: a newspaper-front-page infographic summing up the world
news of Friday, 13 November 2026. Deterministic: no timestamps, no random
numbers, no network. Pure PIL drawing on a 1024x1024 canvas."""

import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (17, 24, 39)
NAVY = (15, 42, 67)
RED = (185, 28, 28)
WHITE = (255, 255, 255)
CARD = (255, 255, 255)
MUTED = (75, 85, 99)
RULE = (203, 213, 225)
GOLD = (245, 158, 11)
BLUE = (37, 99, 235)
SKY = (56, 130, 246)

FONT_DIR = "/usr/share/fonts/truetype/noto"
BOLD = FONT_DIR + "/NotoSans-Bold.ttf"
REG = FONT_DIR + "/NotoSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, start_size, max_w, min_size=14):
    """Largest font size (<= start_size) at which text fits max_w."""
    size = start_size
    while size > min_size:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(path, min_size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines fitting max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
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


def block_height(n_lines, size, leading_factor=1.28):
    return int(n_lines * size * leading_factor)


def draw_lines(draw, x, y, lines, fnt, fill):
    leading = int(fnt.size * 1.28)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def fit_deck(draw, text, max_w, max_h, start_size):
    """Shrink deck font until the wrapped text fits max_h. Returns (font, lines)."""
    size = start_size
    while size >= 18:
        f = font(REG, size)
        lines = wrap(draw, text, f, max_w)
        if block_height(len(lines), size) <= max_h:
            return f, lines
        size -= 1
    f = font(REG, 18)
    return f, wrap(draw, text, f, max_w)


# ---------------------------------------------------------------- icons ----
def icon_chip(draw, cx, cy, s):
    """Microchip: body, pins, inner die."""
    b = s // 2
    pin = max(4, s // 14)
    for i in range(3):
        off = -b // 2 + i * (b // 2)
        draw.rectangle([cx + off - 2, cy - b - pin, cx + off + 2, cy - b], fill=INK)
        draw.rectangle([cx + off - 2, cy + b, cx + off + 2, cy + b + pin], fill=INK)
        draw.rectangle([cx - b - pin, cy + off - 2, cx - b, cy + off + 2], fill=INK)
        draw.rectangle([cx + b, cy + off - 2, cx + b + pin, cy + off + 2], fill=INK)
    draw.rounded_rectangle([cx - b, cy - b, cx + b, cy + b], radius=8, fill=NAVY)
    draw.rounded_rectangle([cx - b // 2, cy - b // 2, cx + b // 2, cy + b // 2],
                           radius=5, fill=GOLD)
    draw.rectangle([cx - 4, cy - 4, cx + 4, cy + 4], fill=NAVY)


def icon_cloud(draw, cx, cy, s):
    """Cloud with a lightning cut (outage)."""
    r = s // 3
    draw.ellipse([cx - s // 2, cy - r // 2, cx - s // 2 + 2 * r, cy + r // 2 + r // 3],
                 fill=SKY)
    draw.ellipse([cx - s // 4, cy - r, cx - s // 4 + 2 * r, cy + r // 3], fill=SKY)
    draw.ellipse([cx, cy - r // 2, cx + 2 * r, cy + r // 2 + r // 3], fill=SKY)
    draw.rounded_rectangle([cx - s // 2, cy, cx + s // 2, cy + r // 2],
                           radius=r // 2, fill=SKY)
    bx, by = cx + s // 6, cy - r // 3
    bolt = [(bx, by), (bx - 16, by + 34), (bx - 2, by + 34),
            (bx - 14, by + 66), (bx + 18, by + 22), (bx + 2, by + 22)]
    draw.polygon(bolt, fill=GOLD)


def icon_flags(draw, cx, cy, s):
    """Two flags on poles: Ukraine (blue/yellow) and EU (navy, gold stars)."""
    pole_h = s
    draw.rectangle([cx - s // 2 - 3, cy - pole_h // 2, cx - s // 2 + 3,
                    cy + pole_h // 2], fill=INK)
    draw.rectangle([cx + s // 2 - 3, cy - pole_h // 2, cx + s // 2 + 3,
                    cy + pole_h // 2], fill=INK)
    fw, fh = s // 2 - 6, s // 3
    x0, y0 = cx - s // 2 + 6, cy - pole_h // 2
    draw.rectangle([x0, y0, x0 + fw, y0 + fh // 2], fill=BLUE)
    draw.rectangle([x0, y0 + fh // 2, x0 + fw, y0 + fh], fill=GOLD)
    x1 = cx + 6
    draw.rectangle([x1, y0, x1 + fw, y0 + fh], fill=NAVY)
    for k in range(8):
        ang = math.pi * 2 * k / 8
        sx = x1 + fw // 2 + int((fh // 3) * math.cos(ang))
        sy = y0 + fh // 2 + int((fh // 3) * math.sin(ang))
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=GOLD)


def icon_tanker(draw, cx, cy, s):
    """Oil/LNG tanker on waves. Everything stays inside the s x s box
    centred on (cx, cy) so it never collides with the headline below."""
    hw = s // 2 - 2
    # funnel (top) and deckhouse
    draw.rectangle([cx + hw - 24, cy - s // 2 + 2, cx + hw - 12, cy - 8],
                   fill=INK)
    draw.rectangle([cx - hw + 6, cy - 18, cx - hw + 34, cy - 2], fill=NAVY)
    draw.rectangle([cx + 8, cy - 12, cx + hw - 6, cy - 2], fill=WHITE,
                   outline=NAVY, width=2)
    # hull
    hull = [(cx - hw, cy - 2), (cx + hw, cy - 2), (cx + hw - 12, cy + 16),
            (cx - hw + 12, cy + 16)]
    draw.polygon(hull, fill=RED)
    # waves
    for wx in (-hw + 4, -hw // 3, hw // 3, hw - 24):
        draw.arc([cx + wx, cy + 20, cx + wx + 28, cy + 34], 0, 180,
                 fill=SKY, width=4)


def icon_hospital(draw, cx, cy, s):
    """Hospital cross in a rounded square."""
    b = s // 2
    draw.rounded_rectangle([cx - b, cy - b, cx + b, cy + b], radius=12,
                           fill=WHITE, outline=RED, width=4)
    cw, ch = s // 5, s // 5 * 3
    draw.rectangle([cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2],
                   fill=RED)
    draw.rectangle([cx - ch // 2, cy - cw // 2, cx + ch // 2, cy + cw // 2],
                   fill=RED)


def icon_ball(draw, cx, cy, s):
    """Football: white circle, black pentagon, seam lines."""
    r = s // 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=INK,
                 width=4)
    pr = r // 3
    pts = []
    for k in range(5):
        ang = -math.pi / 2 + k * 2 * math.pi / 5
        pts.append((cx + pr * math.cos(ang), cy + pr * math.sin(ang)))
    draw.polygon(pts, fill=INK)
    for k in range(5):
        ang = -math.pi / 2 + k * 2 * math.pi / 5
        ex, ey = cx + r * math.cos(ang), cy + r * math.sin(ang)
        vx, vy = pts[k]
        draw.line([vx, vy, ex, ey], fill=INK, width=3)


ICONS = {
    "chip": icon_chip,
    "cloud": icon_cloud,
    "flags": icon_flags,
    "tanker": icon_tanker,
    "hospital": icon_hospital,
    "ball": icon_ball,
}


def panel_side(draw, x, y, w, h, story, icon_size=104,
               headline_size=46, deck_size=28):
    """Lead layout: icon left, kicker + headline + deck to its right."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=CARD,
                           outline=RULE, width=2)
    pad = 22
    ICONS[story["icon"]](draw, x + pad + icon_size // 2,
                         y + pad + icon_size // 2, icon_size)
    tx = x + pad + icon_size + 24
    tw = x + w - pad - tx
    ky = y + pad
    kf = font(BOLD, 25)
    draw.text((tx, ky), story["kicker"], font=kf, fill=RED)
    ky += 36
    hf = font(BOLD, headline_size)
    lines = wrap(draw, story["headline"], hf, tw)
    ky = draw_lines(draw, tx, ky, lines, hf, INK)
    deck_h = (y + h - pad) - (ky + 8)
    df, dlines = fit_deck(draw, story["deck"], tw, deck_h, deck_size)
    draw_lines(draw, tx, ky + 8, dlines, df, MUTED)


def panel_stack(draw, x, y, w, h, story, icon_size=64,
                headline_size=32, deck_size=23, kicker_size=23):
    """Stacked layout: icon + kicker on the top row, headline and deck
    full-width below. Used for the 2- and 3-column rows."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10, fill=CARD,
                           outline=RULE, width=2)
    pad = 20
    ICONS[story["icon"]](draw, x + pad + icon_size // 2,
                         y + pad + icon_size // 2, icon_size)
    kf = fit_font(draw, story["kicker"], BOLD, kicker_size,
                  w - pad - icon_size - 12 - pad)
    draw.text((x + pad + icon_size + 12, y + pad + icon_size // 2 - kf.size // 2),
              story["kicker"], font=kf, fill=RED)
    hx = x + pad
    hw = w - 2 * pad
    hy = y + pad + icon_size + 14
    hf = fit_font(draw, story["headline"], BOLD, headline_size, hw)
    # headline may wrap to at most 2 lines; shrink if it needs 3
    size = hf.size
    while size > 24:
        f = font(BOLD, size)
        if len(wrap(draw, story["headline"], f, hw)) <= 2:
            hf = f
            break
        size -= 1
    hlines = wrap(draw, story["headline"], hf, hw)
    hy = draw_lines(draw, hx, hy, hlines, hf, INK)
    deck_h = (y + h - pad) - (hy + 6)
    df, dlines = fit_deck(draw, story["deck"], hw, deck_h, deck_size)
    draw_lines(draw, hx, hy + 6, dlines, df, MUTED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    draw.rectangle([0, 0, W, 148], fill=NAVY)
    draw.rectangle([0, 144, W, 148], fill=RED)
    f_small = font(BOLD, 26)
    label = "T H E   W O R L D   I N   O N E   D A Y"
    tw = draw.textlength(label, font=f_small)
    draw.text(((W - tw) / 2, 12), label, font=f_small, fill=GOLD)
    f_big = fit_font(draw, "FRIDAY, 13 NOVEMBER 2026", BOLD, 56, W - 40)
    title = "FRIDAY, 13 NOVEMBER 2026"
    tw = draw.textlength(title, font=f_big)
    draw.text(((W - tw) / 2, 44), title, font=f_big, fill=WHITE)
    sub = ("Six stories that defined the day — from Kyiv to Gaza, "
           "Silicon Valley to the Strait of Hormuz")
    f_sub = fit_font(draw, sub, REG, 25, W - 32)
    tw = draw.textlength(sub, font=f_sub)
    draw.text(((W - tw) / 2, 110), sub, font=f_sub, fill=(203, 213, 225))

    stories = [
        {"icon": "chip", "kicker": "LEAD  •  TECH",
         "headline": "NVIDIA CHIEF RESIGNS",
         "deck": "Jensen Huang steps down amid claims of an affair with an "
                 "alleged Chinese spy; shares fall 16%. CFO Colette Kress is "
                 "interim CEO; Congress summons Huang to testify."},
        {"icon": "cloud", "kicker": "TECH",
         "headline": "MICROSOFT GOES DARK",
         "deck": "Outlook and Teams fail around the world in a global "
                 "Microsoft 365 outage."},
        {"icon": "flags", "kicker": "EUROPE",
         "headline": "EUROPE JOINS UKRAINE TALKS",
         "deck": "Russia agrees Europe takes part in the next peace round; "
                 "work begins on the war's largest prisoner exchange."},
        {"icon": "tanker", "kicker": "MIDDLE EAST",
         "headline": "TANKERS HIT IN HORMUZ",
         "deck": "Iran says it destroyed a US radar in Bahrain; an LNG "
                 "tanker hits a mine in the Strait of Hormuz."},
        {"icon": "hospital", "kicker": "MIDDLE EAST",
         "headline": "STRIKE HITS GAZA HOSPITAL",
         "deck": "Israeli missile hits Nasser hospital in Khan Younis; six "
                 "killed, including a surgeon."},
        {"icon": "ball", "kicker": "SPORT",
         "headline": "ENGLAND BEAT CROATIA",
         "deck": "Kane's penalty seals a Wembley win; England reach the "
                 "Nations League quarter-finals."},
    ]

    # ---- lead panel (full width, 156-420) ------------------------------
    panel_side(draw, 24, 156, 976, 264, stories[0],
               icon_size=104, headline_size=46, deck_size=28)

    # ---- row of two (428-684) ------------------------------------------
    y2, h2 = 428, 256
    w2 = (976 - 20) // 2
    panel_stack(draw, 24, y2, w2, h2, stories[1],
                icon_size=64, headline_size=34, deck_size=24)
    panel_stack(draw, 24 + w2 + 20, y2, w2, h2, stories[2],
                icon_size=64, headline_size=34, deck_size=24)

    # ---- row of three (692-964) ----------------------------------------
    y3, h3 = 692, 272
    w3 = (976 - 40) // 3
    for i, st in enumerate(stories[3:]):
        panel_stack(draw, 24 + i * (w3 + 20), y3, w3, h3, st,
                    icon_size=56, headline_size=30, deck_size=22,
                    kicker_size=22)

    # ---- footer ---------------------------------------------------------
    draw.rectangle([0, 968, W, H], fill=NAVY)
    foot = ("Six stories that defined Friday, 13 November 2026  •  "
            "Sources: BBC, Guardian, AP, The New York Times")
    f_foot = fit_font(draw, foot, REG, 24, W - 32)
    tw = draw.textlength(foot, font=f_foot)
    draw.text(((W - tw) / 2, 992), foot, font=f_foot, fill=(203, 213, 225))

    img.save("entry.png", format="PNG", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
