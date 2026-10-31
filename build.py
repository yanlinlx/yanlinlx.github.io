#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — generate the static academic homepage from ./data/*.json

    python build.py

Everything you normally edit lives in ./data/. After each edit, re-run this
script: it rewrites index.html, publications.html, projects.html and
videos.html, which are exactly the files GitHub Pages serves.

No third-party packages required — standard library only.
"""

import html
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

NAV = [
    ("index.html", "About"),
    ("publications.html", "Publications"),
    ("projects.html", "Projects"),
    ("cv.html", "Honours"),
    ("studentlife.html", "Student Life"),
]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def load(name):
    with open(DATA / name, "r", encoding="utf-8") as fh:
        return json.load(fh)


def esc(value):
    return html.escape(str(value), quote=True)


def fill(template, **kw):
    """Tiny brace-safe template filler (so we never fight with CSS/JS braces)."""
    out = template
    for key, value in kw.items():
        out = out.replace("{{" + key + "}}", str(value))
    return out


def external_attrs(url):
    return ' target="_blank" rel="noopener"' if str(url).startswith("http") else ""


def link_pills(links, cls=None):
    out = []
    for item in links or []:
        url = item.get("url", "#")
        attr = ' class="%s"' % cls if cls else ""
        out.append(
            '<a%s href="%s"%s>%s</a>'
            % (attr, esc(url), external_attrs(url), esc(item.get("label", "Link")))
        )
    return "".join(out)


def render_authors(authors, me):
    parts = []
    for name in authors or []:
        if me and str(name).strip().lower() == str(me).strip().lower():
            parts.append("<strong>%s</strong>" % esc(name))
        else:
            parts.append(esc(name))
    return ", ".join(parts)


# --------------------------------------------------------------------------
# page chrome
# --------------------------------------------------------------------------

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}}</title>
<meta name="description" content="{{DESCRIPTION}}">
<meta name="author" content="{{AUTHOR}}">
<meta property="og:type" content="website">
<meta property="og:title" content="{{TITLE}}">
<meta property="og:description" content="{{DESCRIPTION}}">
<meta property="og:url" content="{{URL}}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/style.css">
<script type="application/ld+json">{{JSONLD}}</script>
<script>try{var t=localStorage.getItem("theme");if(t){document.documentElement.setAttribute("data-theme",t);}}catch(e){}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <div class="wrap topbar-inner">
    <a class="brand" href="index.html">{{BRAND}}</a>
    <nav class="nav">{{NAV}}</nav>
    <button class="theme-toggle" type="button" aria-label="Toggle colour theme">
      <svg class="i-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
      <svg class="i-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2v2.4M12 19.6V22M4.2 4.2l1.7 1.7M18.1 18.1l1.7 1.7M2 12h2.4M19.6 12H22M4.2 19.8l1.7-1.7M18.1 5.9l1.7-1.7"/></svg>
    </button>
  </div>
</header>
{{BODY}}
<footer class="footer">
  <div class="wrap">
    <p>© {{YEAR}} {{BRAND}}. Static site, hosted on GitHub Pages.</p>
    <p class="dim">Last built {{BUILT}}.</p>
  </div>
</footer>
<script src="assets/site.js"></script>
</body>
</html>
"""


def render_nav(active):
    out = []
    for href, label in NAV:
        cls = ' class="active"' if href == active else ""
        out.append("<a%s href=\"%s\">%s</a>" % (cls, href, esc(label)))
    return "".join(out)


def build_page(profile, active, page_title, body):
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Person",
        "name": profile.get("name", ""),
        "jobTitle": profile.get("role", ""),
        "affiliation": {"@type": "Organization", "name": profile.get("affiliation", "")},
        "url": profile.get("site_url", ""),
        "email": profile.get("email", ""),
        "knowsAbout": profile.get("interests", []),
    }, ensure_ascii=False)

    return fill(
        PAGE,
        TITLE=esc(page_title),
        DESCRIPTION=esc(profile.get("description", "")),
        AUTHOR=esc(profile.get("name", "")),
        URL=esc(profile.get("site_url", "")),
        JSONLD=jsonld,
        BRAND=esc(profile.get("name", "")),
        NAV=render_nav(active),
        BODY=body,
        YEAR=date.today().year,
        BUILT=date.today().isoformat(),
    )


# --------------------------------------------------------------------------
# fragments
# --------------------------------------------------------------------------

def render_sidebar(profile):
    name_zh = profile.get("name_zh", "")
    zh_line = '<p class="side-name-zh">%s</p>' % esc(name_zh) if name_zh else ""
    links = link_pills(profile.get("links", []), cls="link-pill")
    return """
<aside class="sidebar">
  <img class="avatar" src="{avatar}" alt="Portrait of {name}">
  <p class="side-name">{name}</p>
  {zh}
  <p class="side-role">{role}</p>
  <ul class="side-meta">
    <li><span>Affiliation</span><span>{affil}</span></li>
    <li><span>Location</span><span>{location}</span></li>
    <li><span>Email</span><span><a href="mailto:{email}">{email}</a></span></li>
  </ul>
  <div class="side-links">{links}</div>
</aside>
""".format(
        avatar=esc(profile.get("avatar", "assets/avatar.svg")),
        name=esc(profile.get("name", "")),
        zh=zh_line,
        role=esc(profile.get("role", "")),
        affil=esc(profile.get("affiliation", "")),
        location=esc(profile.get("location", "")),
        email=esc(profile.get("email", "")),
        links=links,
    )


def render_pub_item(pub, me):
    year = esc(pub.get("year", ""))
    title = esc(pub.get("title", ""))
    ptype = pub.get("type", "")
    badge = '<span class="pub-badge">%s</span>' % esc(ptype) if ptype else ""
    authors = render_authors(pub.get("authors", []), me)
    venue_line = "<em>%s</em>" % esc(pub.get("venue", ""))
    volume_pages = pub.get("volume_pages", "")
    if volume_pages:
        venue_line += " · " + esc(volume_pages)
    links = link_pills(pub.get("links", []))
    links_html = '<div class="pub-links">%s</div>' % links if links else ""
    return """<li class="pub">
  <div class="pub-year">{year}</div>
  <div>
    <p class="pub-title">{title}{badge}</p>
    <p class="pub-authors">{authors}</p>
    <p class="pub-venue">{venue}</p>
    {links}
  </div>
</li>""".format(year=year, title=title, badge=badge, authors=authors, venue=venue_line, links=links_html)


def render_entry_media(entry):
    """Render 0/1/2 watermarked photos for a student-life milestone.

    `entry` may carry `image` (single path) or `images` (list of paths).
    Missing files are skipped with a warning so a broken upload never
    breaks the build.
    """
    srcs = entry.get("images") or ([entry["image"]] if entry.get("image") else [])
    if not srcs:
        return ""
    figs = []
    for src in srcs:
        if not (ROOT / src).exists():
            sys.stderr.write("WARN build: student-life image not found, skipped: %s\n" % src)
            continue
        figs.append('<figure class="entry-media"><img loading="lazy" src="%s" alt="%s"></figure>'
                    % (esc(src), esc(entry.get("title", ""))))
    if not figs:
        return ""
    cls = "entry-media two" if len(figs) > 1 else "entry-media"
    return '<div class="%s">%s</div>' % (cls, "".join(figs))


def render_entry_list(entries):
    """CV timeline: each entry is {left, title, meta, details[], image?, images?}."""
    if not entries:
        return '<p class="empty">Nothing here yet.</p>'
    # only reserve the date column if at least one entry actually uses it
    has_left = any(entry.get("left") for entry in entries)
    items = []
    for entry in entries:
        left = ('<div class="entry-left">%s</div>' % entry["left"]) if has_left else ""
        meta = '<p class="entry-meta">%s</p>' % entry["meta"] if entry.get("meta") else ""
        details = entry.get("details") or []
        details_html = ('<ul class="entry-details">%s</ul>'
                        % "".join("<li>%s</li>" % d for d in details)) if details else ""
        media_html = render_entry_media(entry)
        items.append(
            '<li class="entry">%s<div><p class="entry-title">%s</p>%s%s%s</div></li>'
            % (left, entry.get("title", ""), meta, details_html, media_html)
        )
    cls = "entry-list" if has_left else "entry-list no-left"
    return '<ul class="%s">%s</ul>' % (cls, "".join(items))


def render_skills(skills):
    if not skills:
        return '<p class="empty">Nothing here yet.</p>'
    rows = []
    for skill in skills:
        items = "".join("<li>%s</li>" % esc(i) for i in skill.get("items", []))
        rows.append('<div class="skill-row"><h3>%s</h3><ul class="tags">%s</ul></div>'
                    % (esc(skill.get("group", "")), items))
    return "".join(rows)


def render_pub_list(pubs, profile, empty_msg="Nothing here yet."):
    if not pubs:
        return '<p class="empty">%s</p>' % esc(empty_msg)
    me = profile.get("highlight_author", "")
    # newest first; ties keep the order they appear in publications.json
    ordered = sorted(pubs, key=lambda p: p.get("year", 0), reverse=True)
    items = "\n".join(render_pub_item(p, me) for p in ordered)
    return '<ul class="pub-list">\n%s\n</ul>' % items


def render_media(media, title):
    """Return a <figure> for a project's media (gif/image or YouTube), or ''.

    `media` may be:
      - a string  -> image src (local file under ROOT, or a remote http(s) URL)
      - a dict    -> {"src": "...", "caption": "..."}  (image)
                  -> {"youtube": "ID", "caption": "..."}  (embedded video)
    Local files that do not exist are skipped with a warning so a missing gif
    never breaks the build.
    """
    if not media:
        return ""
    caption = ""
    yt = None
    src = None
    if isinstance(media, str):
        src = media
    elif isinstance(media, dict):
        src = media.get("src")
        yt = media.get("youtube") or media.get("youtube_id")
        caption = media.get("caption", "")
    if yt:
        inner = ('<div class="video-wrap"><iframe src="https://www.youtube.com/embed/%s" '
                 'title="%s" loading="lazy" allowfullscreen></iframe></div>'
                 % (esc(yt), esc(title)))
        cap = ('<figcaption>%s</figcaption>' % esc(caption)) if caption else ""
        return '<figure class="card-media">%s%s</figure>' % (inner, cap)
    if not src:
        return ""
    is_remote = src.startswith("http://") or src.startswith("https://")
    if not is_remote and not (ROOT / src).exists():
        sys.stderr.write("WARN build: project media not found, skipped: %s\n" % src)
        return ""
    img = '<img loading="lazy" src="%s" alt="%s">' % (esc(src), esc(title))
    cap = ('<figcaption>%s</figcaption>' % esc(caption)) if caption else ""
    return '<figure class="card-media">%s%s</figure>' % (img, cap)


def render_project_card(proj):
    tags = "".join("<li>%s</li>" % esc(t) for t in proj.get("tags", []))
    tags_html = '<ul class="tags">%s</ul>' % tags if tags else ""
    links = link_pills(proj.get("links", []))
    links_html = '<div class="pub-links">%s</div>' % links if links else ""
    media_html = render_media(proj.get("media"), proj.get("title", ""))
    return """<article class="card">
  {media}
  <div class="card-body">
    <h3>{title}</h3>
    <p class="period">{period}</p>
    <p>{summary}</p>
    {tags}
    {links}
  </div>
</article>""".format(
        media=media_html,
        title=esc(proj.get("title", "")),
        period=esc(proj.get("period", "")),
        summary=esc(proj.get("summary", "")),
        tags=tags_html,
        links=links_html,
    )


def render_project_grid(projects, empty_msg="Nothing here yet."):
    if not projects:
        return '<p class="empty">%s</p>' % esc(empty_msg)
    return '<div class="cards">\n%s\n</div>' % "\n".join(render_project_card(p) for p in projects)


def render_video_card(video):
    """Deprecated: videos section removed in favour of Student Life."""
    return ""


def render_video_grid(videos, empty_msg="No videos yet."):
    """Deprecated: videos section removed in favour of Student Life."""
    return ""


def render_gallery(items):
    out = []
    for it in items or []:
        src = it.get("src")
        cap = it.get("caption", "")
        if not src:
            continue
        if not (ROOT / src).exists():
            sys.stderr.write("WARN build: student-life gallery image not found, skipped: %s\n" % src)
            continue
        out.append('<figure><img loading="lazy" src="%s" alt="%s"><figcaption>%s</figcaption></figure>'
                   % (esc(src), esc(cap), esc(cap)))
    if not out:
        return '<p class="empty">Drop your photos into <code>assets/img/studentlife/</code> to fill this gallery.</p>'
    return '<div class="gallery">\n%s\n</div>' % "\n".join(out)


def studentlife_body(profile, sl):
    def section(title, inner):
        return '<section class="section"><h2>%s</h2>%s</section>' % (title, inner)
    head = ('<div class="page-head"><h1>My Student Life</h1>'
            '<p>%s</p></div>' % esc(sl.get("intro", "")))
    parts = [
        head,
        '<main id="main">',
        section("My Journey", render_entry_list(sl.get("milestones", []))),
        '</main>',
    ]
    return '<div class="wrap narrow">\n%s\n</div>' % "\n".join(parts)


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------

def home_body(profile, cv):
    bio = "\n".join("<p class=\"lede\">%s</p>" % p for p in profile.get("bio", []))
    news = "".join(
        '<li><span class="date">%s</span><span>%s</span></li>' % (esc(n.get("date", "")), n.get("text", ""))
        for n in profile.get("news", [])
    )
    interests = "".join("<li>%s</li>" % esc(i) for i in profile.get("interests", []))

    return """
<div class="wrap layout">
  {sidebar}
  <main id="main">
    <section class="section">{bio}</section>

    <section class="section">
      <h2>News</h2>
      <ul class="news">{news}</ul>
    </section>

    <section class="section">
      <h2>Research interests</h2>
      <ul class="tags">{interests}</ul>
    </section>

    <section class="section">
      <h2>Education</h2>
      {education}
    </section>

    <section class="section">
      <h2>Technical skills</h2>
      {skills}
    </section>
  </main>
</div>
""".format(
        sidebar=render_sidebar(profile),
        bio=bio,
        news=news,
        interests=interests,
        education=render_entry_list(cv.get("education", [])),
        skills=render_skills(cv.get("skills", [])),
    )


def plain_body(profile, heading, intro, inner):
    intro_html = '<div class="page-head"><h1>%s</h1><p>%s</p></div>' % (esc(heading), esc(intro))
    return """
<div class="wrap narrow">
  %s
  <main id="main">%s</main>
</div>
""" % (intro_html, inner)


def honours_body(profile, cv):
    def section(title, inner):
        return '<section class="section"><h2>%s</h2>%s</section>' % (title, inner)

    head = ('<div class="page-head"><h1>Honours</h1>'
            '<p>Scholarships, awards and competition results.</p></div>')

    parts = [
        head,
        '<main id="main">',
        section("Honours &amp; awards", render_entry_list(cv.get("honors", []))),
        section("Competitions", render_entry_list(cv.get("competitions", []))),
        '</main>',
    ]
    return '<div class="wrap narrow">\n%s\n</div>' % "\n".join(parts)


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def main():
    profile = load("profile.json")
    pubs = load("publications.json")
    projects = load("projects.json")
    cv = load("cv.json")
    sl = load("studentlife.json")

    name = profile.get("name", "Home")
    outputs = {
        "index.html": build_page(profile, "index.html", name, home_body(profile, cv)),
        "publications.html": build_page(
            profile, "publications.html", "Publications — " + name,
            plain_body(profile, "Publications",
                       "Peer-reviewed articles, reviews and preprints.",
                       render_pub_list(pubs, profile, "No publications yet.")),
        ),
        "projects.html": build_page(
            profile, "projects.html", "Projects — " + name,
            plain_body(profile, "Projects",
                       "Research projects, methods and the code behind them.",
                       render_project_grid(projects, "No projects yet.")),
        ),
        "cv.html": build_page(
            profile, "cv.html", "Honours — " + name,
            honours_body(profile, cv),
        ),
        "studentlife.html": build_page(
            profile, "studentlife.html", "Student Life — " + name,
            studentlife_body(profile, sl),
        ),
    }

    for filename, content in outputs.items():
        (ROOT / filename).write_text(content, encoding="utf-8")
        print("wrote %s  (%d bytes)" % (filename, len(content.encode("utf-8"))))

    print("\nDone. Open index.html to preview, then commit and push.")


if __name__ == "__main__":
    main()
