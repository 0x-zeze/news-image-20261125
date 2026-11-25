"""News-image-20261125: renders a one-day world newspaper for Wednesday
25 November 2026 as a 1024x1024 PNG. Pure Python 3 standard library,
no network, fully deterministic: two runs write identical bytes.

Layout: masthead, UTC timeline, world map with numbered pins, 52 sourced
stories in 4 columns, a DATE CHECK box, and a counts footer.
"""
import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- PNG encoder
def encode_png(w, h, buf):
    """Encode a w*h*3 RGB bytearray as PNG bytes (filter 0, zlib level 9)."""
    def chunk(tag, data):
        crc = binascii.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", crc)

    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack("!IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------- 5x7 font
FONT_5X7 = {
    "A": ["..#..", ".#.#.", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".###.", "#...#", "#....", ".###.", "....#", "#...#", ".###."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"],
    "3": [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", "..#..", "..#.."],
    ",": [".....", ".....", ".....", ".....", "..#..", "..#..", ".#..."],
    ":": [".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."],
    ";": [".....", "..#..", "..#..", ".....", "..#..", "..#..", ".#..."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    "-": [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "%": ["##..#", "##..#", "...#.", "..#..", ".#...", "#..##", "#..##"],
    "$": ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
    "+": [".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."],
    "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
}


# ---------------------------------------------------------------- drawing
def set_px(buf, w, x, y, r, g, b):
    h = len(buf) // (w * 3)
    if 0 <= x < w and 0 <= y < h:
        i = (y * w + x) * 3
        buf[i] = r
        buf[i + 1] = g
        buf[i + 2] = b


def fill_rect(buf, w, x, y, rw, rh, r, g, b):
    h = len(buf) // (w * 3)
    x0, x1 = max(0, x), min(w, x + rw)
    y0, y1 = max(0, y), min(h, y + rh)
    if x0 >= x1 or y0 >= y1:
        return
    row = bytes((r, g, b)) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * w + x0) * 3
        buf[i:i + len(row)] = row


def draw_hline(buf, w, x0, x1, y, r, g, b):
    for x in range(min(x0, x1), max(x0, x1) + 1):
        set_px(buf, w, x, y, r, g, b)


def draw_vline(buf, w, x, y0, y1, r, g, b):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        set_px(buf, w, x, y, r, g, b)


def draw_circle(buf, w, cx, cy, rad, r, g, b):
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            if dx * dx + dy * dy <= rad * rad:
                set_px(buf, w, cx + dx, cy + dy, r, g, b)


def draw_ring(buf, w, cx, cy, rad, r, g, b):
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            d = dx * dx + dy * dy
            if (rad - 1) * (rad - 1) <= d <= rad * rad:
                set_px(buf, w, cx + dx, cy + dy, r, g, b)


def text_w(text, scale):
    return len(text) * 6 * scale


def draw_text(buf, w, x, y, text, scale, r, g, b, font=FONT_5X7):
    cx, cy = x, y
    for ch in text:
        if ch == "\n":
            cx = x
            cy += 8 * scale
            continue
        glyph = font.get(ch) or font.get(ch.upper()) or font[" "]
        for gy, row in enumerate(glyph):
            for gx, px in enumerate(row):
                if px == "#":
                    fill_rect(buf, w, cx + gx * scale, cy + gy * scale,
                              scale, scale, r, g, b)
        cx += 6 * scale


def wrap(text, width):
    """Wrap text to lines of at most `width` chars at word boundaries."""
    lines, cur = [], ""
    for word in text.split(" "):
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = (cur + " " + word).strip()
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- world map
LAND = [
    ("North America", [
        (-165, 65), (-156, 71), (-125, 70), (-94, 68),
        (-82, 54), (-75, 62), (-56, 52), (-67, 44),
        (-81, 25), (-90, 30), (-97, 22), (-88, 21),
        (-79, 9), (-105, 19), (-117, 33), (-130, 55),
    ]),
    ("Greenland", [
        (-44, 60), (-52, 64), (-53, 69), (-58, 73),
        (-66, 75), (-20, 75), (-21, 70), (-32, 66), (-40, 62),
    ]),
    ("South America", [
        (-78, 9), (-72, 12), (-62, 10), (-50, 1),
        (-35, -6), (-38, -13), (-41, -23), (-53, -34),
        (-65, -42), (-68, -55), (-74, -46), (-71, -18),
        (-81, -5), (-79, 2),
    ]),
    ("Africa", [
        (-6, 36), (10, 37), (15, 32), (32, 31),
        (43, 12), (51, 11), (41, -2), (40, -15),
        (33, -26), (20, -35), (15, -26), (12, -6),
        (9, 4), (-8, 5), (-17, 15), (-13, 28),
    ]),
    ("Europe", [
        (-9, 37), (-9, 43), (-2, 43), (-4, 48),
        (8, 55), (5, 61), (20, 70), (31, 70),
        (42, 67), (60, 68), (58, 50), (40, 45),
        (29, 41), (23, 37), (15, 38), (3, 42),
    ]),
    ("Asia", [
        (60, 68), (104, 75), (142, 72), (178, 66),
        (160, 56), (138, 46), (129, 35), (121, 31),
        (109, 20), (104, 2), (94, 18), (78, 8),
        (67, 25), (58, 22), (44, 13), (35, 36),
    ]),
    ("Australia", [
        (142, -11), (153, -27), (150, -37), (141, -38),
        (136, -34), (129, -32), (115, -34), (114, -22),
        (129, -15), (136, -12), (138, -17),
    ]),
]


def lonlat_to_xy(lon, lat, x0, y0, w, h):
    return (x0 + (lon + 180.0) / 360.0 * w,
            y0 + (75.0 - lat) / 130.0 * h)


def fill_polygon(buf, w, pts, r, g, b):
    if len(pts) < 3:
        return
    min_y = max(0, math.floor(min(y for _, y in pts)))
    max_y = math.ceil(max(y for _, y in pts))
    for y in range(min_y, max_y):
        sy = y + 0.5
        xs = []
        x1, y1 = pts[-1]
        for x2, y2 in pts:
            if (y1 <= sy < y2) or (y2 <= sy < y1):
                xs.append(x1 + (sy - y1) * (x2 - x1) / (y2 - y1))
            x1, y1 = x2, y2
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            xa = max(0, math.ceil(xs[i] - 0.5))
            xb = min(w, math.ceil(xs[i + 1] - 0.5))
            for x in range(xa, xb):
                set_px(buf, w, x, y, r, g, b)


# ---------------------------------------------------------------- the day
# (region, headline, source, status). 52 stories, counts checked in footer.
STORIES = [
    # EUROPE - 10
    ("EUROPE", "ZELENSKIY CONFIRMS UKRAINE DRONE STRIKES ON RUSSIAN SHIPS", "REUTERS", "CONFIRMED"),
    ("EUROPE", "RUSSIA CALLS SHIP STRIKES TERRORISM, WARNS OF SEVERE CONSEQUENCES", "REUTERS", "CONFIRMED"),
    ("EUROPE", "MORE THAN 700,000 RUSSIAN SOLDIERS KILLED IN UKRAINE WAR, ANALYSIS FINDS", "RFE/RL", "REPORTED"),
    ("EUROPE", "NATO PLANS EARLY-WARNING AIRCRAFT IN POLAND AFTER MISSILES LAND", "REUTERS", "REPORTED"),
    ("EUROPE", "EU ANNOUNCES FURTHER SANCTIONS AGAINST RUSSIA", "EU", "CONFIRMED"),
    ("EUROPE", "RUSSIA STARTS TOWING DRONE-HIT SHIP IN BALTIC, FINLAND SAYS", "REUTERS", "CONFIRMED"),
    ("EUROPE", "SARKOZY CORRUPTION CASE ORDERED TO TRIAL, HEARING SET FOR APRIL 2027", "REUTERS", "CONFIRMED"),
    ("EUROPE", "UK MINISTERS ASK PUBLIC VIEWS ON CHANGING AGE OF CONSENT", "BBC", "CONFIRMED"),
    ("EUROPE", "UK NUCLEAR TEST VETERANS TO GET FULL TRUTH, PANEL CONFIRMED", "BBC", "CONFIRMED"),
    ("EUROPE", "THOUSANDS PROTEST CLOSURE OF CRITICAL MEDIA OUTLETS IN TURKEY", "REUTERS", "REPORTED"),
    # MIDDLE EAST - 10
    ("MIDDLE EAST", "HOUTHIS HIT RIYADH'S TALLEST TOWER, 11 WOUNDED", "SAUDI CIVIL DEFENSE", "CONFIRMED"),
    ("MIDDLE EAST", "HOUTHIS PUSH TO 60 KM FROM ADEN, ARMY SAYS CITY WILL HOLD", "REUTERS", "CONFIRMED"),
    ("MIDDLE EAST", "IRAN STRIKE INJURES TWO IN BAHRAIN, SAUDI CONDEMNS ATTACKS", "REUTERS", "CONFIRMED"),
    ("MIDDLE EAST", "IRAN TO RATION ELECTRICITY AS GRID BATTERED BY US, ISRAELI STRIKES", "RFE/RL", "REPORTED"),
    ("MIDDLE EAST", "IRAN BRACES FOR WINTER GAS SHORTAGES AS WAR DAMAGE DEEPENS", "RFE/RL", "REPORTED"),
    ("MIDDLE EAST", "GAZA DEATH TOLL REACHES 74,746, WAFA SAYS", "WAFA", "REPORTED"),
    ("MIDDLE EAST", "OXFAM: POLLUTION RISKS ACROSS MORE THAN 99% OF GAZA", "OXFAM", "REPORTED"),
    ("MIDDLE EAST", "US ENVOY NOT CERTAIN ISRAEL MILITARY AID ENDS THIS YEAR", "REUTERS", "REPORTED"),
    ("MIDDLE EAST", "IRAN TANKERS HIT BY NAVAL MINES IN STRAIT OF HORMUZ, IRGC SAYS", "REUTERS", "REPORTED"),
    ("MIDDLE EAST", "US EYES IRAN IN CYBERATTACKS ON ENERGY TANKERS", "WSJ", "REPORTED"),
    # NORTH AMERICA - 12
    ("NORTH AMERICA", "US CIA AND ODNI SUFFER CYBERSECURITY BREACH", "REUTERS", "REPORTED"),
    ("NORTH AMERICA", "TRUMP AWARDS RUDY GIULIANI THE MEDAL OF FREEDOM", "WASHINGTON POST", "CONFIRMED"),
    ("NORTH AMERICA", "TRUMP PARDONS TURKEYS FREEDOM AND FEATHERS FOR THANKSGIVING", "AP", "CONFIRMED"),
    ("NORTH AMERICA", "DEMOCRATS WIN LARGEST HOUSE MAJORITY IN DECADES", "EURONEWS", "CONFIRMED"),
    ("NORTH AMERICA", "US CONSUMER CONFIDENCE JUMPS TO HIGHEST IN NEARLY TWO YEARS", "REUTERS", "CONFIRMED"),
    ("NORTH AMERICA", "US PCE INFLATION AND Q3 GDP DATA DUE WEDNESDAY", "REUTERS", "CONFIRMED"),
    ("NORTH AMERICA", "PENTAGON IN TALKS WITH GM TO MASS-PRODUCE DRONES", "WSJ", "REPORTED"),
    ("NORTH AMERICA", "MICROSOFT DECLARES CODE RED AFTER HISTORIC OUTAGE", "REUTERS", "REPORTED"),
    ("NORTH AMERICA", "FORT HOOD SHOOTER HASAN SEEKS STAY OF EXECUTION", "REUTERS", "CONFIRMED"),
    ("NORTH AMERICA", "RADAR ISSUE DELAYS FLIGHTS AT CHICAGO O'HARE, FAA SAYS", "REUTERS", "CONFIRMED"),
    ("NORTH AMERICA", "ILHAN OMAR HOME SEARCH: EVIDENCE SOUGHT BACK TO 1980", "WSJ", "REPORTED"),
    ("NORTH AMERICA", "DELTA DELAYS FLIGHTS AS THANKSGIVING TRAVEL BEGINS", "REUTERS", "CONFIRMED"),
    # ASIA-PACIFIC - 10
    ("ASIA-PACIFIC", "HUAWEI CONVICTED IN US CRIMINAL TRIAL OVER IRAN BUSINESS", "REUTERS", "CONFIRMED"),
    ("ASIA-PACIFIC", "NVIDIA'S HUANG BACK AS CEO, SHARES FALL 5.9% AS BOUNCE FADES", "REUTERS", "CONFIRMED"),
    ("ASIA-PACIFIC", "ASIAN STOCKS TUMBLE ON FRESH US TARIFF THREATS, KOREA -5.3%", "REUTERS", "CONFIRMED"),
    ("ASIA-PACIFIC", "US BLACKLISTS SINGAPORE'S MEGASPEED OVER NVIDIA CHIP DIVERSION", "REUTERS", "CONFIRMED"),
    ("ASIA-PACIFIC", "BJP AND AKALI DAL ANNOUNCE ALLIANCE FOR 2027 PUNJAB POLLS", "REUTERS", "CONFIRMED"),
    ("ASIA-PACIFIC", "TATA STEEL PROPOSES $3.7B ACQUISITION OF APL APOLLO STAKE", "REUTERS", "REPORTED"),
    ("ASIA-PACIFIC", "JIO SCRAPS DAILY DATA CAP ON SELECT PLANS", "REUTERS", "CONFIRMED"),
    ("ASIA-PACIFIC", "GOOGLE CLOUD INDIA DENIES MASS LAYOFFS, CONFIRMS 30 CUTS", "REUTERS", "CONFIRMED"),
    ("ASIA-PACIFIC", "ENGLAND BEAT AUSTRALIA BY 8 WICKETS IN 2ND T20I", "REUTERS", "CONFIRMED"),
    ("ASIA-PACIFIC", "RFE/RL RETURNS TO SHORTWAVE RADIO FOR AFGHAN GIRLS", "RFE/RL", "CONFIRMED"),
    # AFRICA - 2
    ("AFRICA", "UKRAINE SINKS RUSSIAN WARSHIP IN BENGHAZI HARBOUR, LIBYA", "RFE/RL", "CONFIRMED"),
    ("AFRICA", "LIBYA'S FROZEN CONFLICT RISKS FRESH INSTABILITY", "REUTERS", "REPORTED"),
    # LATIN AMERICA - 2
    ("LATIN AMERICA", "MEXICO CAPTURES DRUG LORDS WITH GROWING US INTELLIGENCE HELP", "WSJ", "REPORTED"),
    ("LATIN AMERICA", "VENEZUELA REPORTS TOTAL PUBLIC DEBT OF $237.5 BILLION", "REUTERS", "CONFIRMED"),
    # GLOBAL - 6
    ("GLOBAL", "COP31 COLLAPSES IN ANTALYA, NO FOSSIL-FUEL DEAL", "REUTERS", "CONFIRMED"),
    ("GLOBAL", "266 MILLION PEOPLE FACE ACUTE FOOD INSECURITY, WFP SAYS", "WFP", "REPORTED"),
    ("GLOBAL", "RIEMANN HYPOTHESIS PROOF PUBLISHED: 17M LINES OF CODE", "WSJ", "REPORTED"),
    ("GLOBAL", "BITCOIN FALLS TO $59,257, ETHER $1,660", "REUTERS", "CONFIRMED"),
    ("GLOBAL", "DELL LIFTS FORECASTS ON RECORD AI SERVER QUARTER", "REUTERS", "CONFIRMED"),
    ("GLOBAL", "ANTHROPIC'S NEW MILLIONAIRES FUEL SF HOUSING BOOM", "WSJ", "REPORTED"),
]

# Timeline strip: (UTC time, short label), in the order reported.
TIMELINE = [
    ("01:00", "RFE/RL: 700,000 RUSSIAN DEAD"),
    ("03:00", "ASIAN STOCKS SLIDE -2.3%"),
    ("06:00", "HOUTHI STRIKE ON RIYADH TOWER"),
    ("09:00", "ZELENSKIY CONFIRMS SHIP STRIKES"),
    ("12:00", "COP31 COLLAPSES IN ANTALYA"),
    ("15:00", "TRUMP AWARDS GIULIANI MEDAL"),
    ("18:00", "US CONFIDENCE NEAR 2-YEAR HIGH"),
    ("21:00", "NVIDIA SHARES FALL 5.9%"),
]

# Numbered map pins: (number, lon, lat, short label).
PINS = [
    (1, 30.5, 50.5, "KYIV"),
    (2, 24.0, 59.5, "GULF OF FINLAND"),
    (3, 20.0, 32.1, "BENGHAZI"),
    (4, 46.7, 24.7, "RIYADH"),
    (5, 45.0, 12.8, "ADEN"),
    (6, 30.7, 36.9, "ANTALYA"),
    (7, -77.0, 38.9, "WASHINGTON"),
    (8, -87.6, 41.9, "CHICAGO"),
    (9, 127.0, 37.5, "SEOUL"),
    (10, 77.2, 28.6, "NEW DELHI"),
]

# Older news deliberately left out of the 25 November picture.
LEFT_OUT = [
    "GTA 6 RELEASED WORLDWIDE - 19 NOV",
    "PUTIN, TRUMP AND XI MET IN CHINA - 20 NOV",
    "DEADLY RUSSIAN STRIKES POUND KYIV - 20 NOV",
    "NEPAL PM SHAH'S INDIA VISIT ENDS - 23 NOV",
]
NOT_YET = "US OCT PCE INFLATION + Q3 GDP - DUE LATER TODAY"

REGION_COUNTS = [
    ("EUROPE", 10), ("MIDDLE EAST", 10), ("NORTH AMERICA", 12),
    ("ASIA-PACIFIC", 10), ("AFRICA", 2), ("LATIN AMERICA", 2),
    ("GLOBAL", 6),
]

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (20, 20, 20)
NAVY = (26, 42, 74)
RED = (178, 34, 34)
GRAY = (96, 96, 90)
OCEAN = (198, 222, 235)
LANDC = (186, 200, 160)
RULEC = (120, 120, 110)
WHITE = (255, 255, 255)
CREAM = (220, 220, 210)


def draw_masthead(buf):
    fill_rect(buf, W, 0, 0, W, 64, *NAVY)
    draw_text(buf, W, 24, 12, "THE WORLD IN ONE DAY", 3, *WHITE)
    draw_text(buf, W, 24, 42, "WEDNESDAY 25 NOVEMBER 2026", 2, 220, 220, 210)
    right = "52 STORIES - 7 REGIONS"
    draw_text(buf, W, W - 24 - text_w(right, 2), 12, right, 2, *WHITE)
    right2 = "EVERY CLAIM MARKED"
    draw_text(buf, W, W - 24 - text_w(right2, 1), 44, right2, 1, 200, 200, 190)


def draw_timeline(buf):
    draw_text(buf, W, 24, 70, "TIMELINE (UTC)", 1, *NAVY)
    xs = [24, 264, 504, 744]
    for row in range(2):
        y = 84 + row * 12
        for col in range(4):
            t, label = TIMELINE[row * 4 + col]
            x = xs[col]
            draw_text(buf, W, x, y, t, 1, *RED)
            draw_text(buf, W, x + 36, y, label, 1, *INK)


# Pins whose label sits to the LEFT of the pin (avoids a neighbour's label).
LEFT_LABELS = {8}


def draw_map(buf):
    x0, y0, mw, mh = 20, 108, 984, 272
    fill_rect(buf, W, x0, y0, mw, mh, *OCEAN)
    for _name, poly in LAND:
        pts = [lonlat_to_xy(lon, lat, x0, y0, mw, mh) for lon, lat in poly]
        fill_polygon(buf, W, pts, *LANDC)
    draw_hline(buf, W, x0, x0 + mw - 1, y0, *NAVY)
    draw_hline(buf, W, x0, x0 + mw - 1, y0 + mh - 1, *NAVY)
    draw_vline(buf, W, x0, y0, y0 + mh - 1, *NAVY)
    draw_vline(buf, W, x0 + mw - 1, y0, y0 + mh - 1, *NAVY)
    draw_text(buf, W, x0 + 8, y0 + 6, "WORLD MAP - PINS MARK THE 10 TOP STORIES", 1, *NAVY)
    for num, lon, lat, label in PINS:
        px, py = lonlat_to_xy(lon, lat, x0, y0, mw, mh)
        cx, cy = int(px), int(py)
        draw_circle(buf, W, cx, cy, 8, *RED)
        draw_ring(buf, W, cx, cy, 8, *WHITE)
        ns = str(num)
        draw_text(buf, W, cx - text_w(ns, 1) // 2, cy - 4, ns, 1, *WHITE)
        lx, ly = cx + 12, cy - 4
        if num in LEFT_LABELS:
            lx = cx - 12 - text_w(label, 1)
        if lx + text_w(label, 1) > x0 + mw - 6:
            lx = cx - 12 - text_w(label, 1)
        fill_rect(buf, W, lx - 2, ly - 2, text_w(label, 1) + 4, 11, *WHITE)
        draw_text(buf, W, lx, ly, label, 1, *NAVY)


def draw_stories(buf):
    draw_text(buf, W, 24, 390, "THE DAY IN BRIEF", 2, *NAVY)
    draw_hline(buf, W, 24, W - 24, 408, *RULEC)
    col_x = [24, 272, 520, 768]
    col_w = 232
    for col in range(4):
        x = col_x[col]
        y = 418
        prev_region = None
        for k in range(13):
            idx = col * 13 + k
            region, headline, source, status = STORIES[idx]
            if region != prev_region:
                draw_text(buf, W, x, y, region, 1, *RED)
                draw_hline(buf, W, x, x + col_w - 8, y + 9, *RULEC)
                y += 14
                prev_region = region
            lines = wrap("%d. %s" % (idx + 1, headline), 38)
            for ln in lines:
                draw_text(buf, W, x, y, ln, 1, *INK)
                y += 9
            draw_text(buf, W, x, y, "  %s - %s" % (source, status), 1, *GRAY)
            y += 13


def draw_footer(buf):
    draw_hline(buf, W, 24, W - 24, 920, *RULEC)
    # DATE CHECK box, left.
    fill_rect(buf, W, 24, 930, 470, 84, 255, 250, 240)
    draw_hline(buf, W, 24, 493, 930, *RED)
    draw_hline(buf, W, 24, 493, 1013, *RED)
    draw_vline(buf, W, 24, 930, 1013, *RED)
    draw_vline(buf, W, 493, 930, 1013, *RED)
    draw_text(buf, W, 32, 938, "DATE CHECK - LEFT OUT AS OLDER NEWS", 1, *RED)
    y = 954
    for item in LEFT_OUT:
        draw_text(buf, W, 32, y, "X " + item, 1, *INK)
        y += 10
    draw_text(buf, W, 32, y, "NOT YET: " + NOT_YET, 1, *GRAY)
    # Counts, right.
    draw_text(buf, W, 520, 938, "COUNTS - 52 STORIES", 1, *NAVY)
    counts = "  ".join("%s %d" % (name, n) for name, n in REGION_COUNTS)
    for i, ln in enumerate(wrap(counts, 78)):
        draw_text(buf, W, 520, 954 + i * 10, ln, 1, *INK)
    draw_text(buf, W, 520, 978, "SOURCES: REUTERS, RFE/RL, WSJ, BBC, AP, WFP,", 1, *INK)
    draw_text(buf, W, 520, 988, "OXFAM, WAFA, EU, WASHINGTON POST, EURONEWS", 1, *INK)
    draw_text(buf, W, 520, 1002, "DRAWN BY CODE - NO NETWORK - 25 NOV 2026", 1, *GRAY)


def main():
    buf = bytearray(bytes(PAPER) * (W * H))
    draw_masthead(buf)
    draw_timeline(buf)
    draw_map(buf)
    draw_stories(buf)
    draw_footer(buf)
    data = encode_png(W, H, buf)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
