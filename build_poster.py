#!/usr/bin/env python3
"""Build the entry image (v3): a one-page newspaper front page summing up the
world news of Monday 23 November 2026 — 37 stories, 7 regions, and every one
of the 37 stories illustrated.

The composition follows the classic broadsheet front-page skeleton — black
masthead bar, giant serif date, red italic deck, KPI strip, colour region
tabs, a UTC timeline, three hero cards with rich flat scenes, twelve medium
cards with mini-scenes, a dark dotted world map whose red pins match the
card numbers, a numbered ALSO list in which every item also carries a small
drawn thumbnail, a red DATE CHECK box, and a certainty legend. The layout
system is modelled on the previous day's winning front page; every scene,
headline and line of text here is original work for Monday's news. Every
fact printed comes from the reporting listed in ../SOURCES.md (Reuters, AP,
BBC, AFP, Fox News, Guardian, NHS England, Kyodo, ABC, cricket.com.au, Bank
of Ghana — all read on 23 November 2026).

All artwork is drawn here with Pillow primitives: no photographs, no
downloaded assets, no external files besides system fonts.

Run:  python3 build_poster.py   ->  writes entry.png next to this file
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (247, 243, 234)
INK = (18, 18, 20)
GREY = (96, 92, 84)
CAPGREY = (74, 68, 60)
HAIR = (150, 144, 130)
RED = (164, 32, 28)
NAVYBAR = (15, 25, 46)
MAPNAVY = (14, 26, 54)
MAPDOT = (148, 172, 216)
WHITE = (250, 248, 242)
GOLD = (243, 197, 105)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, width):
    """Greedy word wrap measured with PIL; returns list of lines."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, path, size, width, max_lines, min_size=7):
    """Shrink font until the wrapped text fits max_lines. Returns (font, lines)."""
    while size > min_size:
        f = F(path, size)
        lines = wrap(draw, text, f, width)
        if len(lines) <= max_lines:
            return f, lines
        size -= 1
    f = F(path, min_size)
    return f, wrap(draw, text, f, width)[:max_lines]


def banner(draw, x, y, s, size=11, h=20):
    """Red ribbon flush with the art's top-left corner (hero cards)."""
    f = F(SANS_B, size)
    w = int(draw.textlength(s, font=f)) + 16
    draw.rectangle([x, y, x + w, y + h], fill=RED)
    draw.text((x + 8, y + h // 2), s, font=f, fill=WHITE, anchor="lm")
    return w


def banner_s(draw, x, y, s):
    """Smaller red ribbon for medium cards / thumbnails."""
    f = F(SANS_B, 8)
    w = int(draw.textlength(s, font=f)) + 10
    draw.rectangle([x, y, x + w, y + 14], fill=RED)
    draw.text((x + 5, y + 7), s, font=f, fill=WHITE, anchor="lm")
    return w


def callout(draw, x, y, s, colour=WHITE, size=12):
    """Bold stat text sitting directly on the art, top-right."""
    draw.text((x, y + 3), s, font=F(SANS_B, size), fill=colour, anchor="ra")


def num_tag(draw, x, y, n):
    """Small dark square with the story number, bottom-left of the art."""
    draw.rectangle([x, y, x + 15, y + 15], fill=INK)
    draw.text((x + 7.5, y + 7), str(n), font=F(SANS_B, 9), fill=WHITE, anchor="mm")


# ---------------------------------------------------------------- stories
# (num, region, kicker, status, headline, body, source) — content unchanged
# from v2 (hero bodies tightened by a few words to fit the denser page).
HEROES = [
    (1, "World", "ANTALYA, TÜRKIYE · CLIMATE", "REPORTED",
     "COP31 ends without a deal as the text ducks fossil fuels",
     "The EU, Panama and the Marshall Islands refused a cover decision that "
     "never mentioned fossil fuels. Nearly 200 countries talked some 48 hours "
     "into overtime; up to 90 signed the \u201c35 by 35\u201d electrification pledge.",
     "Reuters"),
    (2, "Europe", "DYMER, KYIV REGION · WAR", "REPORTED",
     "Russian strikes kill at least 11 in the Kyiv region",
     "A five-storey block in Dymer partly collapsed in a night strike; the "
     "dead include a teenager. Rescuers still search for 11 people, two of "
     "them children; a boy of seven was pulled out alive. Strikes also hit "
     "Vyshneve and Bila Tserkva.",
     "Reuters, AP"),
    (3, "Europe", "OFF LIBYA · WAR AT SEA", "CLAIM",
     "Ukraine says seven naval drones sank Russia\u2019s corvette Merkury",
     "Zelenskyy says Ukrainian-made naval drones sank one of Russia\u2019s newest "
     "warships, commissioned in 2023, and also hit the cargo ship MV Angara, "
     "which Kyiv says carried weapons. Moscow has not confirmed the loss.",
     "Reuters \u2014 Kyiv\u2019s account"),
]

MEDIUMS = [
    (4, "Americas", "WASHINGTON · US POLITICS", "REPORTED",
     "Democrats take 258 House seats, their most since 1992",
     "The 258th seat: Hubbard beats Foxx in North Carolina after a recount. "
     "Four races still uncalled.", "AP, Reuters"),
    (5, "Middle East", "WASHINGTON · IRAN", "REPORTED",
     "Trump leans to striking Iran after the New Year",
     "No deal, no patience: he warns blockade-testing ships will be sunk. "
     "Talks remain stalled.", "Fox News"),
    (6, "Middle East", "RABIGH, SAUDI ARABIA · ENERGY", "CLAIM",
     "Houthis claim a direct hit on the Rabigh refinery",
     "Riyadh stays silent; the coalition says it intercepted a missile "
     "bound for the coast.", "Reuters"),
    (7, "Asia-Pacific", "CIKANDE, INDONESIA · FIRE", "REPORTED",
     "Factory fire kills 24; about 30 still missing",
     "The blaze tore through a Banten confectionery plant; some 300 people "
     "were on the shift.", "Reuters"),
    (8, "Asia-Pacific", "TAIPEI · MARKETS", "REPORTED",
     "Taiwan eases margin rules; stocks bounce 2.1%",
     "After a \u221217.5% week, brokers cut the margin floor to 120% from "
     "Tuesday.", "Reuters"),
    (9, "World", "NEW YORK · MARKETS", "REPORTED",
     "Hedge funds lose 3%+ in the AI selloff",
     "Their worst week since April 2025; Nvidia fell 23% in five days and "
     "the Nasdaq 10%.", "Reuters"),
    (10, "Europe", "LONDON · EUROPE DEAL", "REPORTED",
     "Burnham: EU deal is our biggest growth measure",
     "He claims +0.5% of GDP, some \u00a317bn; Badenoch calls the gain "
     "0.0%.", "BBC"),
    (11, "Europe", "CAMBRIDGE · HEALTH", "REPORTED",
     "First women join the AI breast-screening trial",
     "EDITH: 700,000 women at 30 sites, with AI reading scans as a second "
     "pair of eyes.", "NHS, BBC"),
    (12, "Europe", "BERLIN · ECONOMY", "REPORTED",
     "German factories hit a 56-month high",
     "Flash composite PMI 55.0, up from 53.4 \u2014 the best reading since "
     "March 2022.", "Reuters"),
    (13, "Africa", "KHARTOUM, SUDAN · WAR", "REPORTED",
     "Drone strikes hit Khartoum and a UN compound",
     "Four killed, including a child; the first UN site hit since the army "
     "retook the capital.", "AFP"),
    (14, "Africa", "KADUNA, NIGERIA · RESCUE", "REPORTED",
     "Army rescues 18 of 22 abducted brigade children",
     "Taken during a Sunday walk in Kachia; four children are still being "
     "sought.", "Wires"),
    (15, "Oceania", "WELLINGTON · CRICKET", "REPORTED",
     "Black Caps hold India to a draw",
     "NZ 5-239, still 113 behind India\u2019s 720 declared; India slip to "
     "fourth in the WTC.", "cricket.com.au"),
]

ALSO = [
    (16, "Asia-Pacific", "Prabowo names two VP candidates; parliament picks on 11 Dec (Reuters)"),
    (17, "Asia-Pacific", "India\u2019s factories hum: flash PMI 56.3, manufacturing at a nine-month high (Reuters)"),
    (18, "Asia-Pacific", "S. Korea\u2019s education minister quits over the exam-cheating-measures chaos (Reuters)"),
    (19, "Asia-Pacific", "Seoul repeats its market-stabilisation pledge after the Kospi\u2019s \u22128% week (Reuters)"),
    (20, "Asia-Pacific", "China\u2019s exchanges ease margin rules over the weekend (Reuters)"),
    (21, "Asia-Pacific", "Japan\u2019s markets shut for Labour Thanksgiving Day (Wires)"),
    (22, "Asia-Pacific", "Japan\u2019s education minister Seki apologises over an aide scandal (Kyodo)"),
    (23, "Europe", "Spain votes Sunday in a snap election; polls put PP+Vox near 190\u2013200 seats (Guardian)"),
    (24, "Europe", "Price beats Van Veen 16\u201311 to win darts\u2019 Grand Slam (BBC Sport)"),
    (25, "Europe", "Manchester\u2019s Co-op Live evacuated over a \u201csmell of gas\u201d; no leak found (BBC)"),
    (26, "Europe", "Liverpool rout Man Utd 4\u20130 in Pochettino\u2019s first match in charge (Reuters)"),
    (27, "Africa", "Ghana opens a buyback of up to GH\u00a228.6bn of 2027 bonds (Bank of Ghana)"),
    (28, "Africa", "The rand firms ~1% as gold recovers from a 14-month low (Reuters)"),
    (29, "Africa", "Rain delays the Centurion Test toss; Bavuma out injured (Reuters)"),
    (30, "Oceania", "Chalmers warns unemployment could rise above 5% (Guardian)"),
    (31, "Oceania", "Australian shares slide again; the NZX 50 falls 1% early (Reuters)"),
    (32, "Oceania", "Australia beat France in the Billie Jean King Cup (ABC)"),
    (33, "Middle East", "IDF intel warned Netanyahu: an Iran strike could ignite three fronts (Channel 12)"),
    (34, "Middle East", "Iran labels the Royal Navy and RAF terrorist organisations (AP)"),
    (35, "Americas", "US futures bounce: Nasdaq +2% after the worst week since 2020 (Reuters)"),
    (36, "Americas", "NFL Sunday: Lions, Bills and Chiefs win; 49ers rout Vikings in Mexico City (Reuters)"),
    (37, "World", "Chess: Gukesh (20) defends his title vs Sindarov (20), Geneva, from Tuesday (Reuters)"),
]

REGION_ORDER = ["EUROPE", "MIDDLE EAST", "AMERICAS", "ASIA-PACIFIC",
                "AFRICA", "OCEANIA", "WORLD"]
REGION_COLOUR = {"EUROPE": (18, 92, 86), "MIDDLE EAST": (150, 44, 32),
                 "AMERICAS": (176, 124, 32), "ASIA-PACIFIC": (178, 84, 28),
                 "AFRICA": (44, 110, 58), "OCEANIA": (96, 62, 140),
                 "WORLD": (24, 44, 84)}
REGION_KEY = {"Europe": "EUROPE", "Middle East": "MIDDLE EAST",
              "Americas": "AMERICAS", "Asia-Pacific": "ASIA-PACIFIC",
              "Africa": "AFRICA", "Oceania": "OCEANIA", "World": "WORLD"}

KPIS = [
    ("258", "US House seats won by the Democrats \u2014 the most since 1992"),
    ("90", "countries sign COP31\u2019s \u201c35 by 35\u201d electrification pledge"),
    ("24", "killed in the Banten factory fire; about 30 still missing"),
    ("11", "killed in the Kyiv-region strikes; 11 more still missing"),
    ("7", "Ukrainian naval drones in the Merkury attack (Kyiv\u2019s account)"),
    ("\u221223%", "Nvidia\u2019s week in the AI selloff; the Nasdaq fell 10%"),
]

TIMELINE = [
    ("00:00", "Khartoum explosions"),
    ("05:05", "India PMI lands"),
    ("06:50", "Rand firms ~1%"),
    ("07:30", "AI screening trial opens"),
    ("09:00", "Ghana buyback opens"),
    ("ALL DAY", "COP31 fallout"),
]


# ---------------------------------------------------------------- artwork
def bands(d, box, cols):
    """Horizontal colour bands filling box (a flat sky/sea)."""
    x, y, w, h = box
    n = len(cols)
    for i, c in enumerate(cols):
        d.rectangle([x, y + h * i // n, x + w, y + h * (i + 1) // n], fill=c)


def ill_cop31(d, box):
    """The summit table: pale sky, green globe, a row of delegates, a clock."""
    x, y, w, h = box
    bands(d, box, [(186, 214, 226), (198, 224, 232), (208, 230, 234)])
    # globe, cropped by the top-left corner
    gx, gy, gr = x + 48, y + 14, 44
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(52, 128, 92))
    d.ellipse([gx - 30, gy - 26, gx - 6, gy - 6], fill=(88, 164, 116))
    d.ellipse([gx + 2, gy + 2, gx + 30, gy + 24], fill=(88, 164, 116))
    d.ellipse([gx - 36, gy + 10, gx - 14, gy + 28], fill=(88, 164, 116))
    # wall clock, right side, clear of the delegates
    cx, cy, cr = x + w - 28, y + 36, 15
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], outline=(30, 34, 44), width=3)
    d.line([cx, cy, cx, cy - 9], fill=(30, 34, 44), width=2)
    d.line([cx, cy, cx + 7, cy + 3], fill=(30, 34, 44), width=2)
    # delegates: heads and shoulders behind the long table
    skin = [(232, 190, 160), (160, 110, 80), (240, 205, 175), (120, 84, 60),
            (215, 170, 135), (90, 62, 45), (238, 198, 168), (175, 125, 92),
            (205, 160, 125)]
    cloth = [(70, 90, 140), (140, 60, 55), (60, 110, 85), (110, 85, 130),
             (80, 80, 90), (150, 110, 60), (95, 120, 150), (120, 70, 90),
             (70, 130, 120)]
    base = y + h
    table_y = base - 26
    for i in range(9):
        fx = x + 26 + i * 29
        d.pieslice([fx - 13, table_y - 24, fx + 13, table_y + 4], 180, 360,
                   fill=cloth[i])
        d.ellipse([fx - 6, table_y - 36, fx + 6, table_y - 24], fill=skin[i])
    d.rectangle([x + 8, table_y, x + w - 8, table_y + 7], fill=(146, 104, 58))
    d.rectangle([x + 8, table_y + 7, x + w - 8, base], fill=(110, 76, 42))
    # papers and a gavel on the table
    for i in range(4):
        px = x + 52 + i * 62
        d.rectangle([px, table_y - 3, px + 20, table_y + 1], fill=(244, 242, 234))
    d.rectangle([x + w - 66, table_y - 6, x + w - 52, table_y - 2], fill=(70, 48, 26))


def drone(d, cx, cy, s=8, col=(238, 196, 92)):
    """A small quadcopter silhouette: crossed arms, four rotors, body."""
    d.line([cx - s, cy - s, cx + s, cy + s], fill=col, width=2)
    d.line([cx - s, cy + s, cx + s, cy - s], fill=col, width=2)
    for dx, dy in ((-s, -s), (s, -s), (-s, s), (s, s)):
        d.ellipse([cx + dx - 2, cy + dy - 2, cx + dx + 2, cy + dy + 2], fill=col)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=col)


def ill_kyiv(d, box):
    """Night strike: drones and a searchlight over a burning, broken block."""
    x, y, w, h = box
    bands(d, box, [(9, 14, 36), (13, 22, 50), (18, 30, 60)])
    for i in range(34):  # deterministic stars
        sx = x + (i * 61) % w
        sy = y + (i * 23) % int(h * 0.42)
        d.point((sx, sy), fill=(205, 212, 232))
    base = y + h
    sil = (20, 24, 38)
    d.rectangle([x, base - 22, x + 40, base], fill=sil)  # low block, far left
    # main five-storey block, intact left part
    bx, bw = x + 118, 104
    d.rectangle([bx, base - 78, bx + bw, base], fill=sil)
    for r in range(5):
        for c in range(5):
            wx, wy = bx + 8 + c * 19, base - 71 + r * 14
            lit = (r * 7 + c * 3) % 4 != 0
            d.rectangle([wx, wy, wx + 10, wy + 8],
                        fill=GOLD if lit else (50, 58, 82))
    # collapsed right section: pancaked slabs, rubble, fire, dust
    slab = (58, 62, 80)
    for i in range(4):
        sx0 = bx + bw - 10 + i * 6
        sy0 = base - 68 + i * 13
        d.polygon([(sx0, sy0), (sx0 + 56 - i * 5, sy0 + 5),
                   (sx0 + 52 - i * 5, sy0 + 12), (sx0 - 2, sy0 + 7)], fill=slab)
        d.line([sx0, sy0, sx0 + 56 - i * 5, sy0 + 5], fill=(150, 156, 178), width=1)
    d.polygon([(bx + bw - 8, base), (bx + bw + 48, base - 9), (bx + bw + 72, base)],
              fill=(42, 44, 58))
    d.ellipse([bx + bw + 8, base - 14, bx + bw + 34, base - 3], fill=(198, 84, 38))
    d.ellipse([bx + bw + 14, base - 11, bx + bw + 28, base - 4], fill=(246, 182, 88))
    d.ellipse([bx + bw - 16, base - 82, bx + bw + 28, base - 66], fill=(74, 82, 106))
    d.ellipse([bx + bw + 6, base - 86, bx + bw + 50, base - 72], fill=(64, 72, 96))
    # searchlight beam sweeping up from the left
    d.polygon([(x + 8, base), (bx + 22, base - 70), (bx + 38, base - 62),
               (x + 22, base)], fill=(44, 60, 100))
    # drones crossing the sky
    for cx, cy, s in ((52, 24, 8), (98, 42, 6), (170, 16, 7), (238, 36, 6),
                      (284, 30, 7)):
        drone(d, x + cx, y + cy, s)


def ill_merkury(d, box):
    """Seven naval drones close on the corvette under a moonlit sea."""
    x, y, w, h = box
    bands(d, (x, y, w, int(h * 0.44)), [(13, 26, 54), (18, 34, 66)])
    bands(d, (x, y + int(h * 0.44), w, h - int(h * 0.44)),
          [(12, 58, 76), (10, 50, 68), (9, 43, 60), (8, 37, 53)])
    d.ellipse([x + w - 52, y + 26, x + w - 30, y + 48], fill=(232, 230, 214))  # moon
    sil = (8, 12, 22)
    sx, sy = x + int(w * 0.40), y + int(h * 0.40)  # the corvette
    d.polygon([(sx, sy + 18), (sx + 168, sy + 18), (sx + 150, sy + 33),
               (sx + 16, sy + 33)], fill=sil)
    d.rectangle([sx + 34, sy + 4, sx + 104, sy + 18], fill=sil)
    d.rectangle([sx + 58, sy - 14, sx + 65, sy + 4], fill=sil)    # mast
    d.line([sx + 61, sy - 14, sx + 88, sy - 14], fill=sil, width=3)  # radar bar
    d.rectangle([sx + 108, sy - 4, sx + 132, sy + 18], fill=sil)  # funnel block
    d.rectangle([sx + 18, sy + 10, sx + 30, sy + 18], fill=sil)   # bow gun
    for i in range(4):  # lit portholes
        d.rectangle([sx + 44 + i * 26, sy + 23, sx + 50 + i * 26, sy + 27],
                    fill=(240, 200, 110))
    # impact flash at the bow where a drone has struck
    fx, fy = sx + 8, sy + 22
    pts = []
    for i in range(10):
        a = i * math.pi / 5
        r = 13 if i % 2 == 0 else 5
        pts.append((fx + r * math.cos(a), fy + r * math.sin(a)))
    d.polygon(pts, fill=(246, 170, 70))
    d.ellipse([fx - 4, fy - 4, fx + 4, fy + 4], fill=(252, 226, 150))
    # the seven naval drones, in two loose arcs, wakes streaming behind
    spots = [(16, 52), (44, 66), (74, 54), (100, 70), (30, 82), (64, 86),
             (96, 88)]
    for dx, dy in spots:
        px, py = x + dx, y + dy
        d.polygon([(px, py), (px + 20, py + 4), (px + 3, py + 9)], fill=(5, 9, 16))
        d.line([px - 14, py + 3, px, py + 4], fill=(130, 178, 196), width=1)
        d.line([px - 10, py + 7, px + 1, py + 6], fill=(110, 160, 182), width=1)
    for i in range(10):  # wave ticks
        wx = x + (i * 67) % w
        wy = y + int(h * 0.60) + (i * 19) % int(h * 0.32)
        d.line([wx, wy, wx + 13, wy], fill=(54, 106, 126), width=2)


def ill_generic(d, box, kind):
    """Small flat scenes for the medium cards (154x38 strips)."""
    x, y, w, h = box
    if kind == "capitol":
        bands(d, box, [(22, 42, 82), (28, 52, 96)])
        cx = x + w // 2
        d.pieslice([cx - 24, y + 2, cx + 24, y + 34], 180, 360, fill=(233, 231, 221))
        d.rectangle([cx - 3, y + 0, cx + 3, y + 6], fill=(233, 231, 221))
        d.rectangle([cx - 34, y + 20, cx + 34, y + 24], fill=(233, 231, 221))
        d.rectangle([cx - 52, y + 24, cx - 34, y + 30], fill=(214, 212, 202))
        d.rectangle([cx + 34, y + 24, cx + 52, y + 30], fill=(214, 212, 202))
        for i in range(7):
            d.line([cx - 27 + i * 9, y + 24, cx - 27 + i * 9, y + 34],
                   fill=(233, 231, 221), width=2)
        d.rectangle([x, y + h - 3, x + w, y + h], fill=(16, 28, 54))
    elif kind == "missile":
        bands(d, box, [(110, 48, 38), (188, 98, 50), (222, 146, 68)])
        d.ellipse([x + 8, y + 8, x + 30, y + 30], fill=(246, 200, 110))
        d.rectangle([x, y + h - 8, x + w, y + h], fill=(40, 26, 24))
        d.arc([x + 26, y - 20, x + 138, y + 40], 300, 25, fill=(250, 246, 238), width=2)
        # the missile itself, nose down-range at the end of the arc
        d.polygon([(x + 118, y + 4), (x + 136, y + 12), (x + 128, y + 20),
                   (x + 112, y + 12)], fill=(238, 236, 228))
        d.polygon([(x + 118, y + 4), (x + 112, y + 12), (x + 128, y + 20),
                   (x + 124, y + 10)], fill=(198, 60, 44))
        d.polygon([(x + 112, y + 12), (x + 104, y + 6), (x + 106, y + 16)],
                  fill=(246, 170, 70))
    elif kind == "refinery":
        bands(d, box, [(24, 24, 32), (32, 30, 38)])
        for tx in (x + 40, x + 76, x + 110):
            d.rectangle([tx, y + 12, tx + 11, y + h], fill=(72, 72, 84))
            d.polygon([(tx + 5, y + 0), (tx, y + 11), (tx + 11, y + 11)],
                      fill=(240, 130, 40))
            d.polygon([(tx + 3, y + 11), (tx + 5, y + 5), (tx + 8, y + 11)],
                      fill=(250, 200, 100))
        d.pieslice([x + 122, y + 22, x + 148, y + 42], 180, 360, fill=(72, 72, 84))
        d.line([x + 14, y + 28, x + 140, y + 28], fill=(90, 90, 104), width=3)
        d.line([x + 14, y + 33, x + 140, y + 33], fill=(90, 90, 104), width=2)
    elif kind == "fire":
        bands(d, box, [(38, 22, 20), (50, 27, 22)])
        d.rectangle([x + 18, y + 18, x + 122, y + h], fill=(22, 18, 18))
        d.polygon([(x + 18, y + 18), (x + 32, y + 11), (x + 46, y + 18),
                   (x + 60, y + 11), (x + 74, y + 18), (x + 88, y + 11),
                   (x + 102, y + 18), (x + 122, y + 18)], fill=(22, 18, 18))
        for fx in range(x + 26, x + 118, 13):
            d.polygon([(fx, y + 20), (fx + 5, y + 3), (fx + 10, y + 20)],
                      fill=(238, 120, 36))
            d.polygon([(fx + 3, y + 20), (fx + 5, y + 10), (fx + 7, y + 20)],
                      fill=(248, 196, 84))
        d.ellipse([x + 92, y + 0, x + 116, y + 9], fill=(112, 106, 102))
        d.ellipse([x + 106, y - 2, x + 138, y + 8], fill=(94, 90, 88))
    elif kind in ("chart_up", "chart_down"):
        bands(d, box, [(17, 27, 48), (21, 33, 58)])
        for gy in (y + 10, y + 20, y + 30):
            d.line([x + 6, gy, x + w - 6, gy], fill=(44, 58, 88), width=1)
        if kind == "chart_up":
            pts = [(x + 8, y + 28), (x + 42, y + 31), (x + 74, y + 22),
                   (x + 104, y + 25), (x + 134, y + 9)]
            col = (84, 190, 110)
        else:
            pts = [(x + 8, y + 8), (x + 42, y + 12), (x + 74, y + 11),
                   (x + 104, y + 22), (x + 134, y + 30)]
            col = (232, 84, 70)
        d.line(pts, fill=col, width=2)
        ex, ey = pts[-1]
        d.polygon([(ex + 6, ey), (ex - 4, ey - 2),
                   (ex + 1, ey + (7 if kind == "chart_down" else -7))], fill=col)
    elif kind == "eu":
        bands(d, box, [(21, 43, 94), (25, 51, 106)])
        cx, cy = x + 32, y + 19
        for i in range(12):
            a = i * math.pi / 6
            d.ellipse([cx + 12 * math.cos(a) - 1.8, cy + 12 * math.sin(a) - 1.8,
                       cx + 12 * math.cos(a) + 1.8, cy + 12 * math.sin(a) + 1.8],
                      fill=(244, 200, 84))
        d.polygon([(x + 84, y + 8), (x + 112, y + 2), (x + 140, y + 8)],
                  fill=(233, 231, 221))
        d.rectangle([x + 84, y + 10, x + 140, y + 13], fill=(233, 231, 221))
        for i in range(5):
            d.line([x + 88 + i * 12, y + 13, x + 88 + i * 12, y + 30],
                   fill=(233, 231, 221), width=2)
        d.rectangle([x + 82, y + 30, x + 142, y + 33], fill=(233, 231, 221))
    elif kind == "health":
        bands(d, box, [(13, 82, 78), (15, 94, 90)])
        d.rectangle([x + 34, y + 6, x + 96, y + 32], outline=(230, 240, 236), width=2)
        d.line([(x + 40, y + 19), (x + 52, y + 19), (x + 58, y + 10),
                (x + 65, y + 28), (x + 71, y + 19), (x + 90, y + 19)],
               fill=(240, 250, 246), width=2)
        d.rectangle([x + 116, y + 11, x + 122, y + 27], fill=(238, 120, 130))
        d.rectangle([x + 111, y + 16, x + 127, y + 22], fill=(238, 120, 130))
        d.ellipse([x + 12, y + 14, x + 20, y + 22], fill=(240, 250, 246))
    elif kind == "factory":
        bands(d, box, [(50, 60, 76), (60, 70, 86)])
        d.polygon([(x + 12, y + h), (x + 12, y + 20), (x + 26, y + 27),
                   (x + 40, y + 20), (x + 40, y + h)], fill=(25, 29, 39))
        d.rectangle([x + 48, y + 9, x + 55, y + h], fill=(25, 29, 39))
        d.ellipse([x + 44, y + 1, x + 60, y + 8], fill=(200, 204, 210))
        for i, bh in enumerate((10, 16, 24)):
            d.rectangle([x + 88 + i * 19, y + h - 4 - bh, x + 101 + i * 19, y + h - 4],
                        fill=(84, 180, 104))
        d.line([x + 84, y + h - 4, x + 146, y + h - 4], fill=(210, 214, 220), width=1)
    elif kind == "khartoum":
        bands(d, box, [(28, 32, 62), (116, 60, 50), (210, 118, 54)])
        d.rectangle([x + 14, y + 20, x + 66, y + h], fill=(21, 21, 31))
        d.rectangle([x + 82, y + 16, x + 132, y + h], fill=(21, 21, 31))
        d.rectangle([x + 100, y + 5, x + 103, y + 16], fill=(21, 21, 31))
        d.rectangle([x + 103, y + 5, x + 120, y + 13], fill=(125, 178, 224))
        d.ellipse([x + 108, y + 6, x + 114, y + 12], outline=(250, 250, 250), width=1)
        for dx, dy in ((x + 36, y + 17), (x + 60, y + 20), (x + 124, y + 18)):
            drone(d, dx, dy, 4, col=(14, 14, 22))
    elif kind == "rescue":
        bands(d, box, [(28, 82, 46), (36, 102, 56)])
        d.ellipse([x + 120, y + 3, x + 140, y + 23], fill=(246, 205, 105))
        d.polygon([(x, y + h), (x + 58, y + 20), (x + 112, y + h)], fill=(22, 60, 34))
        d.polygon([(x + 60, y + h), (x + 116, y + 24), (x + w, y + h)], fill=(26, 70, 40))
        for i, fx in enumerate((x + 28, x + 44, x + 60, x + 76, x + 92)):
            d.ellipse([fx, y + 14, fx + 6, y + 20], fill=(250, 244, 230))
            d.line([fx + 3, y + 20, fx + 3, y + 29], fill=(250, 244, 230), width=2)
    elif kind == "cricket":
        bands(d, box, [(32, 108, 54), (38, 122, 60)])
        d.rectangle([x + 56, y + 4, x + 98, y + 34], fill=(228, 210, 170))
        for sx in (x + 62, x + 88):
            for k in range(3):
                d.line([sx + k * 4, y + 9, sx + k * 4, y + 20], fill=(244, 240, 224), width=1)
        d.ellipse([x + 108, y + 20, x + 115, y + 27], fill=(198, 40, 40))
        d.line([x + 40, y + 28, x + 54, y + 10], fill=(120, 84, 40), width=3)
        d.ellipse([x + 36, y + 24, x + 42, y + 30], fill=(30, 40, 90))


MED_ART = {4: "capitol", 5: "missile", 6: "refinery", 7: "fire", 8: "chart_up",
           9: "chart_down", 10: "eu", 11: "health", 12: "factory",
           13: "khartoum", 14: "rescue", 15: "cricket"}
MED_TAG = {4: "258 SEATS", 5: "AFTER NEW YEAR", 6: "CLAIM: DIRECT HIT",
           7: "24 DEAD", 8: "+2.1% MONDAY", 9: "\u22123% WEEK",
           10: "\u00a317BN CLAIM", 11: "700,000 WOMEN", 12: "55.0 \u00b7 56-MO HIGH",
           13: "UN PREMISES HIT", 14: "18 RESCUED", 15: "DRAWN"}

# ------------------------------------------- ALSO thumbnails (48x18 each)
def thumb(d, box, kind):
    x, y, w, h = box
    if kind == "vp":  # two candidates side by side
        bands(d, box, [(24, 40, 78), (30, 50, 92)])
        for cx, col in ((x + 16, (90, 120, 170)), (x + 32, (150, 90, 80))):
            d.ellipse([cx - 4, y + 3, cx + 4, y + 11], fill=(238, 205, 175))
            d.pieslice([cx - 7, y + 9, cx + 7, y + 21], 180, 360, fill=col)
    elif kind == "factory":
        bands(d, box, [(52, 62, 78), (62, 72, 88)])
        d.polygon([(x + 4, y + 18), (x + 4, y + 9), (x + 11, y + 13),
                   (x + 18, y + 9), (x + 18, y + 18)], fill=(22, 26, 36))
        d.rectangle([x + 24, y + 4, x + 28, y + 18], fill=(22, 26, 36))
        for i, bh in enumerate((5, 8, 11)):
            d.rectangle([x + 34 + i * 5, y + 17 - bh, x + 37 + i * 5, y + 17],
                        fill=(84, 180, 104))
    elif kind == "book":  # education: an open book
        bands(d, box, [(16, 84, 80), (18, 96, 90)])
        d.polygon([(x + 24, y + 4), (x + 10, y + 2), (x + 10, y + 14),
                   (x + 24, y + 16)], fill=(244, 242, 232))
        d.polygon([(x + 24, y + 4), (x + 38, y + 2), (x + 38, y + 14),
                   (x + 24, y + 16)], fill=(232, 230, 218))
        d.line([x + 24, y + 4, x + 24, y + 16], fill=(150, 60, 50), width=1)
    elif kind == "chart_dn_flat":  # Kospi: down, then flat
        bands(d, box, [(18, 28, 50), (22, 34, 60)])
        d.line([(x + 4, y + 4), (x + 18, y + 12), (x + 30, y + 12),
                (x + 44, y + 12)], fill=(232, 84, 70), width=2)
    elif kind == "coin":  # China margin easing: coins and a rising arrow
        bands(d, box, [(104, 40, 36), (118, 48, 40)])
        d.ellipse([x + 6, y + 4, x + 20, y + 18 - 4], outline=(246, 200, 84), width=2)
        d.ellipse([x + 12, y + 8, x + 26, y + 18], outline=(246, 200, 84), width=2)
        d.line([(x + 30, y + 14), (x + 38, y + 8), (x + 44, y + 4)],
               fill=(250, 246, 238), width=2)
        d.polygon([(x + 44, y + 4), (x + 38, y + 4), (x + 43, y + 9)],
                  fill=(250, 246, 238))
    elif kind == "gate":  # Japan shut: a gate, closed for the holiday
        bands(d, box, [(56, 58, 70), (66, 68, 80)])
        d.rectangle([x + 8, y + 3, x + 40, y + 6], fill=(214, 208, 196))
        d.rectangle([x + 12, y + 6, x + 16, y + 17], fill=(214, 208, 196))
        d.rectangle([x + 32, y + 6, x + 36, y + 17], fill=(214, 208, 196))
        d.line([x + 16, y + 11, x + 32, y + 11], fill=(150, 60, 50), width=2)
    elif kind == "podium":  # an apology at the microphones
        bands(d, box, [(40, 50, 80), (48, 60, 94)])
        d.polygon([(x + 16, y + 18), (x + 20, y + 10), (x + 28, y + 10),
                   (x + 32, y + 18)], fill=(120, 84, 46))
        d.ellipse([x + 20, y + 2, x + 28, y + 10], fill=(238, 205, 175))
        d.line([x + 30, y + 4, x + 34, y + 9], fill=(230, 232, 236), width=1)
        d.ellipse([x + 33, y + 2, x + 37, y + 6], fill=(230, 232, 236))
    elif kind == "ballot":  # Spain votes: box and ballot
        bands(d, box, [(140, 44, 34), (154, 52, 38)])
        d.rectangle([x + 12, y + 10, x + 36, y + 17], fill=(240, 238, 230))
        d.rectangle([x + 18, y + 11, x + 30, y + 13], fill=(40, 40, 44))
        d.polygon([(x + 20, y + 1), (x + 29, y + 3), (x + 27, y + 11),
                   (x + 18, y + 9)], fill=(250, 248, 240))
        d.line([x + 21, y + 6, x + 24, y + 9], fill=(30, 120, 70), width=1)
        d.line([x + 24, y + 9, x + 28, y + 4], fill=(30, 120, 70), width=1)
    elif kind == "darts":
        bands(d, box, [(22, 58, 38), (26, 68, 44)])
        cx, cy = x + 18, y + 9
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(238, 234, 222))
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(30, 30, 34))
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(196, 40, 40))
        d.line([cx + 2, cy - 2, x + 42, y + 2], fill=(220, 224, 230), width=1)
        d.polygon([(x + 42, y + 2), (x + 38, y + 1), (x + 41, y + 5)],
                  fill=(240, 160, 60))
    elif kind == "arena":  # Co-op Live: domed arena, wavy "smell of gas"
        bands(d, box, [(50, 60, 76), (58, 70, 86)])
        d.pieslice([x + 8, y + 6, x + 40, y + 24], 180, 360, fill=(24, 28, 38))
        d.rectangle([x + 8, y + 14, x + 40, y + 17], fill=(24, 28, 38))
        for wx in (x + 14, x + 24, x + 34):
            d.arc([wx, y - 2, wx + 6, y + 5], 270, 90, fill=(170, 220, 190), width=1)
    elif kind == "football":
        bands(d, box, [(32, 106, 52), (36, 118, 58)])
        d.rectangle([x + 4, y + 3, x + 44, y + 15], outline=(240, 244, 238), width=1)
        d.line([x + 24, y + 3, x + 24, y + 15], fill=(240, 244, 238), width=1)
        d.ellipse([x + 20, y + 6, x + 28, y + 12], outline=(240, 244, 238), width=1)
        d.ellipse([x + 33, y + 5, x + 39, y + 11], fill=(250, 250, 248))
    elif kind == "bank":  # Ghana buyback: a bank front
        bands(d, box, [(86, 66, 18), (98, 76, 22)])
        d.polygon([(x + 8, y + 5), (x + 24, y + 1), (x + 40, y + 5)],
                  fill=(244, 238, 224))
        d.rectangle([x + 8, y + 6, x + 40, y + 8], fill=(244, 238, 224))
        for i in range(4):
            d.line([x + 12 + i * 8, y + 8, x + 12 + i * 8, y + 15],
                   fill=(244, 238, 224), width=2)
        d.rectangle([x + 7, y + 15, x + 41, y + 17], fill=(244, 238, 224))
    elif kind == "chart_up_gold":  # the rand firms on gold
        bands(d, box, [(18, 66, 42), (22, 78, 50)])
        d.line([(x + 4, y + 14), (x + 16, y + 12), (x + 28, y + 7),
                (x + 42, y + 4)], fill=(246, 200, 84), width=2)
        d.polygon([(x + 42, y + 4), (x + 36, y + 4), (x + 41, y + 9)],
                  fill=(246, 200, 84))
    elif kind == "rain":  # Centurion: cloud, rain, a pitch below
        bands(d, box, [(66, 80, 100), (76, 92, 112)])
        d.ellipse([x + 10, y + 1, x + 30, y + 8], fill=(196, 202, 212))
        d.ellipse([x + 20, y + 0, x + 38, y + 7], fill=(178, 186, 200))
        for rx in (x + 14, x + 22, x + 30):
            d.line([rx, y + 9, rx - 2, y + 13], fill=(170, 205, 235), width=1)
        d.rectangle([x + 8, y + 15, x + 40, y + 17], fill=(226, 208, 168))
    elif kind == "briefcase":  # unemployment warning
        bands(d, box, [(80, 60, 28), (92, 70, 34)])
        d.rectangle([x + 10, y + 6, x + 32, y + 16], fill=(150, 104, 54))
        d.rectangle([x + 17, y + 3, x + 25, y + 7], outline=(226, 200, 150), width=2)
        d.line([x + 10, y + 11, x + 32, y + 11], fill=(110, 76, 38), width=1)
        d.polygon([(x + 41, y + 5), (x + 36, y + 14), (x + 46, y + 14)],
                  outline=(250, 220, 120), width=1)
        d.text((x + 41, y + 8), "!", font=F(SANS_B, 7), fill=(250, 220, 120),
               anchor="ma")
    elif kind == "chart_dn":  # Australian shares slide
        bands(d, box, [(18, 28, 50), (22, 34, 60)])
        d.line([(x + 4, y + 4), (x + 16, y + 7), (x + 28, y + 8),
                (x + 42, y + 14)], fill=(232, 84, 70), width=2)
        d.polygon([(x + 42, y + 14), (x + 36, y + 13), (x + 41, y + 8)],
                  fill=(232, 84, 70))
    elif kind == "tennis":
        bands(d, box, [(28, 88, 118), (32, 100, 132)])
        d.ellipse([x + 8, y + 4, x + 22, y + 16], outline=(240, 244, 238), width=1)
        d.line([x + 20, y + 14, x + 28, y + 18], fill=(240, 244, 238), width=2)
        d.ellipse([x + 32, y + 3, x + 40, y + 11], fill=(206, 226, 80))
        d.arc([x + 32, y + 3, x + 40, y + 11], 90, 270, fill=(250, 250, 240), width=1)
    elif kind == "eye":  # intelligence warning: the watching eye
        bands(d, box, [(28, 32, 62), (34, 38, 72)])
        d.polygon([(x + 6, y + 9), (x + 16, y + 3), (x + 32, y + 3),
                   (x + 42, y + 9), (x + 32, y + 15), (x + 16, y + 15)],
                  outline=(236, 240, 248), width=1)
        d.ellipse([x + 19, y + 4, x + 29, y + 14], outline=(236, 240, 248), width=1)
        d.ellipse([x + 22, y + 7, x + 26, y + 11], fill=(240, 130, 60))
    elif kind == "shipflag":  # Royal Navy labelled: a warship and flag
        bands(d, box, [(14, 38, 68), (17, 46, 80)])
        d.rectangle([x + 4, y + 13, x + 44, y + 16], fill=(10, 16, 28))
        d.rectangle([x + 16, y + 9, x + 28, y + 13], fill=(10, 16, 28))
        d.line([x + 36, y + 3, x + 36, y + 13], fill=(230, 232, 236), width=1)
        d.polygon([(x + 36, y + 3), (x + 44, y + 5), (x + 36, y + 7)],
                  fill=(196, 40, 40))
        d.line([x + 6, y + 17, x + 42, y + 17], fill=(90, 150, 180), width=1)
    elif kind == "chart_up":  # US futures bounce
        bands(d, box, [(18, 28, 50), (22, 34, 60)])
        d.line([(x + 4, y + 14), (x + 16, y + 13), (x + 28, y + 8),
                (x + 42, y + 3)], fill=(84, 190, 110), width=2)
        d.polygon([(x + 42, y + 3), (x + 36, y + 3), (x + 41, y + 8)],
                  fill=(84, 190, 110))
    elif kind == "nfl":
        bands(d, box, [(96, 54, 28), (108, 62, 32)])
        d.ellipse([x + 10, y + 4, x + 38, y + 15], fill=(166, 96, 48))
        d.arc([x + 10, y + 4, x + 38, y + 15], 0, 360, fill=(240, 230, 210), width=1)
        d.line([x + 20, y + 9, x + 28, y + 9], fill=(250, 246, 238), width=1)
        for lx in (x + 22, x + 25):
            d.line([lx, y + 7, lx, y + 11], fill=(250, 246, 238), width=1)
    elif kind == "knight":  # the chess title match
        bands(d, box, [(38, 38, 46), (46, 46, 56)])
        for i in range(6):
            for j in range(2):
                if (i + j) % 2 == 0:
                    d.rectangle([x + 2 + i * 4, y + 10 + j * 4,
                                 x + 6 + i * 4, y + 14 + j * 4], fill=(70, 70, 82))
        pts = [(x + 30, y + 16), (x + 30, y + 10), (x + 33, y + 6),
               (x + 31, y + 3), (x + 35, y + 2), (x + 40, y + 6),
               (x + 38, y + 8), (x + 41, y + 11), (x + 38, y + 12),
               (x + 37, y + 16)]
        d.polygon(pts, fill=(238, 232, 216))
        d.rectangle([x + 28, y + 16, x + 42, y + 18], fill=(238, 232, 216))


ALSO_ART = {16: "vp", 17: "factory", 18: "book", 19: "chart_dn_flat",
            20: "coin", 21: "gate", 22: "podium", 23: "ballot", 24: "darts",
            25: "arena", 26: "football", 27: "bank", 28: "chart_up_gold",
            29: "rain", 30: "briefcase", 31: "chart_dn", 32: "tennis",
            33: "eye", 34: "shipflag", 35: "chart_up", 36: "nfl",
            37: "knight"}

# ------------------------------------------------------------- dotted map
LAND = [  # crude continent boxes in (lon_min, lon_max, lat_min, lat_max)
    (-168, -95, 50, 72), (-125, -66, 30, 50), (-118, -86, 14, 32), (-85, -75, 7, 12),
    (-80, -60, 5, 12), (-78, -58, -8, 5), (-70, -50, -22, -8), (-73, -55, -38, -22),
    (-72, -64, -54, -38),
    (-10, 30, 43, 60), (4, 31, 58, 70), (-9, 3, 36, 44), (-5, 2, 50, 59), (30, 45, 60, 68),
    (-17, 35, 15, 32), (-10, 40, 4, 15), (8, 36, -6, 4), (12, 33, -18, -6),
    (19, 33, -27, -18), (25, 33, -34, -27), (43, 50, -25, -13),
    (35, 60, 12, 42), (44, 76, 35, 50), (60, 100, 48, 70), (100, 180, 45, 72),
    (76, 100, 20, 35), (68, 76, 35, 45), (95, 110, 5, 28), (100, 126, 20, 42),
    (126, 142, 30, 46), (129, 146, 31, 46), (95, 120, 5, -8), (120, 141, -2, -10),
    (141, 150, -3, -9), (48, 60, 42, 52),
    (113, 129, -22, -35), (129, 141, -25, -38), (141, 150, -28, -39), (146, 153, -19, -27),
    (167, 178, -46, -34),
]
PINS = {1: (30.7, 36.9), 2: (30.5, 50.4), 3: (19.0, 33.5), 4: (-88.0, 32.0),
        5: (51.4, 35.7), 6: (39.0, 22.6), 7: (106.4, -6.2), 8: (121.6, 25.0),
        9: (-74.0, 40.7), 10: (-0.5, 51.3), 11: (4.2, 53.9), 12: (13.4, 52.5),
        13: (32.5, 15.5), 14: (7.4, 10.5), 15: (169.0, -41.3)}


def draw_map(d, box):
    x, y, w, h = box
    d.rectangle([x, y, x + w, y + h], fill=MAPNAVY)
    step = 5
    for py in range(y + 3, y + h - 2, step):
        lat = 82 - (py - y) / h * 142
        for px in range(x + 3, x + w - 2, step):
            lon = -180 + (px - x) / w * 360
            if any(a <= lon <= b and c <= lat <= dd for a, b, c, dd in LAND):
                d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=MAPDOT)
    for n, (lon, lat) in PINS.items():
        px = x + (lon + 180) / 360 * w
        py = y + (82 - lat) / 142 * h
        r = 8
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED, outline=WHITE, width=1)
        f = F(SANS_B, 9 if n < 10 else 8)
        d.text((px, py - 1), str(n), font=f, fill=WHITE, anchor="mm")


# ---------------------------------------------------------------- layout
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)


def paste_art(fn, x, y, w, h, *args):
    """Render an illustration into its own tile and paste it, so no stroke
    can spill outside its box onto neighbouring furniture."""
    tile = Image.new("RGB", (w, h), PAPER)
    td = ImageDraw.Draw(tile)
    fn(td, (0, 0, w, h), *args)
    img.paste(tile, (x, y))


M = 26
CW = W - 2 * M  # 972

counts = {}
for _, region, *_ in HEROES + MEDIUMS:
    counts[REGION_KEY[region]] = counts.get(REGION_KEY[region], 0) + 1
for _, region, _ in ALSO:
    counts[REGION_KEY[region]] = counts.get(REGION_KEY[region], 0) + 1
TOTAL = sum(counts.values())

# masthead bar
d.rectangle([0, 0, W, 28], fill=NAVYBAR)
d.text((14, 7), "THE WORLD IN ONE DAY", font=F(SANS_B, 13), fill=WHITE)
d.text((W - 14, 8), f"{TOTAL} STORIES · 7 REGIONS · EVERY ONE DATED MONDAY 23 NOVEMBER 2026",
       font=F(SANS_B, 11), fill=WHITE, anchor="ra")

# giant date + red deck
d.text((W // 2, 34), "Monday 23 November 2026", font=F(SERIF_B, 58), fill=INK, anchor="ma")
deck = ("COP31 ends with no deal \u00b7 Kyiv-region strikes kill 11 \u00b7 "
        "Ukraine says its drones sank a Russian corvette")
d.text((W // 2, 100), deck, font=F(SERIF_I, 16), fill=RED, anchor="ma")

# KPI strip
KY = 122
d.line([M, KY, W - M, KY], fill=INK, width=2)
cell = CW / 6
for i, (num, label) in enumerate(KPIS):
    cx = M + i * cell
    if i:
        d.line([cx, KY + 6, cx, KY + 48], fill=HAIR, width=1)
    nf, _ = fit_lines(d, num, SERIF_B, 29, cell - 8, 1)
    d.text((cx + cell / 2, KY + 5), num, font=nf, fill=INK, anchor="ma")
    lf = F(SANS, 8)
    for j, line in enumerate(wrap(d, label, lf, cell - 10)[:2]):
        d.text((cx + cell / 2, KY + 38 + j * 10), line, font=lf, fill=CAPGREY, anchor="ma")

# region tabs
TY = 180
seg = CW / 7
for i, name in enumerate(REGION_ORDER):
    x0 = M + int(i * seg)
    x1 = M + int((i + 1) * seg)
    d.rectangle([x0, TY, x1, TY + 22], fill=REGION_COLOUR[name])
    d.text(((x0 + x1) / 2, TY + 5), f"{name} {counts.get(name, 0)}",
           font=F(SANS_B, 11), fill=WHITE, anchor="ma")

# timeline strip
LY = 208
d.rectangle([M, LY, W - M, LY + 22], fill=NAVYBAR)
d.text((M + 10, LY + 5), "THE DAY IN UTC", font=F(SANS_B, 10), fill=WHITE)
slot = (CW - 140) / 6
for i, (t, label) in enumerate(TIMELINE):
    ex = M + 140 + i * slot
    tf = F(SANS_B, 9)
    d.text((ex, LY + 6), t, font=tf, fill=(250, 246, 238))
    tw = d.textlength(t, font=tf)
    lf, lines = fit_lines(d, label, SANS, 9, slot - tw - 14, 1, min_size=8)
    d.text((ex + tw + 5, LY + 6), lines[0], font=lf, fill=(216, 212, 200))

# hero cards
HY = 238
HW = 316
HERO_ART_H = 90
HERO_CHIPS = {1: ("SUMMIT ENDS", "NO FOSSIL FUELS", INK),
              2: ("NIGHT STRIKES", "11 KILLED", WHITE),
              3: ("SEVEN NAVAL DRONES", "KYIV\u2019S ACCOUNT", WHITE)}
HERO_ART = {1: ill_cop31, 2: ill_kyiv, 3: ill_merkury}
hero_bottom = HY
for i, (num, region, kicker, status, head, body, src) in enumerate(HEROES):
    x = M + i * (HW + 12)
    paste_art(HERO_ART[num], x, HY, HW, HERO_ART_H)
    lt, rt, rc = HERO_CHIPS[num]
    banner(d, x, HY, lt)
    callout(d, x + HW - 8, HY, rt, colour=rc)
    num_tag(d, x, HY + HERO_ART_H - 15, num)
    ky = HY + HERO_ART_H + 6
    d.text((x, ky), f"{num}  {kicker}", font=F(SANS_B, 10), fill=RED)
    sf = F(SANS_B, 9)
    sw = d.textlength(status, font=sf)
    d.rectangle([x + HW - sw - 13, ky + 2, x + HW - sw - 6, ky + 9], fill=RED)
    d.text((x + HW, ky + 1), status, font=sf, fill=RED, anchor="ra")
    hf, hlines = fit_lines(d, head, SERIF_B, 20, HW, 2, min_size=15)
    yy = ky + 16
    for line in hlines:
        d.text((x, yy), line, font=hf, fill=INK)
        yy += hf.size + 3
    bf, blines = fit_lines(d, body + f" ({src})", SERIF, 10, HW, 4, min_size=9)
    yy += 2
    for line in blines:
        d.text((x, yy), line, font=bf, fill=INK)
        yy += 12
    hero_bottom = max(hero_bottom, yy)

# medium cards: 2 rows x 6
MED_Y = hero_bottom + 12
d.line([M, MED_Y - 6, W - M, MED_Y - 6], fill=HAIR, width=1)
MW = 154
MED_ART_H = 38
for i, (num, region, kicker, status, head, body, src) in enumerate(MEDIUMS):
    x = int(M + (i % 6) * (MW + 9.6))
    y = MED_Y + (i // 6) * 106
    paste_art(ill_generic, x, y, MW, MED_ART_H, MED_ART[num])
    banner_s(d, x, y, MED_TAG[num])
    num_tag(d, x, y + MED_ART_H - 15, num)
    d.text((x, y + MED_ART_H + 4), f"{num}  {kicker}", font=F(SANS_B, 7), fill=RED)
    hf, hlines = fit_lines(d, head, SERIF_B, 13, MW, 2, min_size=9)
    yy = y + MED_ART_H + 15
    for line in hlines:
        d.text((x, yy), line, font=hf, fill=INK)
        yy += hf.size + 2
    bf, blines = fit_lines(d, body + f" ({src})", SERIF, 8, MW, 2, min_size=7)
    yy += 1
    for line in blines:
        d.text((x, yy), line, font=bf, fill=INK)
        yy += 10
med_bottom = MED_Y + 2 * 106

# bottom section: dark map (left) + ALSO list with thumbnails (right)
BY = med_bottom + 10
d.line([M, BY - 5, W - M, BY - 5], fill=HAIR, width=1)
d.text((M, BY), "WHERE IT HAPPENED", font=F(SERIF_B, 13), fill=INK)
d.text((M + 172, BY + 3), "pins match story numbers", font=F(SANS_I, 8), fill=GREY)
paste_art(draw_map, M, BY + 18, 322, 158)
d.text((M, BY + 182), "Schematic dotted map, drawn in code. Stories 16\u201337 are listed",
       font=F(SANS, 7), fill=GREY)
d.text((M, BY + 191), "at right, each with its own thumbnail; the map pins cards 1\u201315.",
       font=F(SANS, 7), fill=GREY)

AX = 364
d.text((AX, BY), f"ALSO ON MONDAY 23 NOVEMBER \u2014 {len(ALSO)} MORE STORIES",
       font=F(SERIF_B, 13), fill=INK)
col_w = 316
col_x = [AX, AX + col_w + 14]
THUMB_W, THUMB_H = 48, 18
lf = F(SANS, 8)
items = []
for num, region, txt in ALSO:
    lines = wrap(d, f"{num} {region}: {txt}", lf, col_w - THUMB_W - 8)
    items.append((num, lines, max(THUMB_H, len(lines) * 9 + 2)))
heights = [it[2] + 1 for it in items]
total_h = sum(heights)
split, acc, best = 1, 0, None
for i in range(1, len(items)):
    acc += heights[i - 1]
    score = max(acc, total_h - acc)
    if best is None or score < best:
        best, split = score, i
also_bottom = BY + 18
for ci, part in enumerate((items[:split], items[split:])):
    yy = BY + 18
    for num, lines, ih in part:
        paste_art(thumb, col_x[ci], yy, THUMB_W, THUMB_H, ALSO_ART[num])
        for j, line in enumerate(lines):
            d.text((col_x[ci] + THUMB_W + 8, yy + j * 9), line, font=lf, fill=INK)
        yy += ih + 1
    also_bottom = max(also_bottom, yy)
    if yy > 940:
        print("WARNING: ALSO column", ci, "overflows to y =", yy)

# DATE CHECK box
DY = 946
d.rectangle([M, DY, W - M, DY + 26], outline=RED, width=2)
d.text((M + 10, DY + 8), "DATE CHECK", font=F(SANS_B, 10), fill=RED)
dc = ("Left out as other days\u2019 news: the Bayelsa funeral-boat capsize (Fri 20 Nov) \u00b7 "
      "Mexico\u2019s capture of \u201cEl Chapo Isidro\u201d (announced Sat 21 Nov) \u00b7 the Nikkei\u2019s \u22125% "
      "plunge (Friday\u2019s close \u2014 Tokyo was shut today). Not dated Monday, not on this page.")
df = F(SERIF, 8)
dx = M + 96
for j, line in enumerate(wrap(d, dc, df, W - M - dx - 8)[:2]):
    d.text((dx, DY + 4 + j * 10), line, font=df, fill=INK)

# footer
d.text((W // 2, 978),
       "Sources: Reuters, AP, BBC, AFP, Al Jazeera, Fox News, The Guardian, NHS England, Kyodo, "
       "cricket.com.au, ABC, Bank of Ghana \u2014 reporting read on Monday 23 November 2026.",
       font=F(SANS, 7), fill=GREY, anchor="ma")
d.text((W // 2, 987),
       "CERTAINTY \u2014 REPORTED = carried by the day\u2019s wires \u00b7 CLAIM = one side\u2019s account, labelled as such \u00b7 "
       "FORECAST = still to happen when drawn. Pictures and map are original illustrations, not photographs.",
       font=F(SANS, 7), fill=INK, anchor="ma")

# bottom bar
d.rectangle([0, 998, W, H], fill=NAVYBAR)
d.text((14, 1005), "THE WORLD IN ONE DAY", font=F(SANS_B, 11), fill=WHITE)
d.text((W - 14, 1005), "MONDAY 23 NOVEMBER 2026 \u00b7 ONE PAGE", font=F(SANS_B, 11),
       fill=WHITE, anchor="ra")

img.save(os.path.join(HERE, "entry.png"), optimize=True)
print("wrote entry.png", img.size, os.path.getsize(os.path.join(HERE, "entry.png")), "bytes")
print("stories:", TOTAL, counts)
print("hero_bottom:", hero_bottom, "med_bottom:", med_bottom, "also_bottom:", also_bottom)
