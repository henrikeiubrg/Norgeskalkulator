#!/usr/bin/env python3
"""
Fix critical bugs on norgeskalkulator.no:
1. Sitemap firmabilkalkulator URL typo
2. Broken internal links across all pages
3. H1 semantic fix: logo → div, calculator name h2 → h1
"""

import re
import os

REPO = "/opt/Norgeskalkulator"

# ─────────────────────────────────────────
# 1. Sitemap fix
# ─────────────────────────────────────────
sitemap_path = os.path.join(REPO, "sitemap.xml")
with open(sitemap_path, "r", encoding="utf-8") as f:
    content = f.read()

original = content
content = content.replace(
    "https://norgeskalkulator.no/firmabilkalkulator/",
    "https://norgeskalkulator.no/firmabil-kalkulator/"
)
if content != original:
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ sitemap.xml: Fixed firmabilkalkulator → firmabil-kalkulator")
else:
    print("⚠️  sitemap.xml: No change (already correct or pattern not found)")

# ─────────────────────────────────────────
# 2. Broken internal links
# ─────────────────────────────────────────
LINK_FIXES = [
    # (wrong, correct)
    ('href="/skattekalkulator"',          'href="/skatte-kalkulator/"'),
    ('href="/feriepengerkalkulator"',     'href="/feriepenger-kalkulator/"'),
    ('href="/drivstoffkalkulator"',       'href="/drivstoff-kalkulator/"'),
    ('href="/tv-storrelse"',              'href="/tv-storrelse-kalkulator/"'),
    ('href="/energisparing"',             'href="/energisparing-kalkulator/"'),
    ('href="/flyttekostnad"',             'href="/flyttekostnad-kalkulator/"'),
    ('href="/overtidkalkulator"',         'href="/overtids-kalkulator/"'),
    ('href="/overtidskalkulator"',        'href="/overtids-kalkulator/"'),
    ('href="/lonnskalkulator"',           'href="/timelonn-kalkulator/"'),
    ('href="/reisebudsjett"',             'href="/reisebudsjett-kalkulator/"'),
]

pages_dir = REPO
for folder in sorted(os.listdir(pages_dir)):
    fpath = os.path.join(pages_dir, folder, "index.html")
    if not os.path.isfile(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    original = content
    fixes_applied = []
    for wrong, correct in LINK_FIXES:
        if wrong in content:
            content = content.replace(wrong, correct)
            fixes_applied.append(f"{wrong} → {correct}")
    if content != original:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        for fix in fixes_applied:
            print(f"✅ {folder}/index.html: {fix}")

# ─────────────────────────────────────────
# 3. H1 semantic fix
# ─────────────────────────────────────────
# Pages that still have the logo as H1 (27 pages — distanse, bmi, levealder,
# lonn-over-under-snittet, protein, sparing-over-under-snittet already correct)
LOGO_H1_PAGES = [
    "algebra-kalkulator",
    "alkoholprosent-kalkulator",
    "barnetrygd-kalkulator",
    "boliglan-kalkulator",
    "bompenge-kalkulator",
    "bryllupsbudsjett-kalkulator",
    "dagpenger-kalkulator",
    "drivstoff-kalkulator",
    "energisparing-kalkulator",
    "feriepenger-kalkulator",
    "firmabil-kalkulator",
    "fly-informasjon",
    "flyttekostnad-kalkulator",
    "foreldrepenger-kalkulator",
    "malings-kalkulator",
    "matpris-oversikt",
    "overtids-kalkulator",
    "promille-kalkulator",
    "quiz-generator-alder",
    "reisebudsjett-kalkulator",
    "ruter-tabell",
    "skatte-kalkulator",
    "strompris-kalkulator",
    "sykepenger-kalkulator",
    "tilhengervekt-kalkulator",
    "timelonn-kalkulator",
    "tv-storrelse-kalkulator",
]

# The logo h1 always starts with this exact string
LOGO_H1_OPEN = '<h1 style="font-size: 1.5em; text-align: center;">'
LOGO_DIV_OPEN = '<div style="font-size: 1.5em; text-align: center;">'

# Inline style to apply to promoted h1 so it visually matches the old h2
H1_INLINE = ' style="font-size: 1.5em; font-weight: 500; color: #4a5568;"'

for folder in LOGO_H1_PAGES:
    fpath = os.path.join(REPO, folder, "index.html")
    if not os.path.isfile(fpath):
        print(f"⚠️  {folder}/index.html not found, skipping")
        continue

    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # Step A: Replace the logo h1 opening tag
    if LOGO_H1_OPEN not in content:
        print(f"⚠️  {folder}/index.html: Logo H1 opening not found, skipping H1 fix")
        continue

    # Replace logo <h1 ...> with <div ...>
    # We need to replace the first </h1> that closes the logo block too.
    # Strategy: replace LOGO_H1_OPEN, then replace the very next </h1> with </div>
    content = content.replace(LOGO_H1_OPEN, LOGO_DIV_OPEN, 1)

    # Find position of LOGO_DIV_OPEN and replace the next </h1> after it
    div_pos = content.index(LOGO_DIV_OPEN)
    close_h1_pos = content.index("</h1>", div_pos)
    content = content[:close_h1_pos] + "</div>" + content[close_h1_pos + len("</h1>"):]

    # Step B: Promote first <h2> (the calculator title) to <h1>
    # Find first <h2> — could be <h2> or <h2 style="...">
    h2_match = re.search(r'<h2([^>]*)>', content)
    if h2_match:
        existing_attrs = h2_match.group(1)
        # If h2 has no inline style, add our own to preserve the visual
        if 'style=' not in existing_attrs:
            new_h1_open = f'<h1{H1_INLINE}>'
        else:
            # Keep existing style but change tag
            new_h1_open = f'<h1{existing_attrs}>'
        content = content[:h2_match.start()] + new_h1_open + content[h2_match.end():]

        # Find the first </h2> after this position and change to </h1>
        h2_close_pos = content.index("</h2>", h2_match.start())
        content = content[:h2_close_pos] + "</h1>" + content[h2_close_pos + len("</h2>"):]
    else:
        print(f"⚠️  {folder}/index.html: No <h2> found for promotion")

    if content != original:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ {folder}/index.html: H1 semantic fix applied")
    else:
        print(f"⚠️  {folder}/index.html: No H1 changes made")

print("\n✅ All done.")
