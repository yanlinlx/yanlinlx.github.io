# Academic Homepage

A dependency-free static academic homepage. Content lives in `data/*.json`;
`build.py` turns it into plain HTML, which you host for free on GitHub Pages
(global CDN, HTTPS, custom domain) so anyone overseas can open it instantly.

```
academic-site/
├── build.py              ← run this after every content edit
├── index.html            ┐
├── publications.html     │
├── projects.html         │ generated — do not edit by hand
├── cv.html               │
├── videos.html           ┘
├── data/                 ← EDIT THESE
│   ├── profile.json      name, bio, links, news, interests
│   ├── publications.json one object per paper
│   ├── projects.json     one object per project
│   ├── cv.json           education, honours, competitions, skills
│   └── videos.json       YouTube ids + captions
├── assets/
│   ├── style.css         colours / layout
│   ├── site.js           theme toggle + lazy YouTube
│   ├── avatar.svg        ← replace with your photo
│   └── favicon.svg
├── files/                ← optional downloads (e.g. a PDF CV)
├── CNAME.example
└── .nojekyll
```

Five pages: **About** (bio, news, interests, selected work), **Publications**,
**Projects**, **CV**, **Videos**.

---

## 1. Preview locally

Just double-click `index.html`. Everything works offline (the only external
request is a YouTube thumbnail, which is optional).

## 2. Edit your content

Open the files in `data/` with any text editor. They are plain JSON.

- **profile.json** — your name, role, affiliation, bio paragraphs, research
  interests, the links in the sidebar, and the "News" list. `highlight_author`
  is the string that gets bolded in every author list.
- **publications.json** — one `{ ... }` block per paper. `"featured": true`
  also pins it to the homepage. `links` accepts any `{label, url}` pairs.
- **projects.json** — same idea; add `"featured": true` to pin to the homepage.
  Each project can show an animated gif / image / embedded video at the top of
  its card via a `"media"` field:
  - local gif:  `"media": "assets/gifs/my-project.gif"`  (put the file in
    `assets/gifs/`; if the file is missing the card just renders without it, no
    broken image)
  - remote image: `"media": "https://.../clip.gif"`
  - with caption: `"media": {"src": "assets/gifs/x.gif", "caption": "MD trajectory of ..."}`
  - embedded YouTube: `"media": {"youtube": "VIDEO_ID", "caption": "..."}`
  Keep each gif small — ideally ≤ 10 MB (GitHub Pages warns above 50 MB and
  rejects a single file above 100 MB). Optimise with e.g.
  `ffmpeg -i in.mp4 -vf "scale=480:-1,fps=15" -loop 0 out.gif`.
- **cv.json** — the CV page. Sections `education`, `honors`, `competitions`
  (each entry is `{left, title, meta, details[]}`, where `left` is the date
  column — drop it if the whole section has no dates) and `skills`
  (`{group, items[]}`). Titles and details accept simple HTML; write `&amp;`
  for an ampersand.
- **videos.json** — paste the YouTube id (the part after `v=` in the watch URL)
  into `"youtube_id"`. Empty id → placeholder tile.

To get a PDF CV, open the generated `cv.html` in a browser and print to PDF —
the print stylesheet strips the navigation and tightens the layout.

Then rebuild:

```bash
python build.py
```

> Watch out for commas: JSON does not allow a trailing comma after the last
> item, and every string needs double quotes. If `build.py` complains, that is
> almost always the reason.

Replace `assets/avatar.svg` with your own photo (e.g. `avatar.jpg`, then point
`"avatar"` in `profile.json` at it) and drop `cv.pdf` into `files/`.

## 3. Put it online (GitHub Pages)

```bash
cd academic-site
git init
git add .
git commit -m "Initial site"
```

Create an empty **public** repository on GitHub named exactly
`<your-username>.github.io`, then:

```bash
git remote add origin https://github.com/<your-username>/<your-username>.github.io.git
git branch -M main
git push -u origin main
```

Within a minute or two your site is live at
`https://<your-username>.github.io`.

Anything pushed to `main` is published automatically — so the update loop is:

```bash
python build.py && git add -A && git commit -m "Update" && git push
```

### If `git push` fails from this machine

This machine's proxy blocks `github.com` (only `api.github.com` is reachable)
and a global git config rewrites `github.com` to an npm mirror, so `git push`
fails here regardless. Two ways out:

- **`deploy_github.py`** (one level above `academic-site/`) — talks to the
  GitHub API directly, no git transport needed:
  `GITHUB_TOKEN=ghp_xxx python deploy_github.py`
  It creates the repo, uploads every file, enables Pages and HTTPS in one go.
- **From another network** (phone hotspot / VPN / another computer) — the
  normal `git push` above works. The API deploy writes an unrelated history,
  so re-sync once with `git push --force origin main`.

## 4. Your own domain

`<your-username>.github.io` is already reachable from anywhere in the world —
GitHub Pages sits on a global CDN. A custom domain does not unlock new
countries; it makes the URL memorable and looks better on a CV or in an email
to a potential supervisor. Budget **US$10–20 / ¥70–120 per year**, forever.

### 4.1 What to buy

`.com` first choice, `.me` / `.dev` good fallbacks. Notes:

- **Avoid `.cn`** — it needs an ICP filing number to keep resolving, and
  personal filing is restricted. You are not hosting in mainland China, so you
  never need to file anything.
- **`.io` is a bad long-term bet.** It works fine today, but the UK handed the
  Chagos Archipelago to Mauritius in 2025 and the ccTLD's future is unsettled.
  Any change would take years — but a homepage you keep through a PhD outlives
  that uncertainty.
- **Google Domains no longer sells to new customers** (moved to Squarespace).
- Hyphens are painful to dictate — `yanlinli.me` beats `yanlin-li.me`.

Name patterns to try, in order: `<first><last>`, `<last><first>`,
`<first>-<last>`, then the same on `.me` / `.dev`.

### 4.2 Where to buy

| If you have… | Buy at | Why |
|---|---|---|
| Alipay / WeChat only | **腾讯云 DNSPod** or **阿里云** | ¥70–90/yr, needs 实名认证 (ID card, 15 min–2 h), DNS console included and fine |
| An international card or PayPal | **Cloudflare Registrar** | sells at wholesale cost — no mark-up, no renewal hike, no upsells |

Whatever you pick, **read the renewal price before paying** — several registrars
advertise ¥1 first years and charge ¥90+ on renewal.

### 4.3 Wire it up (order matters)

Claim the domain on GitHub **first**, then add DNS. Doing it the other way
round leaves a window in which someone else can claim your domain on their own
Pages site.

1. Repo **Settings → Pages → Custom domain** → type `yourname.com` → **Save**.
   This writes a `CNAME` file into the repo — keep it (`CNAME.example` shows
   the format).
2. At your DNS provider add:

   | Type  | Name  | Value |
   |-------|-------|-------|
   | A     | `@`   | `185.199.108.153` |
   | A     | `@`   | `185.199.109.153` |
   | A     | `@`   | `185.199.110.153` |
   | A     | `@`   | `185.199.111.153` |
   | CNAME | `www` | `<your-username>.github.io` |

   Optional IPv6: four AAAA records `2606:50c0:8000::153` …
   `2606:50c0:8003::153`.

3. Wait for propagation (usually minutes, up to 24 h), then back on
   **Settings → Pages** tick **Enforce HTTPS**. GitHub issues and renews the
   certificate itself — **never buy an SSL certificate for this site**.
4. Keep the record **DNS-only / grey cloud**. GitHub's automatic certificate
   breaks behind Cloudflare's proxy (orange cloud).

### 4.4 After that

- **Turn on auto-renew** and keep the registrant email current. An expired
  domain goes: ~30 d grace → ~30 d redemption (¥500+) → public auction.
- **Email**: get `you@yourname.com` forwarding to Gmail/QQ for free (Cloudflare
  Email Routing, or the registrar's own forwarding).
- **Don't buy** hosting, SSL, "website builder" or VPN bundles from the
  registrar — none of it applies to a static Pages site.
- **Transferring out** is locked for 60 days after registration or a transfer;
  after that you can move anywhere. Another reason Cloudflare Registrar is
  attractive for the long run.

## 5. Videos

Do **not** commit large videos: GitHub rejects files over 100 MB and a bloated
repo slows every clone.

- **YouTube (chosen)** — upload, set visibility to *Unlisted* or *Public*,
  copy the id into `videos.json`. The page shows a thumbnail and only loads the
  player after a click, which keeps the page fast.
- **If you later want direct playback** without YouTube, put the `.mp4` on
  Cloudflare R2 or Backblaze B2 behind your domain and link to it — same
  editing flow, just a `url` instead of a `youtube_id`.

Small clips (a few MB) are fine to drop into the repo and embed with a plain
`<video>` tag.

## 6. Optional: automate the build

Instead of running `python build.py` yourself, add
`.github/workflows/pages.yml` with a Python step that runs `build.py` and
publishes the result. Ask me and I will set it up.

---

Colours and typography live in `assets/style.css` as CSS variables at the top —
change `--accent` to restyle the whole site in one line.
