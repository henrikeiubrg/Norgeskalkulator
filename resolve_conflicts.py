#!/usr/bin/env python3
"""
Resolve merge conflicts by keeping HEAD version and adding background:#ffffff to related sections.
"""

import re

CONFLICT_FILES = [
    "/opt/Norgeskalkulator/levealder-kalkulator/index.html",
    "/opt/Norgeskalkulator/protein-kalkulator/index.html",
    "/opt/Norgeskalkulator/quiz-generator-alder/index.html",
]

def resolve_conflict(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if '<<<<<<<' not in content:
        print(f"  No conflicts found in {filepath}")
        return False

    # Resolve conflicts: keep HEAD version (between <<<<<<< HEAD and =======)
    def keep_head(match):
        head_content = match.group(1)
        return head_content

    resolved = re.sub(
        r'<<<<<<< HEAD\n(.*?)=======\n.*?>>>>>>> [^\n]+\n',
        keep_head,
        content,
        flags=re.DOTALL
    )

    # Now add background:#ffffff to the related-calculators section in this file
    # The HEAD version uses: <section class="related-calculators" style="max-width:800px;margin:2rem auto;padding:0 1rem;">
    # We want to add: background:#ffffff;
    resolved = resolved.replace(
        '<section class="related-calculators" style="max-width:800px;margin:2rem auto;padding:0 1rem;">',
        '<section class="related-calculators" style="max-width:800px;margin:2rem auto;padding:24px;background:#ffffff;border-radius:12px;">'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(resolved)

    print(f"  ✅ Resolved: {filepath}")
    return True


for f in CONFLICT_FILES:
    resolve_conflict(f)

print("\nDone!")
