"""Build the Beanhop.com static site from the Shopify blog export.

Outputs:
  site/      full HTML documents, ready for GitHub Pages
  preview/   same site, but index.html as a fragment for the Claude artifact preview
"""
import json, re, os, html, shutil, datetime
from bs4 import BeautifulSoup

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
BLOG = "blogs/industry-insights"

FEATURED = [
    "ai-is-not-weightless",
    "unpacking-the-truths-and-myths-about-ai-what-you-need-to-know",
    "navigating-the-ethical-landscape-of-ai-with-bean-hop-consulting",
    "how-ai-turned-our-holiday-card-into-a-festive-masterpiece",
    "elevate-your-business-website-with-better-photography",
    "making-lemonade-out-of-lemons-how-ai-can-help-turn-work-mistakes-into-opportunities",
    "ai-can-speed-up-analysis-but-human-touch-remains-irreplaceable",
]
MORE = [
    "eco-friendly-ai-innovations-a-beacon-for-island-ecosystems",
    "ai-resources-for-insight-and-learning",
    "embracing-ai-for-more-beach-time-a-simple-guide",
    "the-power-of-starting-why-action-fuels-motivation",
    "leveraging-ai-in-search-to-boost-your-remote-island-business",
]
ISLAND = [
    "the-tunnel-pass-uniting-virgin-islanders-across-the-globe",
    "paradise-found-a-journey-to-the-enchanting-virgin-islands",
    "crafting-unforgettable-journeys-a-marketing-guide-for-charter-boat-companies-in-the-british-virgin-islands",
    "the-ultimate-guide-to-music-for-your-virgin-islands-event-ai-playlists-vs-local-djs",
]

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Graduate&family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700;12..96,800'
         '&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=IBM+Plex+Mono:wght@400;500&display=swap">')

IMG_GUARD = ("<script>document.querySelectorAll('img').forEach(function(i){var h=function(){i.remove()};"
             "if(i.complete&&i.naturalWidth===0)h();else i.addEventListener('error',h)});</script>")

posts = {a["handle"]: a for a in json.load(open(os.path.join(SRC, "articles.json")))["data"]["articles"]["nodes"]}
images = []  # (page, url)


def esc(s):
    return html.escape(s or "", quote=True)


def fix_url(u):
    return "https:" + u if u.startswith("//") else u


def date_of(a):
    return datetime.datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00"))


def text_of(h):
    return re.sub(r"\s+", " ", BeautifulSoup(h or "", "html.parser").get_text(" ")).strip()


def excerpt(a, n=150):
    t = text_of(a["summary"]) if a.get("summary") else ""
    if not t:
        t = text_of(a["body"])
    if len(t) > n:
        t = t[:n].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
    return t


BODY_SWAP = {
    "eco-friendly-ai-innovations-a-beacon-for-island-ecosystems": [("Caribbean_Virgin_Islands_infographic", None)],
    "the-ultimate-guide-to-music-for-your-virgin-islands-event-ai-playlists-vs-local-djs": [("An_imaginative_scene", "ai-dj-vs-local-dj.jpg")],
}


def clean_body(h, handle, root=""):
    s = BeautifulSoup(h, "html.parser")
    for t in s(["meta", "script", "style", "iframe", "link"]):
        t.decompose()
    for t in s.find_all(["span", "font", "div", "section", "o:p"]):
        t.unwrap()
    for t in s.find_all("h1"):
        t.name = "h2"
    for t in s.find_all(True):
        keep = {"a": ["href"], "img": ["src", "alt"], "td": ["colspan", "rowspan"], "th": ["colspan", "rowspan"]}.get(t.name, [])
        t.attrs = {k: v for k, v in t.attrs.items() if k in keep}
        if t.name == "img":
            t["src"] = fix_url(t.get("src", ""))
            swap = next((f for key, f in BODY_SWAP.get(handle, []) if key in t["src"]), "keep")
            if swap is None:
                t.decompose()
                continue
            if swap != "keep":
                t["src"] = f"{root}images/{swap}"
                t["loading"] = "lazy"
                t["alt"] = t.get("alt", "")
                continue
            t["loading"] = "lazy"
            t["alt"] = t.get("alt", "")
            images.append((handle, t["src"]))
        if t.name == "a" and t.get("href", "").startswith("http") and "beanhop.com" not in t["href"]:
            t["target"] = "_blank"
            t["rel"] = "noopener"
    for p in s.find_all(["p", "li", "h2", "h3", "h4"]):
        if not p.get_text(strip=True) and not p.find("img"):
            p.decompose()
    for br in s.find_all("br"):
        if br.next_sibling is None or (isinstance(br.next_sibling, str) and not br.next_sibling.strip() and br.next_sibling.next_sibling is None):
            br.decompose()
    return str(s).strip()


def header(root, home=False):
    p = "" if home else root + "index.html"
    return (f'<header class="top"><a class="brand" href="{root}index.html" aria-label="Bean Hop home"><img class="mark" src="{root}images/bean-mark.png" alt="" width="212" height="240"><span class="bh-word">bean hop<small>a leap of strategy</small></span></a>'
            f'<nav aria-label="Sections"><a href="{p}#work">Work</a><a href="{root}{BLOG}/index.html">Writing</a>'
            f'<a href="{p}#about">About</a><a href="{p}#contact">Contact</a></nav></header>')


def footer(root):
    return '<footer>© 2026 Bean Hop Consulting, LLC</footer>'


ISLAND_SITE = "https://islandviator.com"


def redirect_stub(h):
    target = f"{ISLAND_SITE}/stories/{h}/"
    t = esc(posts[h]["title"])
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
            f"<title>{t}</title><link rel=\"canonical\" href=\"{target}\">"
            f"<meta http-equiv=\"refresh\" content=\"0; url={target}\"></head>"
            f"<body><p>This story moved to <a href=\"{target}\">Island Viator</a>.</p></body></html>\n")


def doc(title, desc, root, body, fragment=False):
    head = (f"<title>{esc(title)}</title><meta name=\"description\" content=\"{esc(desc)}\">{FONTS}"
            f'<link rel="stylesheet" href="{root}style.css">')
    if fragment:
        return head + "\n" + body + IMG_GUARD + "\n"
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            f"{head}\n</head>\n<body>\n{body}{IMG_GUARD}\n</body>\n</html>\n")


def post_rows(handles, root):
    rows = []
    for h in sorted(handles, key=lambda h: date_of(posts[h]), reverse=True):
        a = posts[h]
        rows.append(f'<a class="post-row" href="{root}{BLOG}/{h}/index.html"><span class="pd">{date_of(a):%b %Y}</span>'
                    f'<span><span class="pt">{esc(a["title"])}</span><span class="px">{esc(excerpt(a))}</span></span></a>')
    return '<div class="posts">' + "".join(rows) + "</div>"


LOCAL_FEAT = {
    "eco-friendly-ai-innovations-a-beacon-for-island-ecosystems": "eco-ai-coral-infographic.jpg",
    "unpacking-the-truths-and-myths-about-ai-what-you-need-to-know": "truths-and-myths-ai.jpg",
    "elevate-your-business-website-with-better-photography": "rule-of-thirds-modern-home.jpg",
    "navigating-the-ethical-landscape-of-ai-with-bean-hop-consulting": "ai-ethics-teams.jpg",
    "how-ai-turned-our-holiday-card-into-a-festive-masterpiece": "holiday-card-nativity.jpg",
}


def article(a, h, root, back, hdr, ftr):
    feat = ""
    if h in LOCAL_FEAT:
        feat = f'<img class="feature" src="{root}images/{LOCAL_FEAT[h]}" alt="">'
    elif a.get("image"):
        u = fix_url(a["image"]["url"])
        images.append((h, u))
        feat = f'<img class="feature" src="{esc(u)}" alt="{esc(a["image"].get("altText") or "")}">'
    words = len(text_of(a["body"]).split())
    return (f'<div class="wrap">{hdr}<article><div class="article-head"><span class="crumb">{back}</span>'
            f'<h1>{esc(a["title"])}</h1><span class="byline">Ashley Schultz · {date_of(a):%B %-d, %Y} · {max(1, round(words / 230))} min read</span></div>'
            f'{feat}<div class="prose">{clean_body(a["body"], h, root)}</div>'
            f'<div class="article-foot"><span class="crumb">{back}</span></div></article>{ftr}</div>')


def post_page(h):
    a, root = posts[h], "../../../"
    back = f'<a href="{root}{BLOG}/index.html">← All writing</a>'
    return doc(a["title"] + " | Bean Hop", excerpt(a, 155), root, article(a, h, root, back, header(root), footer(root)))


def writing_page():
    root = "../../"
    body = (f'<div class="wrap">{header(root)}<section><div class="sec-head"><span class="label">Writing</span>'
            f'<h2>Industry Insights</h2><p>Notes on using AI well: what it costs, where it helps, where it fails, and how design and good judgment fit in.</p></div>'
            f'{post_rows(FEATURED + MORE, root)}</section>{footer(root)}</div>')
    return doc("Writing | Bean Hop", "Articles by Ashley Schultz on AI, design and responsible technology.", root, body)


def home(fragment):
    b = open(os.path.join(SRC, "home_body.html")).read()
    b = b[b.index("</header>") + len("</header>"):]
    b = '<div class="wrap">' + header("", home=True) + b
    writing = ('<section id="writing"><div class="sec-head"><span class="label">Writing</span><h2>Recent articles</h2></div>'
               + post_rows(FEATURED[:5], "") +
               f'<a class="more" href="{BLOG}/index.html">All writing →</a></section>')
    b = b.replace('<section id="about">', writing + '<section id="about">', 1)
    b = re.sub(r"<footer>.*?</footer>", footer(""), b, flags=re.S)
    return doc("Bean Hop Consulting", "Ashley Schultz is a UX/UI product designer who builds with AI and teaches teams to use it responsibly.", "", b, fragment)


# ---------------- Island Viator (separate site) ----------------

IV_FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Rubik:wght@500;700;800'
            '&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">')

IV_TOKENS = """
/* Island Viator: sea-spray ground, deep-water ink, accent taken from the newest pass (Bright Violet) */
:root {
  --bg: #F1F7FA; --surface: #FFFFFF; --ink: #0E2A3B; --muted: #4A6475; --line: #CFE0E8;
  --accent: #6A3FCC; --accent-soft: #E6DEFA; --sun: #F28A2E;
  --display: "Rubik", "Arial Black", system-ui, sans-serif;
  --body: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0A1C27; --surface: #112836; --ink: #E4EFF4; --muted: #94AEBC; --line: #21404F;
  --accent: #A98BF2; --accent-soft: #2A2450; --sun: #F5A55C; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #0A1C27; --surface: #112836; --ink: #E4EFF4; --muted: #94AEBC; --line: #21404F;
  --accent: #A98BF2; --accent-soft: #2A2450; --sun: #F5A55C; color-scheme: dark; }
.stripe { height: 6px; border-radius: 3px; background: linear-gradient(90deg, #5FC9B5 0 14%, #7DB8E8 14% 28%, #1FA66B 28% 42%, #F28A2E 42% 56%, #C9302C 56% 70%, #5FC9B5 70% 85%, #7B4FD6 85% 100%); margin-bottom: 2rem; }
.brand { font-weight: 800; letter-spacing: .01em; }
"""


def iv_header(root):
    return (f'<div class="stripe" aria-hidden="true"></div><header class="top"><a class="brand" href="{root}index.html" '
            f'style="text-decoration:none;color:inherit">Island Viator<span>.</span></a>'
            f'<nav aria-label="Sections"><a href="{root}index.html#passes">Tunnel Passes</a><a href="{root}index.html#stories">Stories</a></nav></header>')


def iv_footer():
    return '<footer>© 2026 Bean Hop Consulting, LLC · Island Viator is a brand of Bean Hop Consulting, LLC</footer>'


def iv_doc(title, desc, root, body, fragment=False):
    head = (f"<title>{esc(title)}</title><meta name=\"description\" content=\"{esc(desc)}\">{IV_FONTS}"
            f'<link rel="stylesheet" href="{root}style.css">')
    if fragment:
        return head + "\n" + body + IMG_GUARD + "\n"
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            f"{head}\n</head>\n<body>\n{body}{IMG_GUARD}\n</body>\n</html>\n")


def iv_rows(root):
    rows = []
    for h in sorted(ISLAND, key=lambda h: date_of(posts[h]), reverse=True):
        a = posts[h]
        rows.append(f'<a class="post-row" href="{root}stories/{h}/index.html"><span class="pd">{date_of(a):%b %Y}</span>'
                    f'<span><span class="pt">{esc(a["title"])}</span><span class="px">{esc(excerpt(a))}</span></span></a>')
    return '<div class="posts">' + "".join(rows) + "</div>"


PASSES = [
    ("2009–2010", "Seafoam Aqua", "#5FC9B5", "The original"),
    ("2011–2012", "Sky Blue", "#7DB8E8", ""),
    ("2013–2014", "Caribbean Green", "#1FA66B", ""),
    ("2015–2016", "Orange", "#F28A2E", ""),
    ("2017–2018", "Red Habanero", "#C9302C", ""),
    ("2019–2020", "Tunnel closed", None, ""),
    ("2021–2022", "Seafoam Aqua", "#5FC9B5", ""),
    ("2023–2024", "Bright Violet", "#7B4FD6", ""),
]


def iv_home(fragment):
    cards = []
    for yr, name, col, note in PASSES:
        cls = "pass closed" if col is None else "pass"
        style = "" if col is None else f' style="--c:{col}"'
        cards.append(f'<div class="{cls}"{style}><div class="sw"></div><div class="pi"><span class="py">{yr}</span>'
                     f'<span class="pc">{name}</span>{f"<span class=label>{note}</span>" if note else ""}</div></div>')
    body = (f'<div class="wrap">{iv_header("")}'
            f'<div class="iv-hero"><span class="label">Miami ⇄ St. Thomas · Since 2009</span>'
            f'<h1>The Tunnel Pass</h1>'
            f'<p>It started in 2009 as a joke: a toll pass for an imaginary tunnel between Miami and St. Thomas. '
            f'It turned into a small badge of home for Virgin Islanders, wherever they live now.</p></div>'
            f'<section id="passes"><div class="sec-head"><span class="label">Every two years, a new color</span><h2>The passes</h2>'
            f'<p>A new pass comes out every two years, changing color the way registration stickers do. '
            f'In 2019–2020 the tunnel was closed, and there was no pass.</p></div>'
            f'<div class="passes">{"".join(cards)}</div>'
            f'<p class="note">Passes, prints and Island Viator gear aren\'t sold online right now. '
            f'If you\'d like one, email <code>support@beanhop.com</code>.</p></section>'
            f'<section id="stories"><div class="sec-head"><span class="label">From the islands</span><h2>Stories</h2></div>'
            f'{iv_rows("")}</section>{iv_footer()}</div>')
    return iv_doc("Island Viator", "The Tunnel Pass and other Virgin Islands stories.", "", body, fragment)


def iv_post(h):
    a, root = posts[h], "../../"
    back = f'<a href="{root}index.html#stories">← All stories</a>'
    return iv_doc(a["title"] + " | Island Viator", excerpt(a, 155), root, article(a, h, root, back, iv_header(root), iv_footer()))


# ---------------- build ----------------

def write_site(out, css, index_html, pages, cname=None, with_images=False):
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    open(os.path.join(out, "style.css"), "w").write(css)
    open(os.path.join(out, "index.html"), "w").write(index_html)
    for p, c in pages.items():
        os.makedirs(os.path.join(out, os.path.dirname(p)), exist_ok=True)
        open(os.path.join(out, p), "w").write(c)
    if cname:
        open(os.path.join(out, "CNAME"), "w").write(cname + "\n")
    if with_images:
        shutil.copytree(os.path.join(SRC, with_images if isinstance(with_images, str) else "images"), os.path.join(out, "images"))


base = open(os.path.join(SRC, "base.css")).read() + open(os.path.join(SRC, "extra.css")).read()
bh_pages = {f"{BLOG}/index.html": writing_page()}
for h in FEATURED + MORE:
    bh_pages[f"{BLOG}/{h}/index.html"] = post_page(h)
for h in ISLAND:
    bh_pages[f"{BLOG}/{h}/index.html"] = redirect_stub(h)
iv_pages = {f"stories/{h}/index.html": iv_post(h) for h in ISLAND}
iv_css = base + IV_TOKENS

write_site(os.path.join(ROOT, "site"), base, home(False), bh_pages, "beanhop.com", True)
write_site(os.path.join(ROOT, "preview"), base, home(True), bh_pages, None, True)
write_site(os.path.join(ROOT, "iv-site"), iv_css, iv_home(False), iv_pages, "islandviator.com", "iv-images")
write_site(os.path.join(ROOT, "iv-preview"), iv_css, iv_home(True), iv_pages, None, "iv-images")

seen, lines = set(), ["# Images still hosted on Shopify", "", "Save these before canceling the store.", ""]
for h, u in images:
    if u not in seen:
        seen.add(u)
        lines.append(f"- {posts[h]['title']}: {u}")
open(os.path.join(ROOT, "IMAGES-TO-SAVE.md"), "w").write("\n".join(lines) + "\n")
print("beanhop:", len(bh_pages) + 1, "pages; islandviator:", len(iv_pages) + 1, "pages;", len(seen), "images")
