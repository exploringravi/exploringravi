import math, random, textwrap, os, sys, json, re, urllib.request
from datetime import datetime
from xml.sax.saxutils import escape

UTCI = ["#22307a", "#3457a8", "#5a86cf", "#93b8e6", "#c9def4",
        "#a9d4a0", "#f3cf6a", "#ee9b4c", "#d95b3a", "#9e2229"]
THEMES = {
    "light": dict(bg="#ffffff", ink="#1f2328", mute="#59636e", faint="#8c959f", rule="#d8dee4"),
    "dark":  dict(bg="#0d1117", ink="#e6edf3", mute="#9198a1", faint="#656d76", rule="#2a3038"),
}
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
W = 1280


CSS = """
.f{animation:fadeup .9s cubic-bezier(.2,.7,.2,1) both}
.c{transform-box:fill-box;transform-origin:center;animation:pop .5s cubic-bezier(.3,1.4,.5,1) both, wave 5s ease-in-out 2.6s infinite}
.g{transform-box:fill-box;transform-origin:left center;animation:grow 1s cubic-bezier(.2,.7,.2,1) both}
.d{stroke-dasharray:1200;animation:draw 1.6s ease-out both}
@keyframes fadeup{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes pop{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:scale(1)}}
@keyframes wave{0%,70%,100%{opacity:1}35%{opacity:.5}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes draw{from{stroke-dashoffset:1200}to{stroke-dashoffset:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def svg(h, body, t, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" '
            f'role="img" aria-label="{label}"><style>{CSS}</style>'
            f'<rect width="{W}" height="{h}" fill="{t["bg"]}"/>{body}</svg>')


def d(sec):
    return f'style="animation-delay:{sec:.2f}s"'


def dd(a, b):
    return f'style="animation-delay:{a:.2f}s,{b:.2f}s"'


def mono(x, y, s, fill, size=12, ls=2.5, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" letter-spacing="{ls}" '
            f'fill="{fill}" text-anchor="{anchor}">{s}</text>')


def section(title, t):
    return mono(64, 64, title, t["faint"]) + \
        f'<line class="d" x1="{64 + len(title) * 10 + 24}" y1="60" x2="1216" y2="60" stroke="{t["rule"]}"/>'


# ---------- header: name plus a downscaled heat field ----------
def heat_field():
    rnd = random.Random(7)
    cells = []
    pitch, size = 14, 11
    x0, y0, cols, rows = 712, 56, 36, 22
    spots = [(0.72, 0.38, 0.20, 1.0), (0.45, 0.70, 0.16, 0.8), (0.90, 0.80, 0.14, 0.6), (0.30, 0.25, 0.12, 0.5)]
    for r in range(rows):
        for c in range(cols):
            u, v = c / (cols - 1), r / (rows - 1)
            # fade into the page on the left edge
            if rnd.random() > min(1.0, (u - 0.02) * 2.6):
                continue
            val = 0.30
            for (sx, sy, sr, a) in spots:
                val += a * math.exp(-((u - sx) ** 2 + (v - sy) ** 2) / (2 * sr ** 2))
            # a cool green corridor running diagonally (park or river)
            d = abs(v - (1.15 - 1.1 * u))
            val -= 0.65 * math.exp(-(d ** 2) / (2 * 0.035 ** 2))
            # street grid runs slightly hotter
            if c % 6 == 0 or r % 5 == 0:
                val += 0.12
            val += rnd.uniform(-0.12, 0.12)
            k = max(3, min(9, int(round(3 + val * 4.4))))
            dist = math.hypot(u - 0.72, v - 0.38)
            pop = 0.4 + dist * 1.6 + rnd.uniform(0, 0.15)
            wave = 2.6 + u * 2.2 + v * 0.6
            cells.append(f'<rect class="c" {dd(pop, wave)} x="{x0 + c * pitch}" y="{y0 + r * pitch}" width="{size}" height="{size}" fill="{UTCI[k]}"/>')
    return "".join(cells)


def header(t):
    b = f'<text class="f" {d(0.1)} font-family="{SERIF}" font-size="100" fill="{t["ink"]}" letter-spacing="-1.5">' \
        f'<tspan x="58" y="176">Ravi Kumar</tspan><tspan x="58" y="276">Pandey</tspan></text>'
    b += f'<rect class="g" {d(0.7)} x="64" y="318" width="56" height="3" fill="{UTCI[8]}"/>'
    b += f'<text class="f" {d(0.9)} x="64" y="364" font-family="{SERIF}" font-style="italic" font-size="26" fill="{t["mute"]}">Urbanist, scientist and founder of CityAI</text>'
    b += f'<g opacity="{1 if t["bg"] == "#ffffff" else 0.92}">{heat_field()}</g>'
    return svg(430, b, t, "Ravi Kumar Pandey. Urbanist, scientist and founder of CityAI.")


# ---------- expertise ----------
AREAS = [
    ("Urban heat and", "thermal comfort", "UTCI, WBGT and mean radiant temperature, from decades of city trends down to street-level exposure.", "UTCI · MRT · ENVI-MET", 8),
    ("Earth observation", "and downscaling", "Reanalysis downscaled to 10 m with Random Forest on Sentinel, MODIS and building data in Earth Engine.", "GEE · RANDOM FOREST · SENTINEL-2 · S5P", 6),
    ("Climate data", "analysis", "Hourly ERA5-Land over 46 years, trend testing, extreme-day statistics and WRF runs on HPC.", "ERA5-LAND · WRF · PYTHON", 2),
    ("Field sensing", "and perception", "Wearable sensor campaigns paired with surveys of thermal, air quality and acoustic comfort.", "WEARABLES · SURVEYS", 5),
]


def expertise(t):
    b = section("EXPERTISE", t)
    for i, (l1, l2, body, tags, k) in enumerate(AREAS):
        x = 64 + i * 296
        b += f'<g class="f" {d(0.15 + i * 0.22)}>'
        b += f'<rect class="g" {d(0.4 + i * 0.22)} x="{x}" y="104" width="28" height="4" fill="{UTCI[k]}"/>'
        b += mono(x + 40, 110, f"0{i + 1}", t["faint"], size=12, ls=2)
        b += f'<text font-family="{SERIF}" font-size="27" fill="{t["ink"]}">' \
             f'<tspan x="{x}" y="160">{l1}</tspan><tspan x="{x}" y="194">{l2}</tspan></text>'
        lines = textwrap.wrap(body, 33)
        b += f'<text font-family="{SANS}" font-size="15" fill="{t["mute"]}">' + "".join(
            f'<tspan x="{x}" y="{236 + j * 23}">{ln}</tspan>' for j, ln in enumerate(lines)) + "</text>"
        tl = textwrap.wrap(tags, 30)
        b += "".join(mono(x, 348 + j * 18, s, t["faint"], size=10, ls=1.6) for j, s in enumerate(tl))
        b += "</g>"
    return svg(400, b, t, "Expertise")


# ---------- path ----------
def X(year):
    return 64 + (year - 2015) * 95


PATH = [  # start, end, years label, title, place, side, class colour
    (2015, 2019, "2015 TO 2019", "B.Plan, urban planning", "School of Planning and Architecture, Bhopal", "up", 1),
    (2019, 2020, "2019 TO 2020", "PG Diploma, Geoinformatics", "ITC Twente with IIRS-ISRO", "down", 3),
    (2021, 2023, "2021 TO 2023", "Copernicus Master in Digital Earth", "Salzburg and Olomouc", "up", 5),
    (2023, 2026.9, "2023 TO NOW", "MSCA Doctoral Candidate", "The Cyprus Institute, Nicosia", "down", 7),
    (2025, 2025.6, "2025", "Visiting Scientist", "University of Perugia", "up", 9),
]


def path(t):
    b = section("PATH", t)
    ay = 236
    b += f'<line class="d" x1="64" y1="{ay}" x2="1216" y2="{ay}" stroke="{t["rule"]}" stroke-width="1"/>'
    for n, (s, e, yrs, title, place, side, k) in enumerate(PATH):
        t0 = 0.5 + n * 0.35
        b += f'<g class="f" {d(t0)}>'
        x1, x2 = X(s), X(e)
        point = e - s < 1
        if point:
            xm = (x1 + x2) / 2
            b += f'<circle cx="{xm}" cy="{ay}" r="6" fill="{UTCI[k]}" stroke="{t["bg"]}" stroke-width="3"/>'
            lx, anchor = 1216, "end"
            b += f'<line x1="{xm}" y1="{ay - 8}" x2="{xm}" y2="186" stroke="{t["rule"]}"/>'
        else:
            b += f'<rect class="g" {d(t0)} x="{x1}" y="{ay - 3}" width="{x2 - x1}" height="6" fill="{UTCI[k]}"/>'
            lx, anchor = x1, "start"
            if side == "up":
                b += f'<line x1="{x1}" y1="{ay - 3}" x2="{x1}" y2="186" stroke="{t["rule"]}"/>'
            else:
                b += f'<line x1="{x1}" y1="{ay + 3}" x2="{x1}" y2="282" stroke="{t["rule"]}"/>'
        ys = (120, 148, 172) if side == "up" else (308, 336, 360)
        b += mono(lx, ys[0], yrs, t["faint"], size=11, ls=2, anchor=anchor)
        b += f'<text x="{lx}" y="{ys[1]}" font-family="{SERIF}" font-size="20" fill="{t["ink"]}" text-anchor="{anchor}">{title}</text>'
        b += f'<text x="{lx}" y="{ys[2]}" font-family="{SANS}" font-size="14" fill="{t["mute"]}" text-anchor="{anchor}">{place}</text>'
        b += "</g>"
    return svg(400, b, t, "Path: education and positions")


# ---------- numbers ----------
NUMBERS = [("10 m", "UTCI heat maps"), ("100 m", "air quality maps"), ("46", "years of hourly data"),
           ("3", "European cities"), ("7", "languages spoken")]


def numbers(t):
    b = section("IN NUMBERS", t)
    for i, (big, small) in enumerate(NUMBERS):
        x = [64, 300, 570, 810, 1030][i]
        b += f'<g class="f" {d(0.2 + i * 0.18)}>'
        b += f'<text x="{x}" y="158" font-family="{SERIF}" font-size="60" fill="{t["ink"]}" letter-spacing="-1">{big}</text>'
        b += f'<rect class="g" {d(0.5 + i * 0.18)} x="{x + 2}" y="182" width="36" height="3" fill="{UTCI[[8, 6, 2, 5, 9][i]]}"/>'
        b += f'<text x="{x + 2}" y="214" font-family="{SANS}" font-size="16" fill="{t["mute"]}">{small}</text>'
        b += "</g>"
    return svg(250, b, t, "In numbers: 10 m UTCI heat maps, 100 m air quality maps, 46 years of hourly data, 3 European cities, 7 languages spoken")


# ---------- latest repositories (rebuilt automatically by GitHub Actions) ----------
LANG = {"Python": "#3572A5", "TypeScript": "#3178c6", "HTML": "#e34c26", "JavaScript": "#f1e05a",
        "R": "#198CE7", "Jupyter Notebook": "#DA5B0B", "CSS": "#663399", "Shell": "#89e051"}
USER = "exploringravi"


def fetch_repos():
    req = urllib.request.Request(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed",
                                 headers={"Accept": "application/vnd.github+json"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    repos = json.load(urllib.request.urlopen(req))
    repos = [r for r in repos if not r["fork"] and not r["archived"] and not r["private"] and r["name"] != USER]
    repos.sort(key=lambda r: r["pushed_at"], reverse=True)
    return repos[:6]


def pretty(name):
    return name.replace("_", " ").replace("-", " ")


def latest(t, repos):
    rows = (len(repos) + 2) // 3
    h = 110 + rows * 176
    b = section("LATEST ON GITHUB", t)
    for i, r in enumerate(repos):
        x = 64 + (i % 3) * 392
        y = 96 + (i // 3) * 176
        b += f'<g class="f" {d(0.15 + i * 0.14)}>'
        b += f'<rect x="{x}" y="{y}" width="368" height="152" rx="10" fill="none" stroke="{t["rule"]}"/>'
        b += f'<rect class="g" {d(0.4 + i * 0.14)} x="{x}" y="{y}" width="368" height="3" fill="{UTCI[[8, 6, 2, 5, 9, 3][i % 6]]}"/>'
        name = pretty(r["name"])
        fs = min(23, 318 / (0.53 * max(len(name), 1)))
        b += f'<text x="{x + 24}" y="{y + 46}" font-family="{SERIF}" font-size="{fs:.1f}" fill="{t["ink"]}">{escape(name)}</text>'
        desc = r.get("description") or "Fresh upload. Description coming soon."
        for j, ln in enumerate(textwrap.wrap(desc, 44)[:2]):
            b += f'<text x="{x + 24}" y="{y + 78 + j * 21}" font-family="{SANS}" font-size="14" fill="{t["mute"]}">{escape(ln)}</text>'
        lang = r.get("language") or ""
        when = datetime.strptime(r["pushed_at"][:10], "%Y-%m-%d").strftime("%b %Y").upper()
        fx = x + 24
        if lang:
            b += f'<circle cx="{fx + 5}" cy="{y + 129}" r="5" fill="{LANG.get(lang, t["faint"])}"/>'
            b += mono(fx + 18, y + 133, escape(lang.upper()), t["faint"], size=10, ls=1.6)
        b += mono(x + 344, y + 133, when, t["faint"], size=10, ls=1.6, anchor="end")
        b += "</g>"
    return svg(h, b, t, "Latest repositories: " + ", ".join(r["name"] for r in repos))


def latest_links(repos):
    return " &nbsp;·&nbsp; ".join(f'<a href="{r["html_url"]}">{pretty(r["name"])}</a>' for r in repos)


def write_latest(repos):
    for theme, t in THEMES.items():
        open(f"assets/latest-{theme}.svg", "w").write(latest(t, repos))
    md = open("README.md").read()
    block = ("<!-- LATEST:START -->\n"
             '<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="./assets/latest-dark.svg">\n'
             '  <img alt="Latest repositories" src="./assets/latest-light.svg" width="100%">\n</picture>\n\n'
             f'<p align="center"><sub>{latest_links(repos)}</sub></p>\n'
             "<!-- LATEST:END -->")
    md = re.sub(r"<!-- LATEST:START -->.*?<!-- LATEST:END -->", block, md, flags=re.S)
    open("README.md", "w").write(md)


if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    if "--latest" in sys.argv:
        src = sys.argv[sys.argv.index("--latest") + 1] if len(sys.argv) > sys.argv.index("--latest") + 1 else None
        write_latest(json.load(open(src)) if src else fetch_repos())
    else:
        for theme, t in THEMES.items():
            for fn, part in [("header", header), ("numbers", numbers), ("expertise", expertise), ("path", path)]:
                open(f"assets/{fn}-{theme}.svg", "w").write(part(t))
