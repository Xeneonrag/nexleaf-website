#!/usr/bin/env python3
"""Builds the Nexleaf website from src/ into _site/.

    python build.py            published pages only (what GitHub Pages deploys)
    python build.py --drafts   also builds pages marked "status: draft", with a banner (local preview)

Each file in src/pages/ starts with a comment block of settings:

    <!--
    title: Privacy Policy
    description: One sentence for search engines.
    layout: legal            (home | legal | page)
    status: published        (published | draft)
    updated: November 16, 2026
    -->

The build fails if a published page still has a review note (<mark class="review">),
or if any page links to a page or file that doesn't exist.
"""
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "_site"
DRAFTS = "--drafts" in sys.argv

site = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
template = (SRC / "template.html").read_text(encoding="utf-8")
base_path = urlparse(site["base_url"]).path  # "/nexleaf-website/"


def read_page(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\s*<!--(.*?)-->", text, re.S)
    if not match:
        sys.exit(f"{path.name}: missing the settings comment at the top")
    meta = {}
    for line in match.group(1).strip().splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    meta["slug"] = path.stem
    meta["body"] = text[match.end():].strip()
    return meta


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", text).lower()).strip("-")


def add_heading_ids(body):
    """Gives every <h2> an id and returns the body plus a table of contents."""
    entries = []

    def repl(m):
        ident = slugify(m.group(1))
        entries.append((ident, re.sub(r"<[^>]+>", "", m.group(1))))
        return f'<h2 id="{ident}">{m.group(1)}</h2>'

    body = re.sub(r"<h2>(.*?)</h2>", repl, body, flags=re.S)
    toc = "\n".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in entries)
    return body, toc


def store_button(label, small, url):
    if url:
        return f'<a class="store-btn" href="{html.escape(url)}"><small>{small}</small>{label}</a>'
    return f'<span class="store-btn is-soon" aria-disabled="true"><small>Coming soon to</small>{label}</span>'


def render_games(root):
    cards = []
    for g in site["games"]:
        features = "".join(f"<li>{html.escape(f)}</li>" for f in g.get("features", []))
        shots = "".join(
            f'<img src="{root}{html.escape(s)}" alt="{html.escape(g["name"])} screenshot" loading="lazy">'
            for s in g.get("screenshots", []))
        gallery = f'<div class="shots">{shots}</div>' if shots else ""
        cards.append(f"""
<article class="game reveal">
  <div class="game-art">
    <div class="phone"><img src="{root}{g['art']}" alt="{html.escape(g.get('art_alt', g['name']))}" width="640" height="1137"></div>
  </div>
  <div class="game-info">
    <div class="game-head">
      <img class="game-icon" src="{root}{g['icon']}" alt="" width="72" height="72">
      <div>
        <p class="eyebrow">{html.escape(g['genre'])}</p>
        <h3>{html.escape(g['name'])}</h3>
      </div>
    </div>
    <p class="badges"><span class="badge badge-live">{html.escape(g['status'])}</span><span class="badge">{html.escape(g['platforms'])}</span></p>
    <p class="lead">{html.escape(g['description'])}</p>
    <ul class="ticks">{features}</ul>
    <div class="stores">
      {store_button("Google Play", "Get it on", g.get("google_play_url", ""))}
      {store_button("App Store", "Download on the", g.get("app_store_url", ""))}
    </div>
  </div>
</article>{gallery}""")
    return "\n".join(cards)


def links(items, root, built, home):
    out = []
    for item in items:
        if "slug" in item:
            if item["slug"] not in built:
                continue
            href = f'{root}{item["slug"]}/'
        else:
            href = item["href"] if home else root + item["href"]
        out.append(f'<a href="{href}">{html.escape(item["label"])}</a>')
    return "\n".join(out)


def legal_cards(root, built):
    out = []
    for item in site["footer_legal"]:
        if item["slug"] in built:
            out.append(f'<a class="card reveal" href="{root}{item["slug"]}/"><h3>{html.escape(item["label"])}</h3>'
                       f'<p>{html.escape(item.get("blurb", ""))}</p><span class="arrow">Read &rarr;</span></a>')
        else:
            out.append(f'<div class="card card-soon reveal"><h3>{html.escape(item["label"])}</h3>'
                       f'<p>{html.escape(item.get("blurb", ""))}</p><span class="arrow muted">Coming soon</span></div>')
    return "\n".join(out)


pages = [read_page(p) for p in sorted((SRC / "pages").glob("*.html"))]
skipped = [p["slug"] for p in pages if p.get("status") == "draft" and not DRAFTS]
pages = [p for p in pages if p["slug"] not in skipped]
built = {p["slug"] for p in pages}
errors = []
written = []

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SRC / "assets", OUT / "assets")
(OUT / ".nojekyll").write_text("", encoding="utf-8")

for page in pages:
    slug = page["slug"]
    is_draft = page.get("status") == "draft"
    home = slug == "index"
    if slug == "index":
        target, root = OUT / "index.html", "./"
    elif slug == "404":
        target, root = OUT / "404.html", base_path  # served from any depth, so links are absolute
    else:
        target, root = OUT / slug / "index.html", "../"

    body, toc = add_heading_ids(page["body"])
    if not is_draft and 'class="review"' in body:
        errors.append(f"{slug}: is marked published but still has review notes (<mark class=\"review\">)")

    layout = page.get("layout", "page")
    updated = page.get("updated", "")
    if layout == "legal":
        body = f"""
<div class="doc-wrap">
  <aside class="toc"><p class="toc-title">On this page</p><ol>{toc}</ol></aside>
  <article class="doc">
    <header class="doc-head">
      <p class="eyebrow">{html.escape(page.get('kicker', 'Dicebound · Nexleaf'))}</p>
      <h1>{page['title']}</h1>
      {f'<p class="updated">Last updated: {updated}</p>' if updated else ''}
    </header>
    {body}
  </article>
</div>"""
    elif layout == "page":
        body = f'<article class="doc doc-narrow"><header class="doc-head"><p class="eyebrow">{html.escape(page.get("kicker", "Nexleaf"))}</p><h1>{page["title"]}</h1></header>{body}</article>'

    banner = ""
    if is_draft:
        banner = '<div class="draft-banner">Draft preview. This page is waiting for approval and is not published.</div>'
    elif site.get("announcement") and home:
        banner = f'<div class="announce">{site["announcement"]}</div>'

    title = page["title"] if home else f'{page["title"]} | {site["studio"]}'
    canonical = site["base_url"] + ("" if home else f"{slug}/")
    out = template
    values = {
        "content": body,
        "banner": banner,
        "nav": links(site["nav"], root, built, home),
        "footer_legal": links(site["footer_legal"], root, built, home),
        "games": render_games(root),
        "legal_cards": legal_cards(root, built),
        "title": title,
        "description": html.escape(page.get("description", "")),
        "canonical": canonical,
        "robots": '<meta name="robots" content="noindex">' if is_draft or slug == "404" else "",
        "root": root,
        "email": site["email"],
        "studio": site["studio"],
        "tagline": site["tagline"],
        "year": str(date.today().year),
    }
    for _ in range(2):  # twice, so values inside the page content are filled in too
        for key, value in values.items():
            out = out.replace("{{" + key + "}}", value)
    leftover = re.findall(r"\{\{\w+\}\}", out)
    if leftover:
        errors.append(f"{slug}: unknown placeholder {leftover[0]}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")
    written.append((slug, target, out))

# Every local link and image must exist.
for slug, target, out in written:
    for ref in sorted(set(re.findall(r'(?:href|src)="([^"#]+)(?:#[^"]*)?"', out))):
        if re.match(r"(https?:|mailto:|data:)", ref):
            continue
        if ref.startswith("/"):
            dest = OUT / ref[len(base_path):] if ref.startswith(base_path) else None
        else:
            dest = (target.parent / ref).resolve()
        if dest is None or not (dest.is_file() or (dest / "index.html").is_file()):
            errors.append(f"{slug}: broken link or missing file: {ref}")

if errors:
    print("BUILD FAILED")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print(f"Built {len(pages)} pages into {OUT.name}/ : " + ", ".join(sorted(built)))
if skipped:
    print("Left out (status: draft): " + ", ".join(skipped))
