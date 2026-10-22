#!/usr/bin/env python3
"""Build the site's HTML pages from _data/publications.json.

    python3 scripts/build.py

Edit the JSON (or the page bodies below) and re-run; the generated
index.html, research/, about/ and links/ pages are committed as-is so
GitHub Pages can serve them without a build step.
"""
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ME = 'Sai Saketh Rambhatla'
SCHOLAR = 'https://scholar.google.com/citations?user=VRyNTogAAAAJ&hl=en'
EMAIL = 'saketh@skild.ai'

TOPICS = {
    'generation': 'Image & video generation',
    'video': 'Video understanding',
    'discovery': 'Detection & discovery',
    'reid': 'Re-ID & tracking',
    'learning': 'Learning',
}

NAV = [('/', 'Home'), ('/research/', 'Research'), ('/about/', 'About'), ('/links/', 'Links')]

esc = html.escape


def asset(path):
    """URL for a file under /assets with a content hash, so browsers refetch it after changes."""
    digest = hashlib.sha1((ROOT / path.lstrip('/')).read_bytes()).hexdigest()[:8]
    return f'{path}?v={digest}'


def head(title, desc, path):
    full = 'Saketh Rambhatla' if title is None else f'{title} · Saketh Rambhatla'
    url = f'https://rssaketh.github.io{path}'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(full)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="author" content="Saketh Rambhatla">
  <meta name="theme-color" content="#6aa5d8">
  <link rel="canonical" href="{url}">
  <meta property="og:title" content="{esc(full)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="https://rssaketh.github.io/assets/media/moviegen.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT@0,9..144,300..600,0..100;1,9..144,300..600,0..100&family=Manrope:wght@400;500;600;700&display=swap">
  <link rel="stylesheet" href="{asset('/assets/site.css')}">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-QSFRPR5L7E"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-QSFRPR5L7E');
  </script>
</head>'''


def topbar(path):
    current = ' aria-current="page"'
    items = ''.join(
        f'<li><a href="{href}"{current if href == path else ""}>{label}</a></li>'
        for href, label in NAV)
    return f'''  <header class="topbar">
    <a class="mark glass" href="/" aria-label="Home">SR</a>
    <div class="topbar-right">
      <span class="clock glass" data-clock></span>
      <nav aria-label="Main"><ul class="menu glass">{items}</ul></nav>
    </div>
  </header>'''


# A little pixel Claude that walks back and forth beside the credit.
CLAWD = (
    '<span class="walk" aria-hidden="true"><span class="clawd">'
    '<svg viewBox="0 0 16 12" shape-rendering="crispEdges">'
    '<rect x="2" y="1" width="12" height="7" fill="#d97757"/>'
    '<rect x="0" y="4" width="2" height="2" fill="#d97757"/>'
    '<rect x="14" y="4" width="2" height="2" fill="#d97757"/>'
    '<rect x="5" y="3" width="1" height="2" fill="#1a1a1a"/>'
    '<rect x="10" y="3" width="1" height="2" fill="#1a1a1a"/>'
    '<g class="legs-a"><rect x="3" y="8" width="1" height="3" fill="#d97757"/><rect x="10" y="8" width="1" height="3" fill="#d97757"/></g>'
    '<g class="legs-b"><rect x="5" y="8" width="1" height="3" fill="#d97757"/><rect x="12" y="8" width="1" height="3" fill="#d97757"/></g>'
    '</svg></span></span>'
)

FOOT = f'''    <footer class="foot">
      <span>© 2026 Saketh Rambhatla · The sky follows the time in San Mateo.</span>
      <span class="built">{CLAWD}Built with <a href="https://claude.com/claude-code">Claude</a></span>
    </footer>'''


def page(path, out, title, desc, scene, body, body_class=''):
    cls = f' class="{body_class}"' if body_class else ''
    doc = f'''{head(title, desc, path)}
<body data-scene="{scene}"{cls}>
  <div class="scene"></div>
  <div class="grain"></div>
{topbar(path)}
  <main class="wrap">
{body}
{FOOT}
  </main>
  <script type="module" src="{asset('/assets/scene.js')}"></script>
  <script type="module" src="{asset('/assets/site.js')}"></script>
</body>
</html>
'''
    target = ROOT / out
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc)


# ---------- publication rendering ----------

def authors(names):
    out = []
    for n in names:
        if n.startswith('ME'):
            out.append(f'<b>{esc(ME + n[2:])}</b>')
        else:
            out.append(esc(n))
    return ', '.join(out)


def short_title(t):
    return t.split(':')[0] if ':' in t else t


def media(p, eager=False):
    m = p.get('media')
    if not m:
        return f'<div class="media placeholder">{esc(short_title(p["title"]))}</div>'
    loading = 'eager' if eager else 'lazy'
    if 'video' in m:
        return (f'<div class="media"><video data-autoplay muted loop playsinline preload="none" '
                f'poster="/assets/media/{m["poster"]}" aria-label="{esc(short_title(p["title"]))} sample">'
                f'<source src="/assets/media/{m["video"]}" type="video/mp4"></video>'
                f'<span class="play">Video</span></div>')
    fit = ' contain' if m.get('fit') == 'contain' else ''
    pos = f' style="object-position:{m["pos"]}"' if m.get('pos') else ''
    return (f'<div class="media{fit}"><img src="/assets/media/{m["img"]}" alt="Figure from {esc(short_title(p["title"]))}" '
            f'loading="{loading}" decoding="async"{pos}></div>')


def tags(p):
    t = f'<span>{esc(p["venue"])}</span>'
    if p.get('badge'):
        t += f'<span class="tag hot">{esc(p["badge"])}</span>'
    return t


def links(p):
    return ''.join(f'<a href="{esc(u)}">{esc(n)}</a>' for n, u in p['links'])


def feat_card(p, big=False, eager=False, attrs=''):
    return f'''        <a class="feat card reveal{' big' if big else ''}" href="{esc(p['links'][0][1])}"{attrs}>
          {media(p, eager)}
          <div class="body">
            <div class="meta">{tags(p)}</div>
            <h3>{esc(p['title'])}</h3>
            <p class="note">{esc(p['note'])}</p>
          </div>
        </a>'''


def paper_row(p):
    return f'''          <article class="paper card reveal" data-topics="{' '.join(p['topics'])}">
            {media(p)}
            <div>
              <div class="meta">{tags(p)}</div>
              <h3><a href="{esc(p['links'][0][1])}">{esc(p['title'])}</a></h3>
              <p class="authors">{authors(p['authors'])}</p>
              <p class="note">{esc(p['note'])}</p>
              <div class="links">{links(p)}</div>
            </div>
          </article>'''


def build():
    pubs = json.loads((ROOT / '_data/publications.json').read_text())
    by_title = {p['title'].split(':')[0]: p for p in pubs}

    # ----- research -----
    order = ['Movie Gen', 'Emu Video', 'Toward Diffusible High-Dimensional Latent Spaces',
             'Diffusion Autoencoders are Scalable Image Tokenizers', 'MotiF', 'InstanceDiffusion', 'MOST']
    featured = [by_title[k] for k in order if k in by_title]
    big = {'Movie Gen', 'Emu Video', 'InstanceDiffusion', 'MOST'}

    # Each topic filter gets its own three highlights: hand-picked where listed,
    # otherwise featured papers first, then the newest papers in that topic.
    picks = {
        'generation': ['Movie Gen', 'Emu Video', 'InstanceDiffusion'],
        'discovery': ['MOST', 'The Pursuit of Knowledge', 'SparseDet'],
        'reid': ['Towards Accurate Visual and Natural Language-based Vehicle Retrieval Systems',
                 'A Dual-Path Model With Adaptive Attention for Vehicle Re-Identification',
                 'Body Part Alignment and Temporal Attention Pooling for Video-Based Person Re-Identification'],
        'learning': ['An Empirical Analysis of Boosting Deep Networks'],
    }
    highlights = {}
    for t in TOPICS:
        if t in picks:
            highlights[t] = [by_title[k] for k in picks[t]]
            continue
        ranked = [p for p in featured if t in p['topics']] + [p for p in pubs if t in p['topics'] and p not in featured]
        highlights[t] = ranked[:3]
    cards = featured + [p for t in TOPICS for p in highlights[t] if p not in featured]
    cards = list(dict.fromkeys(id(p) for p in cards))
    cards = [next(p for p in pubs if id(p) == i) for i in cards]

    def hl_attrs(p):
        hl = ' '.join(t for t in TOPICS if p in highlights[t])
        default = ' data-default' if p in featured else ' hidden'
        return f' data-hl="{hl}"{default}'

    feat_html = '\n'.join(
        feat_card(p, short_title(p['title']) in big, i < 2, hl_attrs(p)) for i, p in enumerate(cards))

    counts = {k: sum(k in p['topics'] for p in pubs) for k in TOPICS}
    chips = [f'<button class="glass" data-topic="all" aria-pressed="true">All<span class="count">{len(pubs)}</span></button>']
    chips += [f'<button class="glass" data-topic="{k}" aria-pressed="false">{esc(v)}<span class="count">{counts[k]}</span></button>'
              for k, v in TOPICS.items() if counts[k]]

    years = []
    for y in sorted({p['year'] for p in pubs}, reverse=True):
        rows = '\n'.join(paper_row(p) for p in pubs if p['year'] == y)
        years.append(f'''      <section class="year-group">
        <div class="year-label">{y}</div>
        <div class="papers">
{rows}
        </div>
      </section>''')

    research = f'''    <section class="page-head">
      <p class="kicker"><span class="dot"></span>{len(pubs)} papers · 2019 – 2026</p>
      <h1>Research</h1>
      <p class="lede">Generative models for images and video, and before that object discovery, detection, tracking and re-identification. * equal contribution, † project lead. The full list lives on <a href="{SCHOLAR}">Google Scholar</a>.</p>
      <div class="filters" role="group" aria-label="Filter by topic">
        {''.join(chips)}
      </div>
    </section>

    <section class="section">
      <div class="section-head"><h2>Highlights</h2></div>
      <div class="featured">
{feat_html}
      </div>
    </section>

    <section class="section">
      <div class="section-head"><h2>All papers</h2></div>
{chr(10).join(years)}
    </section>'''
    page('/research/', 'research/index.html', 'Research',
         'Publications by Saketh Rambhatla: Movie Gen, Emu Video, InstanceDiffusion, diffusion tokenizers, MOST, SparseDet and more.',
         'badlands', research)

    # ----- home -----
    home_feat = '\n'.join([
        feat_card(by_title['Movie Gen'], True, True),
        feat_card(by_title['Emu Video'], True, True),
        feat_card(by_title['Toward Diffusible High-Dimensional Latent Spaces']),
        feat_card(by_title['Diffusion Autoencoders are Scalable Image Tokenizers']),
        feat_card(by_title['InstanceDiffusion']),
    ])
    home = f'''    <section class="hero">
      <p class="kicker"><span class="dot"></span>Member of Technical Staff · Skild AI</p>
      <h1>Saketh<br><em>Rambhatla</em></h1>
      <p class="lede">These days I’m teaching robots to do useful things at Skild AI. Before that I spent three years at Meta getting AI to dream up images and video, like Movie Gen and Emu Video.</p>
      <div class="btns">
        <a class="btn primary" href="/research/">See research →</a>
        <a class="btn glass" href="/about/">About me</a>
        <a class="btn glass" href="/data/rssaketh.pdf">CV</a>
      </div>
    </section>

    <section class="section">
      <div class="section-head reveal"><h2>Selected work</h2><a class="btn glass" href="/research/">All {len(pubs)} papers →</a></div>
      <div class="featured">
{home_feat}
      </div>
    </section>'''
    page('/', 'index.html', None,
         'Saketh Rambhatla — Member of Technical Staff at Skild AI working on VLA and world action models for robots. Previously Senior Research Scientist at Meta (Movie Gen, Emu Video); Ph.D. University of Maryland.',
         'mesas', home, 'home')

    # ----- about -----
    about = f'''    <section class="page-head">
      <p class="kicker"><span class="dot"></span>San Mateo, California</p>
      <h1>About</h1>
    </section>

    <div class="about-grid">
      <section class="card pad reveal">
        <p class="sub">Hello</p>
        <p>I’m a Member of Technical Staff at <b>Skild AI</b>, where I research and develop Vision-Language-Action (VLA) and World Action Models (WAM) for multi-embodiment robot control, toward generalist robot policies.</p>
        <p>Before Skild, I was a Senior Research Scientist at Meta AI Research in Seattle, working on native image and video generation with large language models. Before that I was a postdoctoral researcher at Meta in New York with <a href="https://imisra.github.io">Ishan Misra</a>, working on generation — <a href="https://ai.meta.com/research/movie-gen/">Movie Gen</a>, <a href="https://emu-video.metademolab.com">Emu Video</a>, <a href="https://people.eecs.berkeley.edu/~xdwang/projects/InstDiff/">InstanceDiffusion</a> — and evaluation (<a href="https://arxiv.org/abs/2311.10708">SelfEval</a>).</p>
        <p>I did my Ph.D. in Electrical Engineering at the <a href="https://umd.edu">University of Maryland, College Park</a> with <a href="https://engineering.jhu.edu/ece/faculty/rama-chellappa/">Rama Chellappa</a> and <a href="https://abhinavsh.info">Abhinav Shrivastava</a>, on in-the-wild visual understanding: object discovery and localization, sparsely annotated detection, few-shot learning, tracking and re-identification. Before that, a dual degree in Electrical Engineering at <a href="https://www.iitkgp.ac.in">IIT Kharagpur</a>.</p>

        <p class="sub">Service</p>
        <ul class="plain">
          <li><b>Conferences</b> — CVPR ’19–’26, ECCV ’20–’26, ICCV ’19–’25, ICLR ’23–’25, NeurIPS ’23–’25, ICML ’24</li>
          <li><b>Journals</b> — IJCV, T-PAMI, Pattern Recognition Letters, IEEE Access</li>
        </ul>

        <p class="sub">Teaching</p>
        <ul class="plain">
          <li><b>Graduate TA, UMD</b> — ENEE222 (Fall 2016), ENEE324 (Spring 2017), ENEE425 (Fall 2017), ENEE630 (Fall 2017)</li>
        </ul>
      </section>

      <div class="stack">
        <section class="card pad reveal">
          <p class="sub">Experience</p>
          <ol class="timeline">
            <li><div class="when">Dec 2025 – now</div><div class="what">Member of Technical Staff</div><div class="where">Skild AI Research, San Mateo</div></li>
            <li><div class="when">Oct 2024 – Dec 2025</div><div class="what">Senior Research Scientist</div><div class="where">Meta AI Research, Seattle</div></li>
            <li><div class="when">Jan 2023 – Oct 2024</div><div class="what">Postdoctoral Researcher</div><div class="where">Meta AI Research, New York · with Ishan Misra</div></li>
            <li><div class="when">2022</div><div class="what">Research Intern</div><div class="where">Cruise AI, San Francisco</div></li>
            <li><div class="when">2018, 2019</div><div class="what">Research Intern</div><div class="where">Mitsubishi Electric Research Laboratories, Boston</div></li>
          </ol>
        </section>
        <section class="card pad reveal">
          <p class="sub">Education</p>
          <ol class="timeline">
            <li><div class="when">2016 – 2022</div><div class="what">Ph.D., Electrical Engineering</div><div class="where">University of Maryland, College Park · Thesis: Towards In-the-Wild Visual Understanding</div></li>
            <li><div class="when">2016 – 2021</div><div class="what">M.S., Electrical Engineering</div><div class="where">University of Maryland, College Park</div></li>
            <li><div class="when">2011 – 2016</div><div class="what">Dual Degree (B.Tech + M.Tech), Electrical Engineering</div><div class="where">IIT Kharagpur</div></li>
          </ol>
        </section>
      </div>
    </div>'''
    page('/about/', 'about/index.html', 'About',
         'About Saketh Rambhatla: Member of Technical Staff at Skild AI; previously Senior Research Scientist and postdoc at Meta; Ph.D. University of Maryland; IIT Kharagpur.',
         'dunes', about)

    # ----- links -----
    icon = {
        'mail': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
        'scholar': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 9 12 4l10 5-10 5z"/><path d="M6 11v5c3 2.5 9 2.5 12 0v-5"/></svg>',
        'github': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.89 1.53 2.34 1.09 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.02A9.6 9.6 0 0 1 12 6.84c.85 0 1.7.11 2.5.34 1.9-1.29 2.74-1.02 2.74-1.02.55 1.38.2 2.4.1 2.65.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.68-4.57 4.93.36.31.68.92.68 1.85v2.74c0 .27.18.58.69.48A10 10 0 0 0 12 2z"/></svg>',
        'linkedin': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zM9.5 9.5h3.8v1.6h.05c.53-1 1.83-2.05 3.77-2.05 4.03 0 4.78 2.65 4.78 6.1V21h-4v-5.1c0-1.22-.02-2.79-1.7-2.79-1.7 0-1.96 1.33-1.96 2.7V21h-4z"/></svg>',
        'cv': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/></svg>',
    }
    tiles = [
        ('mail', 'Email', 'Opens your mail app', f'mailto:{EMAIL}'),
        ('scholar', 'Scholar', 'Papers & citations', SCHOLAR),
        ('github', 'GitHub', '@rssaketh', 'https://github.com/rssaketh'),
        ('linkedin', 'LinkedIn', 'in/rssaketh', 'https://www.linkedin.com/in/rssaketh/'),
        ('cv', 'CV', 'PDF', '/data/rssaketh.pdf'),
    ]
    tile_html = '\n'.join(
        f'''        <a class="tile card reveal" href="{esc(u)}">{icon[i]}<span class="label">{esc(l)}</span><span class="hint">{esc(h)}</span></a>'''
        for i, l, h, u in tiles)
    links_page = f'''    <section class="page-head">
      <p class="kicker"><span class="dot"></span>Say hello</p>
      <h1>Links</h1>
      <p class="lede">Email is the best way to reach me.</p>
    </section>
    <div class="tiles">
{tile_html}
    </div>'''
    page('/links/', 'links/index.html', 'Links',
         'Contact Saketh Rambhatla: email, Google Scholar, GitHub, LinkedIn and CV.',
         'arch', links_page)


if __name__ == '__main__':
    build()
