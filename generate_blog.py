#!/usr/bin/env python3
"""
generate_blog.py - nakeyNails weekly blog
- Single API call (low token usage, no rate limits)
- Claude picks a fresh niche-relevant topic dynamically
- Never repeats topics (tracked in blogs/topics_used.json)
- 600-750 word human-sounding post with full SEO
- No em dashes in output
"""

import os, json, re, datetime, urllib.request, urllib.error

API_KEY  = os.environ["ANTHROPIC_API_KEY"]
DOMAIN   = "https://nakeynails.com"
TODAY    = datetime.date.today()
SLUG     = TODAY.strftime("%Y-%m-%d")
DATE_STR = TODAY.strftime("%B %d, %Y")
YEAR     = TODAY.year

os.makedirs("blogs", exist_ok=True)
TOPICS_FILE = "blogs/topics_used.json"

# Load used topics
if os.path.exists(TOPICS_FILE):
    with open(TOPICS_FILE) as f:
        topics_used = json.load(f)
else:
    topics_used = []

used_list = "\n".join(f"- {t}" for t in topics_used) or "None yet."
print(f"Topics used so far: {len(topics_used)}")

# ── Single API call: pick topic + write post ─────────────────────
prompt = f"""You are writing for nakeyNails (nakeynails.com). NakeyPen is a nail repair serum for people whose nails have been damaged by gel and acrylic manicures.

TASK: Choose a fresh topic and write a complete blog post in one step.

TOPIC RULES:
- Pick ONE specific topic. Rotate across these niche areas so the blog covers them all over time:
  1. Nail brittleness: causes, prevention, daily habits that help
  2. Nail thinning: why it happens, how to rebuild thickness
  3. Nail peeling: what causes layers to separate, what stops it
  4. Nail yellowing: staining, discolouration, reversing it
  5. Chronic nail damage: long-term gel or acrylic users, cumulative effects
  6. Gel damage: removal damage, UV exposure, keratin loss
  7. Acrylic damage: filing damage, adhesive chemicals, recovery timeline
  8. Nail growth: what speeds it up, what blocks it
  9. Nail hydration: cuticle care, moisture barrier, dry brittle nails
  10. Nail ingredients: what peptides, keratin, hyaluronic acid, niacinamide actually do
- The topic must NOT be in this already-used list:
{used_list}
- Pick whichever niche area above has been covered LEAST based on the used list above
- Be highly specific with your angle:
  Bad: "nail brittleness tips" | Good: "Why nails get extra brittle in winter and what actually helps"
  Bad: "gel nail damage" | Good: "The specific damage that happens when you peel off gel polish"
  Bad: "nail peeling" | Good: "Why the top layer of your nail keeps separating even after stopping gel"
- Vary your title format every single week. Rotate through these structures:
  "Why...", "How to...", "The real reason...", "What happens when...", "Is it normal that...", "How long does it take to...", "What nobody tells you about..."
  Never start two posts in a row with the same opening word

WRITING RULES:
- 600 to 750 words
- Write like a real person who knows nails, not a content generator
- Use short paragraphs (2 to 3 sentences each)
- Mix short and long sentences naturally
- Address the reader directly using "you"
- Include one specific relatable scenario (example: "You finally get your gel removed and...")
- Do NOT use the words: delve, comprehensive, crucial, leverage, furthermore, moreover, in conclusion, it is important to note, game changer
- Do NOT use em dashes (the -- or long dash character). Use commas or full stops instead
- Do NOT open with a question
- Do NOT use bullet points or numbered lists
- 3 to 4 subheadings using h2 tags with natural keyword phrases
- Mention NakeyPen once only, naturally, in the final paragraph
- Sound human. Vary your rhythm. Do not be repetitive.

SEO RULES:
- Focus keyword must appear in: first paragraph, one h2, and 3 times naturally in the body
- Title: 50 to 60 characters, clear and click-worthy
- Meta description: 150 to 160 characters, includes focus keyword, compelling

OUTPUT: Return ONLY a raw JSON object. No markdown. No explanation. No code fences.
{{
  "chosen_topic": "the topic you picked",
  "title": "SEO title 50-60 chars",
  "meta_description": "150-160 char meta description",
  "focus_keyword": "main keyword phrase",
  "h1": "slightly more conversational than title",
  "subtitle": "one sentence to draw reader in, max 20 words",
  "body": "full post HTML using only p and h2 tags"
}}"""

body_payload = json.dumps({
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 2000,
    "messages": [{"role": "user", "content": prompt}]
}).encode()

req = urllib.request.Request(
    "https://api.anthropic.com/v1/messages",
    data=body_payload,
    headers={
        "x-api-key":         API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type":      "application/json"
    }
)

print("Calling API...")
try:
    with urllib.request.urlopen(req) as r:
        response = json.loads(r.read())
except urllib.error.HTTPError as e:
    print(f"API error {e.code}: {e.read().decode()}")
    raise

raw = response["content"][0]["text"].strip()
raw = re.sub(r"^```[a-z]*\n?", "", raw)
raw = re.sub(r"\n?```$", "", raw.strip())

post = json.loads(raw)

chosen_topic     = post["chosen_topic"]

# Generate clean URL slug from title
def make_slug(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:60]  # max 60 chars

base_slug = make_slug(post["title"])

# Ensure slug is unique — append -2, -3 etc if file already exists
url_slug = base_slug
counter  = 2
while os.path.exists(f"blogs/{url_slug}.html"):
    url_slug = f"{base_slug}-{counter}"
    counter += 1
title            = post["title"]
meta_description = post["meta_description"]
focus_keyword    = post["focus_keyword"]
h1               = post["h1"]
subtitle         = post["subtitle"]
body             = post["body"]

# Safety: strip any em dashes that slipped through
for dash in ["\u2014", "\u2013", " -- ", "--"]:
    body     = body.replace(dash, ", ")
    title    = title.replace(dash, " ")
    subtitle = subtitle.replace(dash, ", ")
    h1       = h1.replace(dash, " ")

print(f"Topic: {chosen_topic}")
print(f"Title: {title}")
print(f"Keyword: {focus_keyword}")

# ── Build HTML ────────────────────────────────────────────────────
canonical = f"{DOMAIN}/blogs/{url_slug}"

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<title>{title} - nakeyNails</title>
<meta name="description" content="{meta_description}"/>
<meta name="keywords" content="{focus_keyword}, nail repair, gel nail damage, acrylic nail recovery, NakeyPen, nail care"/>
<link rel="canonical" href="{canonical}"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{meta_description}"/>
<meta property="og:url" content="{canonical}"/>
<meta property="og:site_name" content="nakeyNails"/>
<meta property="article:published_time" content="{TODAY.isoformat()}"/>
<meta name="twitter:card" content="summary"/>
<meta name="twitter:title" content="{title}"/>
<meta name="twitter:description" content="{meta_description}"/>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{title}",
  "description": "{meta_description}",
  "datePublished": "{TODAY.isoformat()}",
  "dateModified": "{TODAY.isoformat()}",
  "author": {{"@type": "Organization", "name": "nakeyNails", "url": "{DOMAIN}"}},
  "publisher": {{"@type": "Organization", "name": "nakeyNails", "url": "{DOMAIN}"}},
  "mainEntityOfPage": {{"@type": "WebPage", "@id": "{canonical}"}},
  "keywords": "{focus_keyword}"
}}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=DM+Sans:wght@300;400&display=swap" rel="stylesheet">
<style>
:root {{
  --paper:#F9F6F1; --ink:#1A1610; --mid:#5C5650; --quiet:#9E9890;
  --serif:'Cormorant Garamond',Georgia,serif; --sans:'DM Sans',system-ui,sans-serif;
  --text-label:10px; --text-sm:clamp(13px,0.4vw + 11px,15px);
  --text-base:clamp(15px,0.4vw + 13px,17px); --text-lg:clamp(18px,0.6vw + 15px,22px);
  --gutter:clamp(24px,5vw,80px); --ease:cubic-bezier(0.22,1,0.36,1);
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
html{{scroll-behavior:smooth;}}
body{{background:var(--paper);color:var(--ink);font-family:var(--sans);font-weight:300;font-size:var(--text-base);line-height:1.65;-webkit-font-smoothing:antialiased;}}
a{{color:inherit;text-decoration:none;}}
button{{font:inherit;color:inherit;background:none;border:0;cursor:pointer;}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:24px var(--gutter);position:sticky;top:0;z-index:50;background:rgba(249,246,241,0.92);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-bottom:1px solid rgba(26,22,16,0.07);}}
.nav-brand{{display:inline-flex;align-items:center;flex-shrink:0;}}
.nav-brand img{{height:28px;width:auto;display:block;}}
.nav-links{{display:flex;gap:36px;font-size:11px;font-weight:400;letter-spacing:0.2em;text-transform:uppercase;color:var(--mid);}}
.nav-links a{{transition:color .2s;}}
.nav-links a:hover,.nav-links a.active{{color:var(--ink);}}
.nav-cta{{display:inline-flex;align-items:center;padding:10px 20px;background:var(--ink);color:var(--paper);font-size:10px;font-weight:400;letter-spacing:0.24em;text-transform:uppercase;transition:opacity .2s;white-space:nowrap;}}
.nav-cta:hover{{opacity:0.72;}}
.nav-menu{{display:none;}}
@media(max-width:720px){{.nav-links{{display:none;}}.nav-menu{{display:block;font-size:11px;letter-spacing:0.18em;text-transform:uppercase;}}}}
.menu-overlay{{display:none;position:fixed;inset:0;background:var(--paper);z-index:70;padding:28px var(--gutter);flex-direction:column;}}
.menu-overlay.open{{display:flex;}}
.menu-overlay-top{{display:flex;justify-content:space-between;align-items:center;}}
.menu-overlay nav{{margin-top:72px;display:flex;flex-direction:column;gap:8px;}}
.menu-overlay nav a{{font-family:var(--serif);font-size:clamp(36px,6vw,56px);font-weight:300;color:var(--ink);letter-spacing:-0.01em;padding:12px 0;transition:color .2s;}}
.menu-overlay nav a:hover{{color:var(--quiet);}}
.article{{max-width:680px;margin:0 auto;padding:clamp(56px,8vw,104px) var(--gutter) clamp(80px,10vw,140px);}}
.back{{font-size:var(--text-label);letter-spacing:0.22em;text-transform:uppercase;color:var(--quiet);display:inline-flex;align-items:center;gap:8px;margin-bottom:48px;transition:color .2s;}}
.back:hover{{color:var(--ink);}}
.article-label{{font-size:var(--text-label);letter-spacing:0.32em;text-transform:uppercase;color:var(--quiet);display:block;margin-bottom:24px;}}
h1{{font-family:var(--serif);font-size:clamp(36px,5vw + 16px,72px);font-weight:300;line-height:0.95;letter-spacing:-0.022em;margin-bottom:24px;}}
.subtitle{{font-size:var(--text-lg);color:var(--mid);line-height:1.65;margin-bottom:48px;padding-bottom:48px;border-bottom:1px solid rgba(26,22,16,0.08);}}
.body p{{color:var(--mid);line-height:1.85;margin-bottom:24px;font-size:var(--text-base);}}
.body h2{{font-family:var(--serif);font-size:clamp(22px,2vw + 14px,32px);font-weight:300;line-height:1.1;letter-spacing:-0.01em;color:var(--ink);margin:40px 0 16px;}}
.body p:last-child{{margin-bottom:0;}}
footer{{padding:40px var(--gutter);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;border-top:1px solid rgba(26,22,16,0.07);}}
.footer-brand{{font-family:var(--serif);font-size:16px;font-weight:400;letter-spacing:0.28em;text-transform:uppercase;}}
.footer-meta{{font-size:11px;letter-spacing:0.2em;text-transform:uppercase;color:var(--quiet);}}
</style>
</head>
<body>
<header class="nav">
  <a class="nav-brand" href="../index.html" aria-label="nakeyNails home">
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
<div class="menu-overlay" id="menuOverlay" role="dialog" aria-modal="true">
  <div class="menu-overlay-top">
    <span style="font-family:var(--serif);font-size:20px;letter-spacing:0.3em;text-transform:uppercase;">nakeyNails</span>
    <button id="menuClose" aria-label="Close" style="font-size:24px;color:var(--quiet);">&#215;</button>
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
<main class="article">
  <a class="back" href="index.html">&#8592; All posts</a>
  <span class="article-label">nakeyNails &middot; {DATE_STR}</span>
  <h1>{h1}</h1>
  <p class="subtitle">{subtitle}</p>
  <div class="body">{body}</div>
</main>
<footer>
  <span class="footer-brand">nakeyNails</span>
  <span class="footer-meta">&copy; {YEAR} &middot; Made in USA &middot; Dermatologist Tested</span>
  <span class="footer-meta">Privacy &middot; Terms</span>
</footer>
<script>
  const btn=document.getElementById('menuBtn'),close=document.getElementById('menuClose'),overlay=document.getElementById('menuOverlay');
  btn?.addEventListener('click',()=>{{overlay.classList.add('open');btn.setAttribute('aria-expanded','true');document.body.style.overflow='hidden';}});
  function closeMenu(){{overlay.classList.remove('open');btn.setAttribute('aria-expanded','false');document.body.style.overflow='';}}
  close?.addEventListener('click',closeMenu);
  overlay?.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
  document.addEventListener('keydown',e=>e.key==='Escape'&&closeMenu());
</script>
</body>
</html>"""

# ── Save post ─────────────────────────────────────────────────────
post_path = f"blogs/{url_slug}.html"
with open(post_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Saved: {post_path}")

# ── Track topic ───────────────────────────────────────────────────
topics_used.append(chosen_topic)
with open(TOPICS_FILE, "w") as f:
    json.dump(topics_used, f, indent=2)
print(f"Tracked topic: {chosen_topic}")

# ── Rebuild blogs/index.html ──────────────────────────────────────
# Match ALL post html files, not just date-named ones
all_files = [fn for fn in os.listdir("blogs")
             if fn.endswith(".html") and fn != "index.html"]

print(f"Found files: {all_files}")
posts_meta = []
for fn in all_files:
    with open(f"blogs/{fn}", encoding="utf-8") as f:
        ct = f.read()
    h1m = re.search(r"<h1>(.*?)</h1>", ct, re.DOTALL)
    sm  = re.search(r'<p class="subtitle">(.*?)</p>', ct, re.DOTALL)
    dm  = re.search(r'article:published_time" content="([^"]+)"', ct)
    pt       = h1m.group(1).strip() if h1m else fn[:-5]
    ps       = sm.group(1).strip()  if sm  else ""
    pub_date = dm.group(1).strip()  if dm  else TODAY.isoformat()
    try:
        dd = datetime.datetime.fromisoformat(pub_date).strftime("%b %d, %Y")
    except Exception:
        dd = DATE_STR
    posts_meta.append((pub_date, fn, pt, ps, dd))

posts_meta.sort(key=lambda x: x[0], reverse=True)

entries = ""
for pub_date, fn, pt, ps, dd in posts_meta:
    entries += f"""
    <a class="post-item reveal" href="{fn[:-5]}">
      <span class="post-date">{dd}</span>
      <div class="post-body">
        <h2>{pt}</h2>
        <p>{ps}</p>
        <span class="post-read">Read &#8594;</span>
      </div>
    </a>"""

with open("blogs/index.html", encoding="utf-8") as f:
    idx = f.read()
idx = re.sub(
    r"<!-- POST_ENTRIES -->.*?(?=\s*</div>)",
    f"<!-- POST_ENTRIES -->{entries}\n    <p class=\"search-empty\" id=\"searchEmpty\">No articles found for that search.</p>",
    idx, flags=re.DOTALL
)
with open("blogs/index.html", "w", encoding="utf-8") as f:
    f.write(idx)
print(f"Updated index: {len(posts_meta)} posts listed.")
print("Done.")
