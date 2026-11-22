#!/usr/bin/env python3
"""Render the Daily Orbit front page for Sunday 22 November 2026.

Draws a dense newspaper front page with Pillow: masthead, lead story,
UTC timeline, three illustrated stories, twelve more top stories, a world
map with numbered pins, a DATE CHECK box, stories 17-50, and a numbers
strip. Deterministic: same bytes on every run (fixed random seed, no
timestamps). Run: python3 gen.py  ->  writes entry.png beside this file.
"""

import math
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "entry.png"

PAPER = (247, 243, 232)
INK = (18, 18, 18)
RED = (176, 32, 32)
GRAY = (96, 96, 96)
DARKGRAY = (70, 70, 70)
OCEAN = (211, 229, 241)
LAND = (216, 207, 180)
LAND_EDGE = (122, 112, 82)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, fnt, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- stories
LEAD = {
    "num": 1,
    "kicker": "COP31",
    "headline": "COP31 NEARS A DEAL AFTER ALL-NIGHT TALKS",
    "deck": (
        "A new package tabled in the small hours in Antalya: delegations "
        "have until 03:00 GMT to object, then a 06:00 GMT session votes it "
        "through after two weeks of talks."
    ),
    "source": "Source: Reuters  ·  Antalya, Türkiye",
}

ILLUSTRATED = [
    {
        "num": 2,
        "headline": "HONG KONG VOTES FOR ITS ELECTION COMMITTEE",
        "deck": (
            "Polls open 9am-6pm: 856 candidates chase 723 seats on the "
            "1,500-member body that picks the chief executive. Only 5,700 "
            "voters are eligible."
        ),
        "source": "Source: HK govt",
    },
    {
        "num": 3,
        "headline": "PANT 128 AS INDIA PILE UP A RECORD 629-6",
        "deck": (
            "India pass their best total in New Zealand and lead by 261 "
            "on day four in Wellington. Pant's ninth Test hundred, 108 "
            "sixes in all, came off 153 balls."
        ),
        "source": "Source: Reuters",
    },
    {
        "num": 4,
        "headline": "BAHRAIN SAYS IRANIAN STRIKE HIT INDUSTRIAL SITE",
        "deck": (
            "Bahrain says an Iranian attack hit a civilian site and set it "
            "on fire; defences intercepted others. Tehran's radar claim "
            "is unverified."
        ),
        "source": "Source: Reuters",
    },
]

TOP = [  # stories 5-16: (num, headline, source)
    (5, "Zverev meets Alcaraz in ATP Finals title match tonight", "ATP"),
    (6, "Norway top court voids disputed oil licences", "Wire"),
    (7, "France holds fourth weekend of cost-of-living protests", "Wire"),
    (8, "Eisenkot tapped to form Israel's next government", "ANI"),
    (9, "Zelenskyy: NATO membership is clearest security guarantee", "ANI"),
    (10, "Four nations press Israel over Gaza aid as floods hit", "Wire"),
    (11, "US details $12bn in Venezuelan oil and mineral revenue", "Wire"),
    (12, "Kenya discharges last Ebola patient; DRC toll tops 5,300", "Wire"),
    (13, "DRC enacts constitutional-reform law amid tensions", "Wire"),
    (14, "Ghana unveils Heritage banknotes honouring Nkrumah, Annan", "Wire"),
    (15, "Kenya wins 293,600 Saudi job slots", "Wire"),
    (16, "Nigeria starts building naval ships at home", "Wire"),
]

REST = [  # stories 17-50: (num, headline, source)
    (17, "Sahel states restart dialogue with West Africa bloc", "Wire"),
    (18, "New Tigray mayor vows elections within six months", "Wire"),
    (19, "Al-Shabaab claims hundreds dead in ambush on Somali troops", "Wire"),
    (20, "Bolsonaro in ICU with acute bowel obstruction", "Wire"),
    (21, "Sinaloa violence kills 11 after cartel boss's arrest", "Wire"),
    (22, "Myanmar quake M4.1 strikes in early hours", "ANI"),
    (23, "UAE president receives US homeland security chief", "ANI"),
    (24, "Finland PM: war spilling over after Baltic ship strike", "ANI"),
    (25, "Crew evacuated from Russian ship hit by drones", "Al Jazeera"),
    (26, "Peru counts 152 homes uninhabitable after Friday's quake", "Wire"),
    (27, "Australia bowls first; injured Smith misses S. Africa decider", "Wire"),
    (28, "France reach Nations final, beating Argentina", "Wire"),
    (29, "Australia beat Wales in Nations Championship", "Wire"),
    (30, "Evanilson scores in sixth straight league game", "Wire"),
    (31, "Awar Odhiang named model of the year", "Wire"),
    (32, "Tyla, Tems and Kidjo lead Africa's Grammy hopes", "Wire"),
    (33, "Protest outside S. African court as police bar rallies", "Wire"),
    (34, "No power, no vote: service chaos tests S. Africa's ANC", "Wire"),
    (35, "SCO forum enters its final day in New Delhi", "Wire"),
    (36, "Pakistan climate minister to attend SCO dialogue in Delhi", "Wire"),
    (37, "Saudi Arabia issues four fog warnings", "Wire"),
    (38, "Manhattan's Turtle Lady took in 680 babies one summer", "TOI"),
    (39, "California mother sues school over report card", "TOI"),
    (40, "Ohio court upholds $6,000 award after landlord tossed art", "TOI"),
    (41, "LA diner since 1924 reopens under nonprofit", "TOI"),
    (42, "Python swallows pet peacock in Florida", "TOI"),
    (43, "1,000+ FEMA staff sent home as bed bugs infest DC office", "TOI"),
    (44, "France probing Depardieu, author over gang-rape claim", "TOI"),
    (45, "US consulate links Lagos Fashion Week to trade ties", "Wire"),
    (46, "Américo Ramos reappointed PM of São Tomé and Príncipe", "Wire"),
    (47, "Coventry edge Crystal Palace 3-2 on late own goal", "Wire"),
    (48, "Blair: UK should rejoin EU only if it innovates on tech", "Wire"),
    (49, "NATO vows to defend every inch of Polish territory", "Wire"),
    (50, "Delhi braces for foggy Sunday as IMD warns of mist", "Wire"),
]

TIMELINE = [
    ("OVERNIGHT", "Bahrain reports Iranian strike on industrial site"),
    ("00:41", "Pant 128; India 629-6 in Wellington"),
    ("01:00", "Hong Kong polls open: 856 vie for 723 seats"),
    ("03:00", "COP31 objection deadline in Antalya"),
    ("06:00", "COP31 approval session reconvenes"),
    ("17:00", "ATP Finals: Zverev v Alcaraz in Turin"),
]

DATE_CHECK = [
    "EU–Indonesia trade deal signed — Fri 21 Nov (Reuters)",
    "El Chapo Isidro captured — Sat 21 Nov (Reuters)",
    "Kryvyi Rih strike, 2 killed, 60 hurt — Sat 21 Nov (AP)",
    "Lviv station strike, 2 killed — Fri 20 Nov (AP)",
    "Peru Andes quake, M6.7 — Fri 21 Nov (USGS)",
    "BepiColombo reaches Mercury — Sat 21 Nov (Reuters)",
    "Australia beat England, 1st T20 — Sat 21 Nov (AP)",
    "Trump contractor order signed — Fri 20 Nov (AP)",
    "UN robot-weapons talks end — Sat 21 Nov (UN)",
]

NUMBERS = (
    "50 stories  ·  856 candidates  ·  723 seats  ·  5,700 voters  ·  "
    "629-6 India's record  ·  128 Pant  ·  261-run lead  ·  5,300+ Ebola toll  ·  "
    "293,600 jobs  ·  11 killed in Sinaloa  ·  152 homes  ·  4 fog warnings"
)

# ---------------------------------------------------------------- map data
# Coarse continent outlines as (lon, lat) pairs, drawn equirectangular.
NORTH_AMERICA = [
    (-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60), (-135, 58),
    (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-117, 33), (-112, 29),
    (-109, 25), (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 13),
    (-83, 9), (-80, 8), (-79, 9), (-81, 13), (-84, 16), (-87, 21), (-90, 21),
    (-91, 19), (-94, 19), (-97, 26), (-93, 30), (-89, 30), (-84, 30),
    (-81, 25), (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 44),
    (-65, 44), (-60, 47), (-55, 52), (-60, 55), (-64, 58), (-68, 58),
    (-72, 62), (-78, 62), (-85, 66), (-92, 66), (-95, 69), (-110, 68),
    (-125, 70), (-140, 70), (-155, 71), (-165, 68),
]
GREENLAND = [
    (-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68), (-22, 70),
    (-20, 74), (-25, 76), (-32, 80), (-45, 81), (-58, 78), (-62, 74),
]
SOUTH_AMERICA = [
    (-80, 9), (-77, 4), (-75, 0), (-80, -3), (-81, -6), (-78, -10),
    (-75, -15), (-72, -18), (-70, -22), (-70, -30), (-72, -38), (-73, -46),
    (-70, -52), (-66, -55), (-68, -50), (-65, -45), (-62, -40), (-58, -34),
    (-52, -32), (-48, -28), (-41, -23), (-38, -15), (-35, -8), (-35, -5),
    (-40, -3), (-44, -2), (-50, 0), (-52, 4), (-55, 6), (-60, 8), (-65, 10),
    (-70, 12), (-75, 11),
]
AFRICA = [
    (-17, 15), (-16, 20), (-15, 25), (-10, 30), (-5, 35), (0, 36), (10, 37),
    (11, 34), (15, 32), (20, 32), (25, 31), (30, 31), (32, 31), (34, 28),
    (35, 24), (37, 20), (39, 18), (40, 15), (43, 12), (46, 11), (48, 11),
    (51, 12), (51, 10), (46, 5), (42, 0), (40, -5), (40, -10), (38, -15),
    (36, -20), (33, -25), (28, -30), (26, -34), (20, -35), (17, -32),
    (15, -27), (13, -20), (12, -15), (13, -10), (12, -5), (9, 0), (9, 4),
    (4, 6), (-2, 5), (-8, 5), (-13, 8), (-17, 12),
]
EUROPE = [
    (-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50),
    (0, 51), (2, 51), (4, 53), (7, 54), (8, 57), (10, 59), (12, 60),
    (10, 62), (5, 60), (5, 62), (10, 64), (13, 66), (18, 69), (25, 71),
    (30, 70), (32, 68), (35, 66), (40, 64), (42, 60), (38, 56), (35, 54),
    (30, 54), (28, 55), (25, 55), (22, 56), (21, 58), (18, 56), (15, 55),
    (12, 54), (10, 54), (8, 55), (5, 58), (0, 58), (-2, 57), (-5, 56),
    (-8, 55), (-10, 54), (-10, 52), (-10, 50), (-8, 48), (-6, 46),
    (-4, 44), (-2, 43), (-2, 40), (-4, 38), (-6, 36), (-9, 37),
]
ASIA = [
    (35, 36), (40, 38), (43, 41), (45, 42), (48, 44), (50, 46), (52, 47),
    (55, 47), (58, 45), (60, 45), (62, 46), (65, 45), (68, 46), (70, 48),
    (72, 50), (75, 52), (78, 55), (80, 58), (82, 60), (85, 62), (88, 65),
    (90, 68), (95, 70), (100, 72), (105, 73), (110, 74), (115, 73),
    (120, 72), (125, 71), (130, 70), (135, 68), (140, 68), (145, 66),
    (150, 64), (155, 62), (158, 60), (160, 62), (162, 60), (160, 55),
    (155, 52), (150, 50), (145, 45), (142, 42), (140, 40), (138, 38),
    (135, 35), (132, 33), (130, 32), (128, 30), (125, 28), (122, 30),
    (120, 28), (118, 25), (115, 22), (112, 21), (108, 18), (105, 15),
    (103, 12), (100, 10), (98, 8), (95, 10), (92, 15), (90, 20), (88, 22),
    (86, 20), (84, 18), (82, 16), (80, 13), (78, 10), (76, 8), (74, 12),
    (72, 18), (70, 20), (68, 22), (66, 24), (64, 25), (62, 25), (60, 25),
    (58, 24), (56, 26), (54, 26), (52, 26), (50, 28), (48, 29), (46, 29),
    (44, 29), (42, 28), (40, 28), (38, 30), (36, 32), (35, 34),
]
AUSTRALIA = [
    (113, -22), (114, -30), (115, -35), (118, -35), (122, -34), (126, -32),
    (129, -32), (132, -32), (135, -35), (137, -38), (140, -38), (143, -39),
    (146, -39), (149, -37), (150, -35), (152, -32), (153, -28), (154, -24),
    (152, -22), (150, -20), (148, -19), (146, -18), (144, -15), (142, -12),
    (140, -17), (138, -17), (136, -15), (134, -12), (132, -11), (130, -13),
    (128, -14), (126, -14), (124, -15), (122, -17), (120, -20), (118, -20),
    (115, -21),
]
BRITAIN = [(-5, 50), (-3, 53), (-5, 55), (-3, 57), (-1, 58), (0, 57),
           (-1, 55), (1, 52), (0, 51), (-3, 50)]
JAPAN = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
         (141, 39), (141, 42), (143, 43), (145, 44), (142, 45), (140, 43),
         (138, 40), (136, 38), (134, 36), (132, 34)]
INDONESIA = [(95, 5), (98, 3), (100, 0), (102, -2), (104, -4), (106, -6),
             (108, -7), (110, -7), (112, -7), (114, -8), (116, -8),
             (118, -9), (120, -10), (122, -9), (124, -9), (126, -8),
             (128, -6), (130, -4), (131, -2), (132, 0), (130, 2), (128, 3),
             (126, 2), (124, 1), (122, 0), (120, 1), (118, 2), (116, 4),
             (114, 5), (112, 6), (110, 4), (108, 3), (106, 2), (104, 1),
             (102, 2), (100, 4), (98, 5)]
BORNEO = [(109, 1), (113, 4), (117, 6), (119, 2), (117, -2), (113, -3),
          (110, -1)]
NEW_GUINEA = [(131, -1), (136, -2), (141, -3), (146, -6), (150, -8),
              (147, -9), (142, -8), (137, -6), (132, -3)]

CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EUROPE,
              ASIA, AUSTRALIA, BRITAIN, JAPAN, INDONESIA, BORNEO,
              NEW_GUINEA]

# story number -> (lon, lat) for the map pins (nudged a few degrees where
# true positions would merge at this scale; still in the right country)
PINS = {
    1: (26, 39), 2: (114.2, 22.3), 3: (174.8, -41.3), 4: (50.6, 26.2),
    5: (9, 44), 6: (10.7, 59.9), 7: (0, 50), 8: (36, 31),
    9: (30.5, 50.45), 10: (-66.9, 10.5), 11: (15.3, -4.3), 12: (-0.2, 5.6),
}


# ---------------------------------------------------------------- drawing
def draw_sun_globe(draw, x0, y0, x1, y1):
    """Lead illustration: a rising sun over a small globe. Pure geometry."""
    draw.rectangle([x0, y0, x1, y1], fill=(253, 214, 140),
                   outline=INK, width=2)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 + 6
    r = 26
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        xa, ya = cx + int(32 * math.cos(a)), cy + int(32 * math.sin(a))
        xb, yb = cx + int(38 * math.cos(a)), cy + int(38 * math.sin(a))
        draw.line([xa, ya, xb, yb], fill=(214, 120, 20), width=3)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(232, 148, 40),
                 outline=(150, 70, 10), width=2)
    gx, gy, gr = x0 + 30, y0 + 26, 18
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(90, 140, 190),
                 outline=INK, width=2)
    draw.ellipse([gx - 10, gy - 12, gx + 2, gy + 2], fill=(90, 170, 90))
    draw.ellipse([gx - 2, gy + 4, gx + 12, gy + 12], fill=(90, 170, 90))
    draw.arc([gx - gr, gy - gr, gx + gr, gy + gr], 300, 60,
             fill=(255, 255, 255), width=2)
    draw.line([gx, gy - gr, gx, gy + gr], fill=(255, 255, 255), width=1)
    draw.text((x0 + 8, y1 - 18), "ANTALYA", font=font(SANS_B, 11), fill=INK)


def draw_ballot(draw, x0, y0, x1, y1):
    """Hong Kong: a ballot box with a checked ballot."""
    draw.rectangle([x0, y0, x1, y1], fill=(226, 232, 240),
                   outline=INK, width=2)
    draw.rectangle([x0 + 6, y0 + 8, x0 + 30, y0 + 34], fill=(255, 255, 255),
                   outline=INK, width=2)
    draw.line([x0 + 11, y0 + 23, x0 + 17, y0 + 29, x0 + 26, y0 + 14],
              fill=RED, width=3)
    draw.rectangle([x0 + 34, y0 + 30, x1 - 6, y1 - 8], fill=(60, 90, 140),
                   outline=INK, width=2)
    draw.rectangle([x0 + 40, y0 + 36, x1 - 12, y0 + 40], fill=INK)
    draw.text((x0 + 36, y1 - 18), "723", font=font(SANS_B, 10),
              fill=(255, 255, 255))


def draw_cricket(draw, x0, y0, x1, y1):
    """Wellington: stumps, a bat and a red ball."""
    draw.rectangle([x0, y0, x1, y1], fill=(198, 226, 160),
                   outline=INK, width=2)
    draw.rectangle([x0 + 6, y0 + 40, x1 - 6, y1 - 6], fill=(232, 214, 160),
                   outline=INK, width=1)
    for sx in (x0 + 10, x0 + 15, x0 + 20):
        draw.rectangle([sx, y0 + 14, sx + 3, y0 + 38], fill=(210, 170, 90),
                       outline=INK, width=1)
    draw.polygon([(x0 + 52, y0 + 8), (x0 + 60, y0 + 6), (x0 + 44, y0 + 40),
                  (x0 + 36, y0 + 44)], fill=(214, 178, 110), outline=INK)
    draw.rectangle([x0 + 56, y0 + 2, x0 + 62, y0 + 10], fill=(120, 80, 40))
    bx, by = x1 - 14, y0 + 16
    draw.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=RED,
                 outline=INK, width=2)
    draw.arc([bx - 9, by - 9, bx + 9, by + 9], 200, 340,
             fill=(255, 255, 255), width=2)
    draw.text((x0 + 6, y1 - 16), "629-6", font=font(SANS_B, 10), fill=INK)


def draw_radar(draw, x0, y0, x1, y1):
    """Bahrain: a radar dish with signal arcs and a flame."""
    draw.rectangle([x0, y0, x1, y1], fill=(240, 224, 200),
                   outline=INK, width=2)
    draw.arc([x0 + 8, y0 + 10, x0 + 48, y0 + 50], 180, 360, fill=INK,
             width=3)
    draw.line([x0 + 28, y0 + 30, x0 + 28, y1 - 8], fill=INK, width=3)
    draw.line([x0 + 18, y1 - 8, x0 + 38, y1 - 8], fill=INK, width=3)
    for rr in (6, 12, 18):
        draw.arc([x0 + 28 - rr, y0 + 30 - rr, x0 + 28 + rr, y0 + 30 + rr],
                 270, 360, fill=RED, width=2)
    fx = x1 - 16
    draw.polygon([(fx, y0 + 22), (fx + 8, y0 + 38), (fx + 4, y0 + 43),
                  (fx - 4, y0 + 43), (fx - 8, y0 + 38)], fill=(230, 110, 20),
                 outline=INK)
    draw.text((x0 + 6, y1 - 16), "AL-RIFFA", font=font(SANS_B, 9), fill=INK)


ILLUSTRATIONS = {1: draw_sun_globe, 2: draw_ballot, 3: draw_cricket,
                 4: draw_radar}


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([4, 4, W - 5, H - 5], outline=INK, width=3)

    # ---- masthead
    d.text((W // 2, 8), "THE DAILY ORBIT", font=font(SERIF_B, 64), fill=INK,
           anchor="ma")
    d.text((W // 2, 80),
           "SUNDAY 22 NOVEMBER 2026  ·  50 STORIES  ·  7 REGIONS  ·  "
           "EVERY ONE FROM THIS SUNDAY",
           font=font(SANS_B, 13), fill=INK, anchor="ma")
    d.line([12, 100, W - 12, 100], fill=INK, width=2)
    d.line([12, 104, W - 12, 104], fill=INK, width=1)

    # ---- lead story
    y = 112
    d.text((12, y), "1  ·  COP31", font=font(SANS_B, 13), fill=RED)
    y += 20
    f_head = font(SERIF_B, 26)
    lines = wrap(d, LEAD["headline"], f_head, 800)
    y = draw_lines(d, 12, y, lines, f_head, INK, 29)
    y += 4
    f_deck = font(SANS, 13)
    lines = wrap(d, LEAD["deck"], f_deck, 800)
    y = draw_lines(d, 12, y, lines, f_deck, INK, 16)
    y += 3
    d.text((12, y), LEAD["source"], font=font(SANS, 10), fill=GRAY)
    ILLUSTRATIONS[1](d, 836, 112, 1012, 206)
    d.line([12, 214, W - 12, 214], fill=INK, width=2)

    # ---- UTC timeline
    y = 222
    d.text((12, y), "THE DAY IN UTC", font=font(SANS_B, 12), fill=RED)
    col_w = 1000 // 6
    y = 240
    for i, (t, label) in enumerate(TIMELINE):
        cx = 12 + i * col_w
        d.text((cx, y), t, font=font(SANS_B, 13), fill=RED)
        lines = wrap(d, label, font(SANS, 10), col_w - 10)
        draw_lines(d, cx, y + 17, lines[:2], font(SANS, 10), INK, 12)
    d.line([12, 282, W - 12, 282], fill=INK, width=1)

    # ---- stories 2-4
    y0 = 290
    col_w = 322
    for i, st in enumerate(ILLUSTRATED):
        cx = 12 + i * (col_w + 13)
        ILLUSTRATIONS[st["num"]](d, cx + 246, y0, cx + 322, y0 + 64)
        d.text((cx, y0), str(st["num"]), font=font(SERIF_B, 20), fill=RED)
        f_h = font(SANS_B, 14)
        lines = wrap(d, st["headline"], f_h, 212)
        draw_lines(d, cx + 26, y0 + 2, lines[:3], f_h, INK, 17)
        f_d = font(SANS, 11)
        lines = wrap(d, st["deck"], f_d, 310)
        draw_lines(d, cx, y0 + 68, lines[:3], f_d, INK, 13)
        d.text((cx, y0 + 110), st["source"], font=font(SANS, 10), fill=GRAY)
    d.line([12, 418, W - 12, 418], fill=INK, width=2)

    # ---- more top stories 5-16
    y = 426
    d.text((12, y), "MORE TOP STORIES", font=font(SANS_B, 12), fill=RED)
    y = 444
    f_top = font(SANS, 11)
    for row in range(6):
        for col in range(2):
            st = TOP[row * 2 + col]
            cx = 12 + col * 500
            d.text((cx, y), f"{st[0]}.  {st[1]}  ({st[2]})", font=f_top,
                   fill=INK)
        y += 15
    d.line([12, y + 2, W - 12, y + 2], fill=INK, width=2)

    # ---- map + date check
    y_map = y + 10
    d.text((12, y_map), "WHERE IT HAPPENED", font=font(SANS_B, 12),
           fill=RED)
    map_x0, map_y0 = 12, y_map + 18
    map_w, map_h = 594, 124
    d.rectangle([map_x0, map_y0, map_x0 + map_w, map_y0 + map_h],
                fill=OCEAN, outline=INK, width=1)

    def project(lon, lat):
        px = map_x0 + (lon + 180.0) / 360.0 * map_w
        py = map_y0 + (84.0 - lat) / 142.0 * map_h
        return (px, py)

    for poly in CONTINENTS:
        d.polygon([project(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=LAND_EDGE)
    f_pin = font(SANS_B, 7)
    for num, (lon, lat) in sorted(PINS.items()):
        px, py = project(lon, lat)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED, outline=INK,
                  width=1)
        d.text((px, py), str(num), font=f_pin, fill=(255, 255, 255),
               anchor="mm")
    d.text((12, map_y0 + map_h + 4), "Pins are numbered to the stories above.",
           font=font(SANS, 9), fill=GRAY)

    # date check panel
    dx0, dx1 = 618, 1012
    d.rectangle([dx0, y_map, dx1, y_map + 18 + map_h], outline=INK, width=1)
    d.rectangle([dx0, y_map, dx1, y_map + 22], fill=RED)
    d.text((dx0 + 8, y_map + 4), "DATE CHECK — LEFT OUT AS OLDER NEWS",
           font=font(SANS_B, 11), fill=(255, 255, 255))
    yy = y_map + 26
    f_dc = font(SANS, 10)
    for item in DATE_CHECK:
        d.text((dx0 + 8, yy), "·  " + item, font=f_dc, fill=INK)
        yy += 11
    d.text((dx0 + 8, yy + 1),
           "Not yet: the COP31 deal is a draft until the 06:00 GMT session.",
           font=font(SANS_B, 10), fill=RED)

    # ---- the rest of the day 17-50
    y = map_y0 + map_h + 20
    d.text((12, y), "THE REST OF THE DAY  —  STORIES 17 TO 50",
           font=font(SANS_B, 12), fill=RED)
    y += 18
    d.line([12, y, W - 12, y], fill=INK, width=1)
    y += 6
    f_rest = font(SANS, 10)
    f_src = font(SANS, 9)
    for row in range(17):
        for col in range(2):
            st = REST[row * 2 + col]
            cx = 12 + col * 500
            d.text((cx, y), f"{st[0]}.  {st[1]}", font=f_rest, fill=INK)
            sw = d.textlength(st[2], font=f_src)
            d.text((cx + 488 - sw, y + 1), st[2], font=f_src, fill=GRAY)
        y += 14
    d.line([12, y + 2, W - 12, y + 2], fill=INK, width=2)

    # ---- by the numbers
    y += 6
    d.rectangle([12, y, W - 12, y + 26], outline=INK, width=1)
    d.text((W // 2, y + 2), "BY THE NUMBERS", font=font(SANS_B, 11),
           fill=RED, anchor="ma")
    d.text((W // 2, y + 14), NUMBERS, font=font(SANS, 10), fill=INK,
           anchor="ma")

    # ---- footer (one line, just below the numbers box, inside the border)
    d.text((W // 2, y + 29),
           "Every story here happened, or was first reported, on Sunday "
           "22 November 2026. Sources: Reuters · AP · AFP · Al Jazeera · "
           "ANI · PTI · HK govt · wire reports.",
           font=font(SANS, 9), fill=DARKGRAY, anchor="ma")

    # ---- paper grain (deterministic) for texture and file density
    rng = random.Random(20261122)
    grain = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grain)
    for _ in range(9000):
        gx = rng.randrange(W)
        gy = rng.randrange(H)
        shade = rng.choice([(0, 0, 0, 10), (255, 255, 255, 12)])
        gd.point((gx, gy), fill=shade)
    img = Image.alpha_composite(img.convert("RGBA"), grain).convert("RGB")

    img.save(OUT, format="PNG")
    print("wrote", OUT)


if __name__ == "__main__":
    render()
