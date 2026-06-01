#!/usr/bin/env python3
"""
add_canonicals.py
One-time script — adds canonical, og:url and og:type tags to any
blog post that doesn't already have them.
Run once via GitHub Actions, then delete.
"""

import os, re

DOMAIN   = "https://nakeynails.com"
blog_dir = "blogs"

files = [f for f in os.listdir(blog_dir)
         if f.endswith(".html") and f != "index.html"]

updated = 0

for fn in files:
    path = os.path.join(blog_dir, fn)
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Skip if canonical already present
    if 'rel="canonical"' in content:
        print(f"Skipping (already has canonical): {fn}")
        continue

    slug      = fn[:-5]
    canonical = f"{DOMAIN}/blogs/{slug}"

    # Build the tags to inject
    tags = (
        f'<link rel="canonical" href="{canonical}"/>\n'
        f'<meta property="og:type" content="article"/>\n'
        f'<meta property="og:url" content="{canonical}"/>\n'
    )

    # Inject after <meta name="viewport" .../>
    new_content = re.sub(
        r'(<meta name="viewport"[^/]*/>\s*)',
        r'\1' + tags,
        content,
        count=1
    )

    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated: {fn}")
        updated += 1
    else:
        print(f"No change: {fn}")

print(f"\nDone. Updated {updated} files.")
