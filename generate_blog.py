#!/usr/bin/env python3
"""
generate_blog.py — nakeyNails weekly blog automation
1. Searches web for a trending nail care topic this week
2. Checks topics_used.json — never repeats a topic
3. Writes a 700-900 word SEO-optimised, human-sounding post
4. Saves blogs/YYYY-MM-DD.html
5. Updates blogs/index.html
6. Updates blogs/topics_used.json
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
print(f"Topics used: {len(topics_used)}")


def call_api(messages, tools=None, max_tokens=512):
    body = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": max_tokens,
        "messages": messages
    }
    if tools:
        body["tools"] = tools
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={
            "x-api-key":         API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json"
        }
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"API error {e.code}: {e.read().decode()}")
        raise


def extract_text(response):
    for block in response.get("content", []):
        if block.get("type") == "text":
            return block["text"].strip()
    return ""


def clean_json(text):
    text = re.sub(r"^```[a-z]*\n?", "", text.strip())
    text = re.sub(r"\n?```$", "", text.strip())
    return text.strip()


# ── STEP 1: Find trending topic ───────────────────────────────────
print("Step 1: Finding trending topic...")

topic_prompt = f"""You are a content strategist for nakeyNails — a nail repair brand for people recovering from gel and acrylic damage.

Today is {DATE_STR}. Search the web to find what nail care topics are being discussed or trending RIGHT NOW — check Reddit, Google searches, TikTok, Instagram, beauty blogs, and nail forums.

Pick ONE specific, fresh topic that:
- Is trending or highly relevant this week
- Relates to: nail repair, gel/acrylic damage recovery, nail health, nail growth, nail care routines, or nail ingredients
- Has NOT been covered before in this list:
{used_list}

The topic must be specific — not generic like "nail care tips". Think: a specific problem, question, ingredient, trend, or technique people are searching for RIGHT NOW.

Return ONLY raw JSON (no markdown):
{{"topic": "specific topic title", "reason": "why it is trending now"}}"""

topic_res = call_api(
    messages=[{"role": "user", "content": topic_prompt}],
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    max_tokens=1024
)

topic_text = clean_json(extract_text(topic_res))

try:
    topic_data   = json.loads(topic_text)
    chosen_topic = topic_data["topic"]
    topic_reason = topic_data.get("reason", "")
except Exception:
    m = re.search(r'"topic"\s*:\s*"([^"]+)"', topic_text)
    chosen_topic = m.group(1) if m else "How to rebuild nails after gel removal"
    topic_reason = ""

print(f"Topic: {chosen_topic}")
print(f"Reason: {topic_reason}")


# ── STEP 2: Write the blog post ───────────────────────────────────
print("Step 2: Writing post...")

write_prompt = f"""Write a blog post for nakeyNails (nakeynails.com).
NakeyPen is a nail repair serum for people whose nails are damaged from gel and acrylic.

Topic: {chosen_topic}

VOICE AND TONE:
- Write like a knowledgeable friend who works in beauty — warm, direct, no fluff
- Use "you" throughout — talk to the reader personally
- Vary your sentence length: mix short punchy sentences with longer explanatory ones
- Include one relatable scenario the reader will recognise (e.g. "If you've ever picked off a gel manicure...")
- Sound like a person who has seen this problem firsthand, not a blog generator

WHAT NOT TO DO:
- Never write: "delve", "comprehensive", "crucial", "it's important to note", "in conclusion", "game-changer", "furthermore", "moreover"
- Do not start consecutive sentences with the same word
- No bullet points or numbered lists — flowing paragraphs only
- Do not open with a question or "Are you..."
- Do not make it obvious AI wrote it

STRUCTURE:
- 700 to 900 words
- 3 to 4 subheadings using <h2> tags with natural keyword-rich phrases
- All text in <p> and <h2> tags only — no other HTML tags
- Mention NakeyPen once, naturally, in the final paragraph — do not make it promotional

SEO:
- Focus keyword must appear in: first paragraph, at least one h2, and 3-4 times naturally in the body
- Title: 50-60 characters, clear, compelling, includes the focus keyword
- Meta description: 150-160 characters, includes focus keyword, makes the reader want to click
- H1 can be slightly different from the title — more conversational

Return ONLY a raw JSON object, no markdown, no explanation:
{{
  "title": "...",
  "meta_description": "...",
  "focus_keyword": "...",
  "h1": "...",
  "subtitle": "one sentence that draws the reader in, max 25 words",
  "body": "full post HTML using only <p> and <h2> tags"
}}"""

post_res  = call_api(
    messages=[{"role": "user", "content": write_prompt}],
    max_tokens=2800
)

raw = clean_json(extract_text(post_res))
post = json.loads(raw)

title            = post["title"]
meta_description = post["meta_description"]
focus_keyword    = post["focus_keyword"]
h1               = post["h1"]
subtitle         = post["subtitle"]
body             = post["body"]

print(f"Title: {title}")
print(f"Keyword: {focus_keyword}")


# ── STEP 3: Build HTML ────────────────────────────────────────────
canonical = f"{DOMAIN}/blogs/{SLUG}.html"

html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"/>
<title>{title} · nakeyNails</title>
<meta name="description" content="{meta_description}"/>
<meta name="keywords" content="{focus_keyword}, nail repair, gel nail damage, acrylic nail recovery, NakeyPen, nail care"/>
<link rel="canonical" href="{canonical}"/>
<meta property="og:type"        content="article"/>
<meta property="og:title"       content="{title}"/>
<meta property="og:description" content="{meta_description}"/>
<meta property="og:url"         content="{canonical}"/>
<meta property="og:site_name"   content="nakeyNails"/>
<meta property="article:published_time" content="{TODAY.isoformat()}"/>
<meta name="twitter:card"        content="summary"/>
<meta name="twitter:title"       content="{title}"/>
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
a{{color:inherit;text-decoration:none;}} button{{font:inherit;color:inherit;background:none;border:0;cursor:pointer;}}
.nav{{display:flex;align-items:center;justify-content:space-between;padding:24px var(--gutter);position:sticky;top:0;z-index:50;background:rgba(249,246,241,0.92);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-bottom:1px solid rgba(26,22,16,0.07);}}
.nav-brand{{display:inline-flex;align-items:center;flex-shrink:0;}}
.nav-brand img{{height:28px;width:auto;display:block;}}
.nav-links{{display:flex;gap:36px;font-size:11px;font-weight:400;letter-spacing:0.2em;text-transform:uppercase;color:var(--mid);}}
.nav-links a{{transition:color .2s;}} .nav-links a:hover,.nav-links a.active{{color:var(--ink);}}
.nav-cta{{display:inline-flex;align-items:center;padding:10px 20px;background:var(--ink);color:var(--paper);font-size:10px;font-weight:400;letter-spacing:0.24em;text-transform:uppercase;transition:opacity .2s;white-space:nowrap;}}
.nav-cta:hover{{opacity:0.72;}} .nav-menu{{display:none;}}
@media(max-width:720px){{.nav-links{{display:none;}} .nav-menu{{display:block;font-size:11px;letter-spacing:0.18em;text-transform:uppercase;}}}}
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
  <a class="nav-brand" href="../index.html" aria-label="nakeyNails home"><img src="../logo.png" alt="nakeyNails"/></a>
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

# ── STEP 4: Save post ─────────────────────────────────────────────
post_path = f"blogs/{SLUG}.html"
with open(post_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Saved: {post_path}")

# ── STEP 5: Track topic ───────────────────────────────────────────
topics_used.append(chosen_topic)
with open(TOPICS_FILE, "w") as f:
    json.dump(topics_used, f, indent=2)
print(f"Tracked: {chosen_topic}")

# ── STEP 6: Rebuild blogs/index.html ─────────────────────────────
post_files = sorted(
    [fn for fn in os.listdir("blogs") if re.match(r"\d{4}-\d{2}-\d{2}\.html$", fn)],
    reverse=True
)

entries = ""
for fn in post_files:
    s = fn.replace(".html", "")
    with open(f"blogs/{fn}", encoding="utf-8") as f:
        ct = f.read()
    h1m = re.search(r"<h1>(.*?)</h1>", ct, re.DOTALL)
    sm  = re.search(r'<p class="subtitle">(.*?)</p>', ct, re.DOTALL)
    pt  = h1m.group(1).strip() if h1m else s
    ps  = sm.group(1).strip() if sm else ""
    try:
        dd = datetime.datetime.strptime(s, "%Y-%m-%d").strftime("%b %d, %Y")
    except Exception:
        dd = s
    entries += f"""
    <a class="post-item reveal" href="{fn}">
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
    f"<!-- POST_ENTRIES -->{entries}",
    idx, flags=re.DOTALL
)

with open("blogs/index.html", "w", encoding="utf-8") as f:
    f.write(idx)

print(f"Updated index with {len(post_files)} posts.")
print("Done.")
