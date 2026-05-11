#!/usr/bin/env python3
"""
generate_blog.py
Runs every Monday via GitHub Actions.
- Calls Claude API to write a nail care blog post
- Saves it as blogs/YYYY-MM-DD.html (matching nakeyNails design exactly)
- Updates blogs/index.html with the new post entry
"""

import os, json, datetime, urllib.request, urllib.error, re

# ── Config ──────────────────────────────────────────────────────
API_KEY   = os.environ["ANTHROPIC_API_KEY"]
TODAY     = datetime.date.today()
SLUG      = TODAY.strftime("%Y-%m-%d")
DATE_STR  = TODAY.strftime("%B %d, %Y")
DATE_SHORT = TODAY.strftime("%b %d, %Y")

# Rotating topic list — cycles weekly, never repeats for 16 weeks
TOPICS = [
    "How to recover from gel nail damage",
    "Why nails peel after acrylics — and how to stop it",
    "5 daily habits that keep nails strong and healthy",
    "The truth about nail hardeners",
    "How to grow nails naturally after gel",
    "Why hydration is the most underrated part of nail care",
    "How peptides help repair damaged nails",
    "What to do between nail appointments",
    "How long does nail recovery really take",
    "Morning vs night: when is the best time to apply nail serum",
    "The difference between nail strengtheners and nail repair",
    "Why your nails keep breaking — and what actually helps",
    "How frequent handwashing affects nail health",
    "What ingredients to look for in a nail treatment",
    "Gel vs acrylic: which causes more damage to your nails",
    "How to build a simple nail care routine that you'll actually stick to",
]

week_number = TODAY.isocalendar()[1]
topic = TOPICS[week_number % len(TOPICS)]

print(f"Generating blog post for: {topic}")

# ── Call Claude API ──────────────────────────────────────────────
prompt = f"""Write a blog post for nakeyNails, a premium nail care brand.

Topic: {topic}

Requirements:
- 380 to 450 words
- Warm, knowledgeable, human tone — like a trusted expert, not a salesperson
- Educational and genuinely helpful
- Last paragraph should mention NakeyPen naturally (do not make it feel like an ad)
- Do NOT use bullet points or lists — write in flowing paragraphs only
- Return ONLY a raw JSON object with exactly these three fields:
    title       (string, compelling headline, max 8 words)
    subtitle    (string, one sentence that summarises the post, max 20 words)
    body        (string, full post in HTML using <p> tags only, no other tags)
- No markdown. No code fences. No explanation. Just the JSON object."""

payload = json.dumps({
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 1200,
    "messages": [{"role": "user", "content": prompt}]
}).encode()

req = urllib.request.Request(
    "https://api.anthropic.com/v1/messages",
    data=payload,
    headers={
        "x-api-key":          API_KEY,
        "anthropic-version":  "2023-06-01",
        "content-type":       "application/json"
    }
)

try:
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())
except urllib.error.HTTPError as e:
    print(f"API error {e.code}: {e.read().decode()}")
    raise

raw_text = data["content"][0]["text"].strip()

# Strip any accidental markdown fences
raw_text = re.sub(r"^```[a-z]*\n?", "", raw_text)
raw_text = re.sub(r"\n?```$", "", raw_text)

post = json.loads(raw_text)
title    = post["title"]
subtitle = post["subtitle"]
body     = post["body"]

print(f"Title: {title}")

# ── Generate blog post HTML ──────────────────────────────────────
post_html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<title>{title} · nakeyNails</title>
<meta name="description" content="{subtitle}"/>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=DM+Sans:wght@300;400&display=swap" rel="stylesheet">
<style>

:root {{
  --paper:      #F9F6F1;
  --ink:        #1A1610;
  --mid:        #5C5650;
  --quiet:      #9E9890;
  --serif:      'Cormorant Garamond', Georgia, serif;
  --sans:       'DM Sans', system-ui, sans-serif;
  --text-label: 10px;
  --text-sm:    clamp(13px, 0.4vw + 11px, 15px);
  --text-base:  clamp(15px, 0.4vw + 13px, 17px);
  --text-lg:    clamp(18px, 0.6vw + 15px, 22px);
  --gutter:     clamp(24px, 5vw, 80px);
  --ease:       cubic-bezier(0.22, 1, 0.36, 1);
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  background: var(--paper);
  color: var(--ink);
  font-family: var(--sans);
  font-weight: 300;
  font-size: var(--text-base);
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
}}
a   {{ color: inherit; text-decoration: none; }}
button {{ font: inherit; color: inherit; background: none; border: 0; cursor: pointer; }}

/* ── Nav ─────────────────────────────────────────────────────── */
.nav {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px var(--gutter);
  position: sticky; top: 0; z-index: 50;
  background: rgba(249,246,241,0.92);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(26,22,16,0.07);
}}
.nav-brand {{ display: inline-flex; align-items: center; flex-shrink: 0; }}
.nav-brand img {{ height: 28px; width: auto; display: block; }}
.nav-links {{
  display: flex; gap: 36px;
  font-size: 11px; font-weight: 400; letter-spacing: 0.2em; text-transform: uppercase; color: var(--mid);
}}
.nav-links a {{ transition: color .2s; }}
.nav-links a:hover {{ color: var(--ink); }}
.nav-links a.active {{ color: var(--ink); }}
.nav-cta {{
  display: inline-flex; align-items: center; padding: 10px 20px;
  background: var(--ink); color: var(--paper);
  font-family: var(--sans); font-size: 10px; font-weight: 400; letter-spacing: 0.24em; text-transform: uppercase;
  transition: opacity .2s; white-space: nowrap;
}}
.nav-cta:hover {{ opacity: 0.72; }}
.nav-menu {{ display: none; }}
@media (max-width: 720px) {{
  .nav-links {{ display: none; }}
  .nav-menu  {{ display: block; font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; }}
}}

/* ── Mobile menu ─────────────────────────────────────────────── */
.menu-overlay {{
  display: none; position: fixed; inset: 0;
  background: var(--paper); z-index: 70;
  padding: 28px var(--gutter); flex-direction: column;
}}
.menu-overlay.open {{ display: flex; }}
.menu-overlay-top {{ display: flex; justify-content: space-between; align-items: center; }}
.menu-overlay nav {{ margin-top: 72px; display: flex; flex-direction: column; gap: 8px; }}
.menu-overlay nav a {{
  font-family: var(--serif); font-size: clamp(36px, 6vw, 56px); font-weight: 300;
  color: var(--ink); letter-spacing: -0.01em; padding: 12px 0; transition: color .2s;
}}
.menu-overlay nav a:hover {{ color: var(--quiet); }}

/* ── Article ─────────────────────────────────────────────────── */
.article {{
  max-width: 680px;
  margin: 0 auto;
  padding: clamp(56px, 8vw, 104px) var(--gutter) clamp(80px, 10vw, 140px);
}}

.back {{
  font-size: var(--text-label);
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--quiet);
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 48px;
  transition: color .2s;
}}
.back:hover {{ color: var(--ink); }}

.article-label {{
  font-size: var(--text-label);
  letter-spacing: 0.32em;
  text-transform: uppercase;
  color: var(--quiet);
  display: block;
  margin-bottom: 24px;
}}

h1 {{
  font-family: var(--serif);
  font-size: clamp(36px, 5vw + 16px, 72px);
  font-weight: 300;
  line-height: 0.95;
  letter-spacing: -0.022em;
  margin-bottom: 24px;
}}

.subtitle {{
  font-size: var(--text-lg);
  color: var(--mid);
  line-height: 1.65;
  margin-bottom: 48px;
  padding-bottom: 48px;
  border-bottom: 1px solid rgba(26,22,16,0.08);
}}

.body p {{
  color: var(--mid);
  line-height: 1.85;
  margin-bottom: 24px;
  font-size: var(--text-base);
}}
.body p:last-child {{ margin-bottom: 0; }}

/* ── Footer ──────────────────────────────────────────────────── */
footer {{
  padding: 40px var(--gutter);
  display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;
  border-top: 1px solid rgba(26,22,16,0.07);
}}
.footer-brand {{
  font-family: var(--serif); font-size: 16px; font-weight: 400;
  letter-spacing: 0.28em; text-transform: uppercase;
}}
.footer-meta {{ font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--quiet); }}

</style>
</head>
<body>

<!-- Nav -->
<header class="nav">
  <a class="nav-brand" href="../index.html" aria-label="nakeyNails — home">
    <img src="../logo.png" alt="nakeyNails"/>
  </a>
  <nav class="nav-links" aria-label="Main navigation">
    <a href="../index.html#product">The Pen</a>
    <a href="../index.html#ingredients">Formula</a>
    <a href="../index.html#faq">FAQ</a>
    <a href="../remind-me.html">Remind Me</a>
    <a href="index.html" class="active">Blog</a>
  </nav>
  <button class="nav-menu" id="menuBtn" aria-label="Open menu" aria-expanded="false">Menu</button>
  <a href="https://www.amazon.com/dp/B0G14TM258" target="_blank" rel="noopener" class="nav-cta">Shop Now</a>
</header>

<!-- Mobile menu -->
<div class="menu-overlay" id="menuOverlay" role="dialog" aria-modal="true" aria-label="Navigation">
  <div class="menu-overlay-top">
    <span style="font-family:var(--serif);font-size:20px;letter-spacing:0.3em;text-transform:uppercase;">nakeyNails</span>
    <button id="menuClose" aria-label="Close" style="font-size:24px;color:var(--quiet);">×</button>
  </div>
  <nav>
    <a href="../index.html#product">The Pen</a>
    <a href="../index.html#ingredients">Formula</a>
    <a href="../index.html#faq">FAQ</a>
    <a href="../remind-me.html">Remind Me</a>
    <a href="index.html">Blog</a>
    <a href="https://www.amazon.com/dp/B0G14TM258" target="_blank" rel="noopener">Shop</a>
  </nav>
</div>

<!-- Article -->
<main class="article">
  <a class="back" href="index.html">← All posts</a>
  <span class="article-label">nakeyNails · {DATE_STR}</span>
  <h1>{title}</h1>
  <p class="subtitle">{subtitle}</p>
  <div class="body">
    {body}
  </div>
</main>

<!-- Footer -->
<footer>
  <span class="footer-brand">nakeyNails</span>
  <span class="footer-meta">© {TODAY.year} · Made in USA · Dermatologist Tested</span>
  <span class="footer-meta">Privacy · Terms</span>
</footer>

<script>
  const btn     = document.getElementById('menuBtn');
  const close   = document.getElementById('menuClose');
  const overlay = document.getElementById('menuOverlay');
  btn?.addEventListener('click', () => {{ overlay.classList.add('open'); btn.setAttribute('aria-expanded','true'); document.body.style.overflow='hidden'; }});
  function closeMenu() {{ overlay.classList.remove('open'); btn.setAttribute('aria-expanded','false'); document.body.style.overflow=''; }}
  close?.addEventListener('click', closeMenu);
  overlay?.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
  document.addEventListener('keydown', e => e.key === 'Escape' && closeMenu());
</script>

</body>
</html>"""

# ── Write post file ──────────────────────────────────────────────
os.makedirs("blogs", exist_ok=True)
post_path = f"blogs/{SLUG}.html"
with open(post_path, "w", encoding="utf-8") as f:
    f.write(post_html)
print(f"Written: {post_path}")

# ── Update blogs/index.html ──────────────────────────────────────
# Read all existing blog files to rebuild the post list
blog_dir = "blogs"
post_files = sorted(
    [f for f in os.listdir(blog_dir) if re.match(r"\d{4}-\d{2}-\d{2}\.html$", f)],
    reverse=True  # newest first
)

entries_html = ""
for filename in post_files:
    slug = filename.replace(".html", "")
    filepath = os.path.join(blog_dir, filename)

    # Parse title and subtitle from the file
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    t_match  = re.search(r"<title>(.*?) · nakeyNails</title>", content)
    h1_match = re.search(r"<h1>(.*?)</h1>", content, re.DOTALL)
    s_match  = re.search(r'<p class="subtitle">(.*?)</p>', content, re.DOTALL)

    post_title    = h1_match.group(1).strip() if h1_match else slug
    post_subtitle = s_match.group(1).strip() if s_match else ""

    # Format date from slug
    try:
        d = datetime.datetime.strptime(slug, "%Y-%m-%d")
        display_date = d.strftime("%b %d, %Y")
    except Exception:
        display_date = slug

    entries_html += f"""
    <a class="post-item reveal" href="{filename}">
      <span class="post-date">{display_date}</span>
      <div class="post-body">
        <h2>{post_title}</h2>
        <p>{post_subtitle}</p>
        <span class="post-read">Read →</span>
      </div>
    </a>"""

# Inject entries into index template
index_path = "blogs/index.html"
with open(index_path, "r", encoding="utf-8") as f:
    index_content = f.read()

index_content = re.sub(
    r"<!-- POST_ENTRIES -->.*?(?=\s*</div>)",
    f"<!-- POST_ENTRIES -->{entries_html}",
    index_content,
    flags=re.DOTALL
)

with open(index_path, "w", encoding="utf-8") as f:
    f.write(index_content)

print(f"Updated: {index_path} ({len(post_files)} posts)")
print("Done.")
