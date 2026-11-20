#!/usr/bin/env python3
"""Render entry.png: one square newspaper front page summing up Friday 20 Nov 2026.

Layout v2: rebalanced section heights so all nine bands fit the 1024px page,
kicker lines no longer collide, stat numerals auto-fit their cells.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

S = 2  # supersample factor: canvas 2048, final 1024
W = 2048

PAPER = (246, 241, 229)
INK = (26, 26, 46)
RED = (179, 53, 44)
GOLD = (185, 138, 47)
PANEL = (239, 231, 211)
HAIR = (138, 127, 99)
REDBAND = (243, 226, 218)
WHITE = (255, 255, 255)

FD = "/usr/share/fonts/truetype/dejavu/"


def F(name, size):
    return ImageFont.truetype(FD + name, int(size * S))


def serif_b(size):
    return F("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return F("DejaVuSerif.ttf", size)


def sans_b(size):
    return F("DejaVuSans-Bold.ttf", size)


def sans(size):
    return F("DejaVuSans.ttf", size)


img = Image.new("RGB", (W, W), PAPER)
d = ImageDraw.Draw(img)


def X(v):
    return v * S


def wrap(text, font, maxw):
    """Wrap text to lines that fit maxw (in final-image px)."""
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=font) <= X(maxw) or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def draw_lines(x, y, lines, font, fill=INK, leading=1.15):
    lh = font.size * leading
    for ln in lines:
        d.text((X(x), X(y)), ln, font=font, fill=fill)
        y += lh / S
    return y


def hline(x0, x1, y, fill=HAIR, wdt=2):
    d.line([X(x0), X(y), X(x1), X(y)], fill=fill, width=max(1, int(wdt * S)))


def spaced(x, y, text, font, fill=INK, tracking=2):
    cx = x
    for ch in text:
        d.text((X(cx), X(y)), ch, font=font, fill=fill)
        cx += (d.textlength(ch, font=font) + X(tracking)) / S
    return cx


def spaced_width(text, font, tracking=2):
    return (sum(d.textlength(c, font=font) for c in text) + X(tracking) * (len(text) - 1)) / S


def spaced_right(xr, y, text, font, fill=INK, tracking=2):
    spaced(xr - spaced_width(text, font, tracking), y, text, font, fill, tracking)


def fit_font(text, name, start, maxw, minimum=14):
    """Largest font (<= start px) whose text fits maxw."""
    size = start
    while size > minimum:
        f = F(name, size)
        if d.textlength(text, font=f) <= X(maxw):
            return f
        size -= 1
    return F(name, minimum)


MX = 56           # page margin
CW = 1024 - 2 * MX  # content width (final px)

# ---------------------------------------------------------------- 1. kicker
kf = sans_b(11)
spaced(MX, 18, "ONE DAY OF WORLD NEWS, ONE PICTURE", kf, INK)
spaced_right(1024 - MX, 18, "51 STORIES · 7 REGIONS · EVERY ONE FROM THIS FRIDAY", kf, RED)
hline(MX, 1024 - MX, 40, INK, 3)
hline(MX, 1024 - MX, 45, HAIR, 1)

# ---------------------------------------------------------------- 2. masthead
mf = serif_b(48)
title = "Friday 20 November 2026"
tw = d.textlength(title, font=mf) / S
d.text((X((1024 - tw) / 2), X(52)), title, font=mf, fill=INK)
hline(MX, 1024 - MX, 108, INK, 3)

# ---------------------------------------------------------------- 3. stat strip
stats = [
    ("298,676", "people evacuated in Odisha before Cyclone Akvan"),
    ("-4.6%", "Nikkei 225, Friday morning in Tokyo"),
    ("-2.02%", "S&P 500 overnight — a sixth straight fall"),
    ("144 → 80", "paragraphs left in the COP31 draft"),
    ("60", "Houthi targets the coalition says it struck"),
    ("2.2%", "Japan core inflation — the year's high"),
]
sy = 116
cellw = CW / 6
lf = sans(10.5)
for i, (num, lab) in enumerate(stats):
    cx = MX + i * cellw
    if i:
        d.line([X(cx), X(sy + 2), X(cx), X(sy + 66)], fill=HAIR, width=S)
    nf = fit_font(num, "DejaVuSerif-Bold.ttf", 25, cellw - 16)
    d.text((X(cx + 10), X(sy)), num, font=nf, fill=RED if i in (1, 2) else INK)
    draw_lines(cx + 10, sy + 36, wrap(lab, lf, cellw - 18), lf, INK, 1.14)
hline(MX, 1024 - MX, 194, HAIR, 1)

# ---------------------------------------------------------------- 4. timeline
ty = 200
d.rectangle([X(MX), X(ty), X(1024 - MX), X(ty + 76)], fill=PANEL)
d.text((X(MX + 12), X(ty + 6)), "THE DAY IN UTC", font=sans_b(11.5), fill=RED)
stops = [
    ("Overnight", "Kyiv hit by four ballistic missiles; Dutch embassy damaged"),
    ("~02:00 UTC", "Cyclone Akvan crosses the coast near Gopalpur"),
    ("Morning", "Asia's AI selloff deepens; China holds its loan rates"),
    ("17:00 UTC", "Trump faces the press at the White House"),
    ("Late", "Wall Street opens after six straight falls"),
]
sw = (CW - 16) / 5
bf, df = sans_b(11.5), sans(10)
d.line([X(MX + 16), X(ty + 33), X(1024 - MX - 16), X(ty + 33)], fill=HAIR, width=S)
for i, (t, txt) in enumerate(stops):
    cx = MX + 8 + i * sw
    d.ellipse([X(cx + 2), X(ty + 29), X(cx + 10), X(ty + 37)], fill=RED)
    d.text((X(cx), X(ty + 16)), t, font=bf, fill=INK)
    draw_lines(cx, ty + 40, wrap(txt, df, sw - 8), df, INK, 1.1)

# ---------------------------------------------------------------- art helpers
def art_storm(x, y, w, h):
    d.rectangle([X(x), X(y), X(x + w), X(y + h)], fill=(214, 224, 230))
    cx, cy = x + w * 0.42, y + h * 0.44
    for r in range(52, 7, -8):
        d.arc([X(cx - r), X(cy - r), X(cx + r), X(cy + r)], 20, 300, fill=(70, 110, 140), width=3 * S)
        d.arc([X(cx - r * 0.7), X(cy - r * 0.7), X(cx + r * 0.7), X(cy + r * 0.7)], 200, 120, fill=(70, 110, 140), width=3 * S)
    d.ellipse([X(cx - 6), X(cy - 6), X(cx + 6), X(cy + 6)], fill=RED)
    pts = [(x, y + h * 0.78), (x + w * 0.3, y + h * 0.7), (x + w * 0.55, y + h * 0.8),
           (x + w * 0.8, y + h * 0.72), (x + w, y + h * 0.82), (x + w, y + h), (x, y + h)]
    d.polygon([(X(px), X(py)) for px, py in pts], fill=(196, 178, 128))
    d.line([(X(px), X(py)) for px, py in pts[:5]], fill=(120, 100, 60), width=2 * S)


def art_chart(x, y, w, h):
    d.rectangle([X(x), X(y), X(x + w), X(y + h)], fill=(250, 240, 238))
    for gy in range(1, 5):
        hline(x + 8, x + w - 8, y + h * gy / 5, (220, 200, 195), 1)
    candles = [(0.16, 0.28), (0.30, 0.40), (0.44, 0.50), (0.58, 0.63), (0.72, 0.76)]
    for fx, fy in candles:
        cxp, cyp = x + w * fx, y + h * fy
        d.line([X(cxp), X(cyp - 12), X(cxp), X(cyp + 20)], fill=RED, width=2 * S)
        d.rectangle([X(cxp - 10), X(cyp - 6), X(cxp + 10), X(cyp + 14)], fill=RED)
    pts = [(x + w * 0.08, y + h * 0.16), (x + w * 0.34, y + h * 0.34), (x + w * 0.6, y + h * 0.52), (x + w * 0.88, y + h * 0.78)]
    d.line([(X(px), X(py)) for px, py in pts], fill=INK, width=2 * S)
    ax_, ay_ = pts[-1]
    d.polygon([(X(ax_), X(ay_)), (X(ax_ - 13), X(ay_ - 2)), (X(ax_ - 3), X(ay_ - 12))], fill=INK)


def art_whitehouse(x, y, w, h):
    d.rectangle([X(x), X(y), X(x + w), X(y + h)], fill=(226, 232, 238))
    bx, by, bw, bh = x + w * 0.16, y + h * 0.36, w * 0.68, h * 0.48
    d.rectangle([X(bx), X(by), X(bx + bw), X(by + bh)], fill=(250, 250, 248), outline=(120, 120, 130), width=S)
    d.polygon([(X(bx - 8), X(by)), (X(bx + bw + 8), X(by)), (X(bx + bw / 2), X(by - h * 0.13))], fill=(250, 250, 248), outline=(120, 120, 130))
    d.rectangle([X(bx + bw / 2 - 9), X(by - h * 0.19), X(bx + bw / 2 + 9), X(by - h * 0.12)], fill=(250, 250, 248), outline=(120, 120, 130), width=S)
    d.line([X(bx + bw / 2), X(by - h * 0.19), X(bx + bw / 2), X(by - h * 0.28)], fill=INK, width=S)
    d.polygon([(X(bx + bw / 2), X(by - h * 0.28)), (X(bx + bw / 2 + 15), X(by - h * 0.245)), (X(bx + bw / 2), X(by - h * 0.21))], fill=RED)
    for i in range(6):
        cxx = bx + bw * (0.1 + i * 0.16)
        d.rectangle([X(cxx), X(by + 5), X(cxx + 6), X(by + bh - 3)], fill=(205, 208, 214))
    d.rectangle([X(bx + bw / 2 - 8), X(by + bh - 24), X(bx + bw / 2 + 8), X(by + bh)], fill=INK)
    for i in range(4):
        wx = bx + bw * (0.14 + i * 0.22)
        d.rectangle([X(wx), X(by + 10), X(wx + 11), X(by + 22)], fill=(150, 170, 190))
    d.rectangle([X(x), X(y + h * 0.88), X(x + w), X(y + h)], fill=(150, 168, 130))


# ---------------------------------------------------------------- 5. hero cards
heroes = [
    ("1", "ODISHA · CYCLONE · TODAY", "Cyclone Akvan crosses the coast near Gopalpur",
     "Akvan crossed the Odisha coast near Gopalpur between 07:30 and 08:30 IST on Friday at 70-80 gusting to 90 km/h, the IMD says; the landfall process continues, with a red warning for extremely heavy rain in Mayurbhanj and Balasore. 298,676 people were evacuated to 2,523 camps and 423 rescue teams deployed.", art_storm),
    ("2", "ASIA-PACIFIC · MARKETS · REPORTED", "AI selloff deepens as Asia's markets slide",
     "The Nikkei fell 4.6% by mid-morning, Seoul's Kospi 4.8% and Taiwan over 6%, with SoftBank down 14% — Asia is heading for its worst week since 2020. Overnight the Nasdaq fell 2.25% after a four-point intraday reversal.", art_chart),
    ("3", "WASHINGTON · POLITICS · TODAY", "Trump faces the press on his Asia trip at noon",
     "The White House news conference, his first since the Shenzhen summit, is set to cover the trip and trade deals with Thailand, the Philippines and others.", art_whitehouse),
]
hy = 284
hw = (CW - 24) / 3
hh = 202
tagf, hf, dkf = sans_b(10.5), serif_b(17), sans(10.5)
for i, (num, tag, head, dek, art) in enumerate(heroes):
    cx = MX + i * (hw + 12)
    d.rectangle([X(cx), X(hy), X(cx + hw), X(hy + hh)], outline=HAIR, width=S)
    art(cx + 8, hy + 8, hw - 16, 70)
    d.ellipse([X(cx + 13), X(hy + 13), X(cx + 37), X(hy + 37)], fill=RED)
    nw = d.textlength(num, font=sans_b(14)) / S
    d.text((X(cx + 25 - nw / 2), X(hy + 16.5)), num, font=sans_b(14), fill=WHITE)
    d.text((X(cx + 12), X(hy + 86)), tag, font=tagf, fill=GOLD)
    yy = draw_lines(cx + 12, hy + 104, wrap(head, hf, hw - 24), hf, INK, 1.12)
    # Heroes 1 and 2 have longer deks; they are set a touch smaller so each
    # stays inside its card.
    hdkf = {"1": sans(8.5), "2": sans(10.0)}.get(num, dkf)
    hlead = {"1": 1.05, "2": 1.12}.get(num, 1.15)
    draw_lines(cx + 12, yy + 3, wrap(dek, hdkf, hw - 24), hdkf, INK, hlead)

# ---------------------------------------------------------------- 6. story grid 4-13
cards = [
    ("4", "EUROPE · UKRAINE WAR", None, "Kyiv hit by four ballistic missiles; embassy damaged",
     "A projectile damaged the Dutch embassy; The Hague summoned Russia's ambassador. In Berlin, Ukraine's allies backed a winter energy ceasefire."),
    ("5", "MIDDLE EAST · CONFLICT", None, "Tanker ablaze after mine strike east of Hormuz",
     "Iran widened attacks on Gulf states and shipping; the IEA calls the conflict the biggest energy-security threat in history. A maritime centre counts four attacks on commercial vessels in 96 hours."),
    ("6", "ASIA · RATES", None, "China leaves its loan rates unchanged",
     "One-year LPR held at 3.0% and five-year at 3.5% for an 18th month; the PBoC's signal is now its 1.25% overnight rate."),
    ("7", "ASIA · INFLATION", None, "Japan's core inflation rises to 2.2%",
     "The year's high, as an energy subsidy expired; markets now look to a December Bank of Japan rate rise."),
    ("8", "YEMEN · WAR", "CLAIM", "Coalition says it struck 60 Houthi targets",
     "It says four ballistic missiles were stopped. The Houthis claim strikes on four Saudi targets, including a Riyadh tower. On Friday the coalition said Saudi air defences intercepted a Houthi ballistic missile over the kingdom's south."),
    ("9", "ANTALYA · CLIMATE", None, "COP31 reaches its final day with no deal in sight",
     "Negotiators hunt a final text by midnight. The draft is cut from 144 paragraphs to 80, the fossil-fuel words are dropped and the $120bn adaptation figure is unresolved. Panama says it may block a deal without a clear transition path."),
    ("10", "ASIA · SECURITY", "REPORTED", "North Korea expanding uranium enrichment",
     "The UN watchdog reports growth at the Yongbyon nuclear site."),
    ("11", "ASIA · HEALTH", None, "India launches its own H5N1 bird-flu vaccine",
     "The first made at home, for poultry, from the ICAR-NIHSAD institute in Bhopal."),
    ("12", "AFRICA · WAR", "REPORTED", "Sudan's army pushes west towards An Nahud",
     "A first sustained advance in central Sudan since 2025; RSF defections grow."),
    ("13", "AMERICAS · CEREMONY", "TODAY", "Sheinbaum leads Mexico's Revolution Day parade",
     "The 116th anniversary of the 1910 revolution, held amid strain with Washington."),
]
gy = hy + hh + 8
gw = (CW - 4 * 10) / 5
gh = 118
ctf, chf, cdf = sans_b(9), serif_b(12), sans(9)
chipf = sans_b(8)
for idx, (num, tag, chip, head, dek) in enumerate(cards):
    r, c = divmod(idx, 5)
    cx, cy = MX + c * (gw + 10), gy + r * (gh + 6)
    d.rectangle([X(cx), X(cy), X(cx + gw), X(cy + gh)], fill=PANEL)
    d.rectangle([X(cx), X(cy), X(cx + 22), X(cy + 22)], fill=INK)
    nw = d.textlength(num, font=sans_b(12)) / S
    d.text((X(cx + 11 - nw / 2), X(cy + 3.5)), num, font=sans_b(12), fill=PAPER)
    d.text((X(cx + 27), X(cy + 5)), tag, font=ctf, fill=RED)
    if chip:
        cwid = d.textlength(chip, font=chipf) / S + 9
        d.rectangle([X(cx + gw - cwid - 5), X(cy + gh - 19), X(cx + gw - 5), X(cy + gh - 4)], fill=GOLD)
        d.text((X(cx + gw - cwid - 0.5), X(cy + gh - 17)), chip, font=chipf, fill=WHITE)
    yy = draw_lines(cx + 7, cy + 27, wrap(head, chf, gw - 14), chf, INK, 1.08)
    # Cards 5, 8 and 9 have extended deks; they are set a touch smaller so
    # each stays inside its card.
    cdkf = sans(8.0) if num in ("5", "8", "9") else cdf
    cdlead = 1.02 if num in ("5", "8", "9") else 1.08
    draw_lines(cx + 7, yy + 2, wrap(dek, cdkf, gw - 14), cdkf, INK, cdlead)

# ---------------------------------------------------------------- 7. bottom band
by = gy + 2 * gh + 6 + 8
bh = 166
mapw = 450
d.rectangle([X(MX), X(by), X(MX + mapw), X(by + bh)], fill=(238, 240, 235), outline=HAIR, width=S)
d.text((X(MX + 12), X(by + 7)), "WHERE IT HAPPENED", font=sans_b(12), fill=INK)
# Simplified low-poly world map: one (lon, lat) polygon per landmass, drawn
# through the same lonlat() projection as the pins so pins stay on their places.
land = [
    # North America (Alaska, Hudson Bay notch, Florida, Central America)
    [(-168, 66), (-168, 60), (-165, 58), (-160, 55), (-155, 56), (-150, 58), (-145, 60), (-140, 61), (-136, 57), (-132, 52), (-128, 48), (-124, 42), (-122, 37), (-118, 33), (-113, 30), (-110, 26), (-107, 22), (-100, 17), (-95, 16), (-91, 14), (-87, 13), (-83, 9), (-79, 9), (-81, 12), (-84, 15), (-87, 16), (-88, 18), (-90, 21), (-94, 19), (-97, 20), (-97, 25), (-94, 29), (-90, 29), (-86, 29), (-82, 28), (-81, 21), (-78, 22), (-79, 27), (-77, 33), (-75, 37), (-74, 40), (-72, 41), (-70, 43), (-66, 45), (-61, 45), (-64, 48), (-68, 50), (-76, 53), (-80, 53), (-83, 56), (-85, 57), (-90, 57), (-94, 58), (-99, 62), (-107, 64), (-114, 65), (-121, 65), (-129, 64), (-137, 65), (-147, 65), (-155, 66), (-161, 64)],
    # Greenland
    [(-46, 60), (-42, 61), (-40, 64), (-36, 67), (-32, 68), (-27, 70), (-22, 70), (-19, 72), (-21, 75), (-25, 78), (-33, 79), (-44, 80), (-54, 78), (-59, 76), (-57, 73), (-54, 69), (-53, 65), (-51, 61)],
    # South America
    [(-79, 9), (-77, 7), (-74, 10), (-71, 12), (-67, 11), (-62, 10), (-57, 7), (-52, 5), (-50, 1), (-46, -1), (-42, -3), (-38, -5), (-35, -8), (-37, -11), (-39, -14), (-40, -19), (-42, -22), (-46, -24), (-49, -28), (-52, -33), (-55, -36), (-58, -39), (-61, -40), (-63, -43), (-65, -46), (-66, -50), (-68, -52), (-68, -55), (-70, -54), (-72, -51), (-73, -46), (-74, -41), (-74, -35), (-72, -30), (-70, -24), (-70, -19), (-74, -15), (-77, -11), (-80, -6), (-81, -2), (-80, 2), (-79, 6)],
    # Africa
    [(-6, 35), (-1, 35), (3, 37), (9, 37), (11, 34), (15, 32), (20, 32), (26, 31), (30, 31), (32, 30), (34, 27), (35, 24), (37, 22), (38, 20), (39, 16), (41, 14), (43, 12), (46, 11), (50, 12), (51, 11), (48, 6), (44, 1), (42, -4), (40, -9), (39, -14), (38, -19), (36, -24), (34, -28), (31, -30), (27, -33), (22, -34), (19, -34), (18, -32), (16, -28), (14, -22), (13, -16), (12, -10), (12, -4), (10, 1), (9, 4), (6, 4), (1, 5), (-3, 5), (-7, 4), (-11, 6), (-13, 8), (-15, 11), (-17, 15), (-17, 19), (-16, 23), (-15, 27), (-13, 30), (-10, 31)],
    # Madagascar
    [(43, -17), (44, -14), (47, -13), (49, -14), (50, -16), (49, -19), (47, -22), (46, -24), (44, -25), (43, -22), (43, -19)],
    # Eurasia: Iberia, Scandinavia, the Italian boot and Greece in the west;
    # Arabia, the India triangle and the Malay peninsula in the south
    [(-9, 37), (-9, 40), (-9, 43), (-6, 44), (-2, 44), (-1, 46), (-4, 48), (-1, 49), (1, 51), (3, 52), (5, 53), (7, 54), (8, 55), (8, 57), (5, 58), (5, 60), (7, 62), (10, 64), (13, 66), (16, 68), (20, 69), (26, 71), (31, 70), (35, 68), (40, 67), (46, 66), (52, 67), (58, 68), (65, 69), (72, 70), (80, 70), (88, 71), (96, 72), (103, 76), (108, 77), (113, 74), (118, 72), (120, 71), (128, 71), (136, 71), (144, 71), (152, 70), (160, 69), (168, 67), (176, 66), (178, 64), (173, 62), (170, 60), (164, 60), (160, 57), (157, 53), (154, 49), (149, 46), (143, 44), (141, 41), (140, 38), (137, 35), (134, 34), (130, 33), (127, 33), (126, 35), (127, 38), (124, 39), (122, 37), (120, 33), (121, 29), (119, 26), (116, 24), (112, 22), (109, 20), (108, 16), (109, 13), (107, 10), (105, 8), (103, 7), (101, 6), (100, 2), (99, 8), (98, 11), (97, 14), (95, 16), (93, 17), (92, 19), (90, 20.9), (88, 20.9), (87, 19.4), (85, 16.3), (83, 13.2), (81, 10.1), (80, 7), (79, 2.3), (78, -0.8), (77, 0.8), (75, 5.4), (73, 10.1), (72, 14.7), (72, 17.8), (70, 20.9), (68, 22.5), (66, 25), (62, 25), (58, 26), (54, 26), (52, 27), (50, 29), (48, 27.4), (49, 24.8), (50, 22.2), (53, 22.2), (55, 22.2), (57, 22.2), (59, 20.9), (59, 19.6), (57, 15.7), (55, 13.1), (53, 11.8), (50, 9.2), (47, 7.9), (45, 6.6), (44, 6.6), (43, 9.2), (42, 11.8), (40, 17), (39, 20.9), (36, 26.1), (35, 28.7), (34, 31), (36, 34), (36, 36), (33, 36), (30, 36), (28, 37), (27, 38), (27, 40), (25, 39), (23, 36), (23, 32), (22, 34), (21, 38), (19, 41), (16, 43), (14, 45), (13, 43), (14, 40), (16, 38), (19, 38), (18, 35), (16, 33), (15, 36), (13, 39), (12, 42), (10, 44), (8, 44), (7, 43), (5, 43), (3, 42), (2, 40), (0, 38), (-1, 36), (-2, 35), (-5, 34), (-7, 35)],
    # Britain
    [(-5, 50), (-3, 50), (-1, 51), (0, 52), (-1, 54), (-2, 56), (-3, 58), (-5, 58), (-6, 56), (-7, 54), (-5, 53), (-5, 51)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (138, 34), (140, 35), (141, 37), (142, 39), (142, 41), (143, 43), (145, 44), (145, 45), (143, 45), (141, 43), (140, 40), (139, 38), (137, 36), (134, 34), (132, 32)],
    # Indonesia: Sumatra, Java, Borneo, Sulawesi, New Guinea; plus the Philippines
    [(95, 5), (97, 3), (99, 1), (101, -1), (103, -3), (105, -5), (106, -6), (104, -5), (101, -2), (99, 0), (97, 2), (95, 4)],
    [(106, -6), (108, -7), (111, -7), (114, -8), (114, -9), (110, -8), (107, -7)],
    [(109, 0), (110, 2), (113, 3), (116, 4), (118, 2), (119, 0), (117, -2), (114, -3), (111, -2), (109, -1)],
    [(119, 0), (120, 1), (121, 1), (120, -1), (120, -3), (119, -2)],
    [(131, -1), (134, -2), (137, -3), (140, -3), (143, -4), (146, -6), (149, -8), (150, -10), (147, -9), (144, -7), (140, -5), (136, -4), (133, -2)],
    [(120, 12), (121, 14), (121, 16), (122, 18), (121, 19), (120, 17), (119, 15), (120, 13)],
    # Australia
    [(113, -22), (113, -26), (114, -30), (115, -33), (117, -35), (120, -34), (124, -33), (128, -32), (131, -32), (133, -32), (135, -34), (136, -35), (137, -35), (138, -36), (139, -37), (141, -38), (144, -38), (146, -39), (148, -38), (150, -37), (152, -33), (153, -29), (153, -26), (152, -25), (150, -22), (148, -20), (146, -19), (144, -16), (143, -13), (142, -11), (142, -13), (141, -16), (140, -18), (138, -17), (136, -15), (136, -13), (135, -12), (133, -11), (131, -12), (129, -13), (126, -14), (124, -16), (122, -17), (120, -19), (117, -20), (114, -21)],
    # New Zealand
    [(167, -45), (169, -44), (171, -43), (173, -42), (174, -40), (175, -38), (177, -37), (175, -37), (173, -39), (172, -41), (170, -43), (168, -45)],
]
mx0, my0, mw, mh = MX + 12, by + 30, mapw - 24, bh - 40


def lonlat(lon, lat):
    return mx0 + (lon + 180) / 360 * mw, my0 + (90 - lat) / 180 * mh


for poly in land:
    d.polygon([(X(lonlat(lo, la)[0]), X(lonlat(lo, la)[1])) for lo, la in poly],
              fill=(214, 208, 188), outline=(188, 179, 152))
dots = [(84.9, 19.3, "1"), (139.7, 35.7, "2"), (-77.0, 38.9, "3"), (30.5, 50.4, "4"),
        (56.5, 26.5, "5"), (116.4, 39.9, "6"), (44.2, 15.4, "8"), (127.0, 37.6, "9"),
        (77.4, 23.3, "11"), (28.4, 12.7, "12"), (-99.1, 19.4, "13")]
def draw_pin(lon, lat, n, number_only=False):
    px, py = lonlat(lon, lat)
    r = 7.5 if len(n) == 1 else 9.5
    fnt = sans_b(8.5 if len(n) == 1 else 7.5)
    if not number_only:
        d.ellipse([X(px - r), X(py - r), X(px + r), X(py + r)], fill=RED, outline=WHITE, width=S)
    else:
        nw = d.textlength(n, font=fnt) / S
        nh = fnt.size / S
        d.text((X(px - nw / 2), X(py - nh / 2 - 0.5)), n, font=fnt, fill=WHITE)


# Discs first, pin 1 last so it sits on top of pin 11 (their centres are only
# ~9px apart); numbers afterwards, pin 1's last, so every number stays visible.
pin_order = [t for t in dots if t[2] != "1"] + [t for t in dots if t[2] == "1"]
for lon, lat, n in pin_order:
    draw_pin(lon, lat, n)
for lon, lat, n in pin_order:
    draw_pin(lon, lat, n, number_only=True)

# right: ALSO ON FRIDAY briefs 14-40, three flowing columns
ax = MX + mapw + 16
aw = 1024 - MX - ax
d.text((X(ax), X(by + 1)), "ALSO ON FRIDAY", font=sans_b(12), fill=INK)
briefs = [
    "EU proposes a 45bn euro joint-debt loan for Ukraine",
    "Putin invites Europe's leaders to Moscow",
    "Macron: the Shenzhen declaration will not reorganise the world",
    "Trump says he will meet Kim Jong-un \"at some point\"",
    "Iraq takes a base in the Jurf al-Sakhar militia stronghold",
    "Migrant boat sinks off Senegal; dozens missing",
    "Genoa airport halts flights over unidentified drones",
    "Toddler pulled from Tbilisi rubble 8 hours after gas blast",
    "One dead, 15 hurt in French apartment-block fire",
    "South Korea's exports pass $1 trillion for the first time",
    "Sensex +1.21% as India defies the selloff",
    "IEA: data-centre power use could double by 2030",
    "COP31 draft drops the fossil-fuel words",
    "New Zealand 317-6 at lunch on day two v India; Nicholls 146*, Phillips out for 118",
    "Modi opens a civilisations forum in Delhi",
    "Merz hosts Qatar's emir in Berlin",
    "Trump announces a posthumous pardon for Pete Rose",
    "Haiti approves Salvadoran troops to fight the gangs",
    "US and Venezuela restore military cooperation",
    "EU-UK summit opens in Brussels",
    "Philippines signs a trade deal with Chile",
    "India's electronics exports jump 44%",
    "EU delays its methane rules by 24 months",
    "Australia beat Argentina 2-0 at the U17 World Cup",
    "World Children's Day is marked around the globe",
    "Amur falcons complete their Arabian Sea crossing",
    "Florida's St. Johns River hits a record 18.3 ft; schools shut in four counties",
    "The US war against Iran has cost $48.3bn, the Pentagon says",
    "Taiwan reports Russian bombers flying east of the island",
    "Jakarta: Indonesia's parliament passes an asset-forfeiture bill",
    "GTA VI's first full day: user scores open, Metacritic 99",
    "California probes Nvidia over China chip risks",
    "Oil eases in Friday dealing: Brent $89.72, WTI $82.83",
    "China-Africa expo opens its second day in Johannesburg",
    "Iowa: the army blows up 68 barrels of unstable explosive at noon",
    "South Australia storm fells two towers; 24,000 properties lose power",
    "Italy hit by a 24-hour general strike; rail stoppage runs into Saturday",
    "Bitcoin slips to $61,503 in Friday trade",
]
bcolw = (aw - 24) / 3
per = (len(briefs) + 2) // 3
chunks = [briefs[i * per:(i + 1) * per] for i in range(3)]


def brief_height(fs, leading, gap):
    """Tallest of the three brief columns (final px) at the given type size."""
    f = sans(fs)
    worst = 0
    for chunk in chunks:
        h = 0
        for btxt in chunk:
            h += len(wrap(btxt, f, bcolw - 15)) * (f.size * leading) / S + gap
        worst = max(worst, h - gap)
    return worst


# Shrink the brief type until all three columns fit inside the band.
bfs, blead, bgap = 6.0, 1.05, 1.5
for fs_try, lead_try, gap_try in ((7.5, 1.05, 2.0), (7.0, 1.05, 1.8), (7.0, 1.03, 1.5),
                                  (6.5, 1.05, 1.5), (6.5, 1.03, 1.2), (6.0, 1.05, 1.5),
                                  (5.5, 1.03, 1.0), (5.25, 1.03, 1.0), (5.0, 1.03, 1.0)):
    if brief_height(fs_try, lead_try, gap_try) <= bh - 28:
        bfs, blead, bgap = fs_try, lead_try, gap_try
        break
bff = sans(bfs)
bnf = sans_b(bfs)
for col, chunk in enumerate(chunks):
    bx = ax + col * (bcolw + 12)
    byy = by + 24
    for j, btxt in enumerate(chunk):
        n = 14 + col * per + j
        d.text((X(bx), X(byy)), f"{n}", font=bnf, fill=RED)
        byy = draw_lines(bx + 15, byy, wrap(btxt, bff, bcolw - 15), bff, INK, blead) + bgap

# ---------------------------------------------------------------- 8. date check
dy = by + bh + 6
d.rectangle([X(MX), X(dy), X(1024 - MX), X(dy + 48)], fill=REDBAND)
dcf = sans(10.5)
dc = ("DATE CHECK — First reported Thursday 19 November, so they are NOT on this page as Friday's news: "
      "the Shenzhen trilateral summit and its peace declaration · the ICJ's genocide ruling on Myanmar · "
      "Anthropic's record market debut · the release of GTA VI · the US Senate's 51-48 Iran war-powers vote · "
      "Denmark's Greenland defence pact · Voyager 1's light-day milestone (18 Nov) · "
      "the acquittal of South Korea's ex-PM Han (19 Nov). Their Friday fallout is covered above.")
draw_lines(MX + 12, dy + 6, wrap(dc, dcf, CW - 24), dcf, INK, 1.15)

# ---------------------------------------------------------------- 9. footer
fy = dy + 48 + 8
hline(MX, 1024 - MX, fy, INK, 2)
ff = sans(9.5)
foot = ("Every story here happened, or was first reported, on Friday 20 November 2026, in some time zone. "
        "CLAIM = one side's account, not independently confirmed. Sources: Reuters, AP, AFP, BBC, Al Jazeera, "
        "The Hindu, IMD. Original drawings.")
draw_lines(MX, fy + 7, wrap(foot, ff, CW - 235), ff, INK, 1.15)
spaced_right(1024 - MX, fy + 7, "FRIDAY 20 NOVEMBER 2026", sans_b(10.5), RED, 2)
spaced_right(1024 - MX, fy + 24, "ONE DAY, ONE PICTURE", sans_b(10.5), INK, 2)

# ---------------------------------------------------------------- downscale + save
final = img.resize((1024, 1024), Image.LANCZOS)
final.save(OUT, optimize=True)
size = os.path.getsize(OUT)
if size > 1_048_576:
    q = final.quantize(colors=256, method=Image.MEDIANCUT)
    q.save(OUT, optimize=True)
    size = os.path.getsize(OUT)
print(f"entry.png: {final.size[0]}x{final.size[1]} px, {size} bytes")
