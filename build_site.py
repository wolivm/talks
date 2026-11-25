#!/usr/bin/env python3
"""Builds the public talks site (GitHub Pages, repo wolivm/talks) from slide exports and the films.

Each talk page: slides in order (click-step copies and skipped slides already left out), each film playing where it
sits in the deck, a Present mode (arrows, swipe, full screen), the PDF, and the sources where the talk cites any.
Run: python3 build_site.py <shots_dir> <scratch_dir>
"""
import glob, html, json, os, shutil, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS, SCR = sys.argv[1], sys.argv[2]
ROOT = "/Users/willian/Documents/Windows/Andela-Agentic-AI/meetup-talk"

TALKS = [
    {
        "slug": "plugin-to-pipeline",
        "title": "From plugin to pipeline",
        "subtitle": "Three levels of content design automation",
        "event": "Berlin Content Design Meetup · October 2026",
        "ids": open(f"{SCR}/p2p-ids.txt").read().split(),
        "drop": [],  # filled in below from the review
        "videos": {
            "2:70": ("wiki-path.mp4", f"{ROOT}/renders/wiki-path.mp4", False),
            "2:129": ("proofie-demo.mp4", f"{SCR}/proofie-demo.mp4", False),
            "50:146": ("plugin-how-to.mp4", f"{ROOT}/renders/plugin-how-to.mp4", False),
            "35:2": ("skill-how-to.mp4", f"{ROOT}/renders/skill-how-to.mp4", False),
            "37:21": ("context-bleeding.mp4", f"{ROOT}/renders/context-bleeding.mp4", False),
            "2:270": ("pipeline-how-to.mp4", f"{ROOT}/renders/pipeline-how-to.mp4", False),
            "50:191": ("content-pipeline.mp4", f"{ROOT}/renders/content-pipeline.mp4", False),
            "62:206": ("closing-thank-you.mp4", f"{ROOT}/renders/closing-thank-you.mp4", True),
        },
        "sources": [],
    },
    {
        "slug": "agents-automation-design-systems",
        "title": "Agents, Automation and Design Systems",
        "subtitle": "with AI",
        "event": "Berlin Product Designers Meetup #46 · Raisin, Berlin · 12 November 2026",
        "ids": open(f"{SCR}/bpd46-ids.txt").read().split(),
        "drop": [],
        "videos": {"10:110": ("agent-flow.mp4", f"{ROOT}/renders/agent-flow.mp4", False)},
        "sources": [
            ("Research and reports", [
                ("Building effective agents", "Erik Schluntz & Barry Zhang · Anthropic blog · December 2024", "https://www.anthropic.com/research/building-effective-agents"),
                ("Economic Index: Uneven AI adoption", "Anthropic · September 2025", "https://www.anthropic.com/research/anthropic-economic-index-september-2025-report"),
                ("Economic Index: AI's impact on software development", "Anthropic · 2025", "https://www.anthropic.com/research/impact-software-development"),
                ("Design System-Compliant User Interface Generation with LLM Agents", "Cha, Jo, Shin & Seo · CHI 2026 Extended Abstracts", "https://doi.org/10.1145/3772363.3798616"),
                ("Paper MCP vs Figma MCP for frontend agents", "Jess Wang · Braintrust · July 2026", "https://www.braintrust.dev/evals/paper-vs-figma-mcp"),
                ("TaoD2C-Bench", "Shi et al. · arXiv preprint · October 2026", "https://arxiv.org/abs/2610.10374"),
                ("Prompt to Design Interfaces", "Huei-Hsin Wang · Nielsen Norman Group · December 2025", "https://www.nngroup.com/articles/vague-prototyping/"),
            ]),
            ("Tools I used", [
                ("Claude Code", "The design agent and the auditor", "https://claude.com/claude-code"),
                ("Figma MCP server", "How the agents read and build in Figma", "https://developers.figma.com/docs/figma-mcp-server/"),
                ("n8n", "The workflow between Telegram and the agent", "https://n8n.io"),
                ("Remotion", "The films in the talk", "https://www.remotion.dev"),
            ]),
        ],
    },
]
review = f"{SCR}/drop.json"
if os.path.exists(review):
    d = json.load(open(review))
    for t in TALKS: t["drop"] = d.get(t["slug"], [])

CSS = open(os.path.join(HERE, "site.css")).read()
JS = open(os.path.join(HERE, "deck.js")).read()
E = html.escape

def shot(nid):
    hits = glob.glob(f"{SHOTS}/*/{nid.replace(':', '-')}.png")
    if not hits: raise SystemExit("missing shot " + nid)
    im = Image.open(hits[0]).convert("RGB")
    return im if im.size == (1920, 1080) else im.resize((1920, 1080), Image.LANCZOS)

def head(title, desc):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&display=swap"><style>{CSS}</style></head><body>"""

FOOT = """<footer class="foot"><span>Willian Magalhães · Content &amp; Conversation Designer</span>
<a href="https://www.linkedin.com/in/uxwillian/">linkedin.com/in/uxwillian</a><a href="https://arara.school/en/">arara.school/en</a></footer>"""

cards = []
for t in TALKS:
    out = os.path.join(HERE, t["slug"]); shutil.rmtree(out, ignore_errors=True)
    os.makedirs(f"{out}/slides"); os.makedirs(f"{out}/video")
    items, pdf_pages = [], []
    ids = [i for i in t["ids"] if i not in t["drop"]]
    for n, nid in enumerate(ids, 1):
        im = shot(nid)
        jpg = f"slides/s{n:02d}.jpg"
        im.resize((1600, 900), Image.LANCZOS).save(f"{out}/{jpg}", quality=82, optimize=True)
        if nid in t["videos"]:
            name, src, loop = t["videos"][nid]
            shutil.copyfile(src, f"{out}/video/{name}")
            poster = f"slides/p{n:02d}.jpg"  # a frame from the film, since the slide shot only shows the player
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1.5", "-i", src, "-frames:v", "1", "-vf", "scale=1600:-2", "-q:v", "4", f"{out}/{poster}"], check=True)
            items.append({"type": "video", "src": f"video/{name}", "poster": poster, "loop": loop})
        else:
            items.append({"type": "img", "src": jpg})
            pdf_pages.append(im)
    pdf = f"{t['slug']}.pdf"
    pdf_pages[0].save(f"{out}/{pdf}", save_all=True, append_images=pdf_pages[1:], resolution=144, quality=85)
    vids = sum(1 for x in items if x["type"] == "video")
    figs = []
    for n, it in enumerate(items, 1):
        if it["type"] == "img":
            media = f'<img src="{it["src"]}" alt="Slide {n}" width="1600" height="900" loading="{"eager" if n < 3 else "lazy"}" decoding="async">'
        else:
            extra = ' loop muted autoplay' if it["loop"] else ''
            media = f'<video controls playsinline preload="none" poster="{it["poster"]}"{extra} width="1600" height="900"><source src="{it["src"]}" type="video/mp4"></video>'
        figs.append(f'<figure class="slide" id="s{n}">{media}<figcaption>{n} / {len(items)}{" · film" if it["type"] == "video" else ""}</figcaption></figure>')
    src_html = ""
    if t["sources"]:
        groups = "".join(f'<div class="group"><h3>{E(g)}</h3>' + "".join(f'<div class="src"><a href="{u}">{E(a)}</a><span class="meta">{E(m)}</span></div>' for a, m, u in rows) + "</div>" for g, rows in t["sources"])
        src_html = f'<section class="sources" id="sources"><h2>Sources</h2><p class="note">Everything I mentioned in the talk.</p>{groups}</section>'
    page = head(t["title"] + " · Willian Magalhães", f"{t['title']}: {t['subtitle']}. {t['event']}.") + f"""
<main class="wrap">
  <p class="crumb"><a href="../">All talks</a></p>
  <header class="intro">
    <p class="eyebrow">{E(t["event"])}</p>
    <h1>{E(t["title"])} <em>{E(t["subtitle"])}</em></h1>
    <p class="byline">Willian Magalhães</p>
    <div class="actions"><button class="btn" id="present" type="button">Present ▶</button><a class="ghost" href="{pdf}" download>Download the PDF</a>{'<a class="ghost" href="#sources">Sources</a>' if t["sources"] else ''}</div>
    <p class="note">{len(items)} slides, {vids} film{"s" if vids != 1 else ""} with sound. Click-by-click builds are shown as one finished slide.</p>
  </header>
  <section class="deck">{"".join(figs)}</section>
  {src_html}
  {FOOT}
</main>
<div class="stage" id="stage" hidden><div class="frame" id="frame"></div><div class="bar"><button type="button" id="prev" aria-label="Previous slide">←</button><span id="count"></span><button type="button" id="next" aria-label="Next slide">→</button><button type="button" id="close" aria-label="Close">✕</button></div></div>
<script>const ITEMS = {json.dumps(items)};
{JS}</script></body></html>"""
    open(f"{out}/index.html", "w").write(page)
    cards.append(f'<a class="card" href="{t["slug"]}/"><img src="{t["slug"]}/slides/s01.jpg" alt="" width="1600" height="900"><span class="eyebrow">{E(t["event"])}</span><span class="ctitle">{E(t["title"])} <em>{E(t["subtitle"])}</em></span><span class="meta">{len(items)} slides · {vids} film{"s" if vids != 1 else ""}</span></a>')
    print(t["slug"], len(items), "items", vids, "videos", round(os.path.getsize(f"{out}/{pdf}") / 1e6, 1), "MB pdf")

index = head("Talks · Willian Magalhães", "Slides and films from Willian Magalhães's talks on content design, design systems and AI agents.") + f"""
<main class="wrap"><header class="intro"><p class="eyebrow">Talks</p><h1>Willian Magalhães <em>talks</em></h1>
<p class="byline">Content &amp; Conversation Designer at DEPT, Director at Arara School. The slides and films from my talks, free to watch.</p></header>
<section class="cards">{"".join(reversed(cards))}</section>{FOOT}</main></body></html>"""
open(os.path.join(HERE, "index.html"), "w").write(index)
open(os.path.join(HERE, ".nojekyll"), "w").write("")
