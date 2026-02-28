#!/usr/bin/env python3
"""
Add internal linking to all calculator pages on norgeskalkulator.no.
- Adds "Relaterte Kalkulatorer" card section before footer
- Adds 2-3 contextual in-text links within content
"""
import os
import re

# Calculator clusters
CLUSTERS = {
    'okonomi': [
        'skatte-kalkulator', 'timelonn-kalkulator', 'boliglan-kalkulator',
        'studielan-kalkulator', 'pensjon-kalkulator', 'lonn-over-under-snittet',
        'feriepenger-kalkulator', 'dagpenger-kalkulator', 'sykepenger-kalkulator',
        'overtids-kalkulator', 'sparing-over-under-snittet', 'foreldrepenger-kalkulator',
        'barnetrygd-kalkulator'
    ],
    'kjoretoy': [
        'drivstoff-kalkulator', 'elbil-lading-kalkulator', 'bompenge-kalkulator',
        'tilhengervekt-kalkulator', 'firmabil-kalkulator'
    ],
    'helse': [
        'bmi-kalkulator', 'protein-kalkulator', 'promille-kalkulator',
        'alkoholprosent-kalkulator', 'levealder-kalkulator'
    ],
    'bolig': [
        'boliglan-kalkulator', 'energisparing-kalkulator', 'strompris-kalkulator',
        'malings-kalkulator', 'flyttekostnad-kalkulator', 'tv-storrelse-kalkulator'
    ],
    'reise': [
        'reisebudsjett-kalkulator', 'ruter-tabell', 'fly-informasjon',
        'distanse-kalkulator', 'bryllupsbudsjett-kalkulator', 'algebra-kalkulator',
        'quiz-generator-alder'
    ]
}

# Display names and descriptions for each calculator
CALC_INFO = {
    'skatte-kalkulator': ('Skattekalkulator', 'Beregn skatten din for inneværende år'),
    'timelonn-kalkulator': ('Timelønn-kalkulator', 'Regn ut timelønn fra årslønn eller månedslønn'),
    'boliglan-kalkulator': ('Boliglånskalkulator', 'Beregn månedlige avdrag og totalkostnad'),
    'studielan-kalkulator': ('Studielånskalkulator', 'Se nedbetalingsplan for studielånet ditt'),
    'pensjon-kalkulator': ('Pensjonskalkulator', 'Estimer fremtidig pensjon og sparebehov'),
    'lonn-over-under-snittet': ('Lønn over/under snittet', 'Sammenlign lønnen din med gjennomsnittet'),
    'feriepenger-kalkulator': ('Feriepengekalkulator', 'Beregn hvor mye du får i feriepenger'),
    'dagpenger-kalkulator': ('Dagpengekalkulator', 'Se hva du kan få i dagpenger ved arbeidsledighet'),
    'sykepenger-kalkulator': ('Sykepengekalkulator', 'Beregn sykepenger basert på inntekt'),
    'overtids-kalkulator': ('Overtidskalkulator', 'Regn ut overtidsbetaling og tillegg'),
    'sparing-over-under-snittet': ('Sparing over/under snittet', 'Sammenlign sparingen din med andre'),
    'foreldrepenger-kalkulator': ('Foreldrepengekalkulator', 'Beregn foreldrepenger ved fødsel'),
    'barnetrygd-kalkulator': ('Barnetrygdkalkulator', 'Se hvor mye du får i barnetrygd'),
    'drivstoff-kalkulator': ('Drivstoffkalkulator', 'Beregn drivstoffkostnader for reisen'),
    'elbil-lading-kalkulator': ('Elbil ladekalkulator', 'Regn ut ladekostnader for elbilen din'),
    'bompenge-kalkulator': ('Bompengekalkulator', 'Beregn bompengekostnader for ruten din'),
    'tilhengervekt-kalkulator': ('Tilhengervektkalkulator', 'Sjekk tillatt tilhengervekt for bilen'),
    'firmabil-kalkulator': ('Firmabilkalkulator', 'Beregn skatt på firmabil'),
    'bmi-kalkulator': ('BMI-kalkulator', 'Sjekk om vekten din er innenfor normalområdet'),
    'protein-kalkulator': ('Proteinkalkulator', 'Beregn daglig proteinbehov'),
    'promille-kalkulator': ('Promillekalkulator', 'Estimer promillenivå etter alkoholinntak'),
    'alkoholprosent-kalkulator': ('Alkoholprosentkalkulator', 'Beregn alkoholprosent i hjemmebrygg'),
    'levealder-kalkulator': ('Levealder-kalkulator', 'Estimer forventet levealder basert på livsstil'),
    'energisparing-kalkulator': ('Energisparingkalkulator', 'Se hvor mye du kan spare på strøm'),
    'strompris-kalkulator': ('Strømpriskalkulator', 'Beregn strømkostnader og sammenlign priser'),
    'malings-kalkulator': ('Malingskalkulator', 'Beregn hvor mye maling du trenger'),
    'flyttekostnad-kalkulator': ('Flyttekostnadkalkulator', 'Estimer kostnader ved flytting'),
    'tv-storrelse-kalkulator': ('TV-størrelse kalkulator', 'Finn riktig TV-størrelse for rommet'),
    'reisebudsjett-kalkulator': ('Reisebudsjettkalkulator', 'Planlegg budsjettet for reisen din'),
    'ruter-tabell': ('Ruter-tabell', 'Se avgangstider og rutetabeller'),
    'fly-informasjon': ('Flyinformasjon', 'Sjekk flyavganger og ankomster'),
    'distanse-kalkulator': ('Distansekalkulator', 'Beregn avstand mellom steder'),
    'bryllupsbudsjett-kalkulator': ('Bryllupsbudsjettkalkulator', 'Planlegg budsjettet for bryllupet'),
    'algebra-kalkulator': ('Algebrakalkulator', 'Løs algebraiske ligninger og uttrykk'),
    'quiz-generator-alder': ('Aldersquiz', 'Morsom quiz som gjetter alderen din'),
}

# Cross-cluster connections (source_cluster -> [target slugs from other clusters])
CROSS_CLUSTER = {
    'okonomi': ['boliglan-kalkulator', 'energisparing-kalkulator', 'firmabil-kalkulator'],
    'kjoretoy': ['skatte-kalkulator', 'reisebudsjett-kalkulator'],
    'helse': ['levealder-kalkulator', 'drivstoff-kalkulator'],
    'bolig': ['skatte-kalkulator', 'boliglan-kalkulator', 'flyttekostnad-kalkulator'],
    'reise': ['drivstoff-kalkulator', 'bompenge-kalkulator'],
}

def get_clusters_for(slug):
    """Return list of cluster names this slug belongs to."""
    return [c for c, members in CLUSTERS.items() if slug in members]

def get_related(slug, count=5):
    """Get related calculator slugs for a page."""
    clusters = get_clusters_for(slug)
    related = []
    
    # Same cluster first
    for cluster in clusters:
        for member in CLUSTERS[cluster]:
            if member != slug and member not in related:
                related.append(member)
    
    # Cross-cluster
    for cluster in clusters:
        for cross in CROSS_CLUSTER.get(cluster, []):
            if cross != slug and cross not in related:
                related.append(cross)
    
    # If still not enough, add popular calcs
    popular = ['skatte-kalkulator', 'bmi-kalkulator', 'boliglan-kalkulator', 
               'timelonn-kalkulator', 'pensjon-kalkulator']
    for p in popular:
        if p != slug and p not in related:
            related.append(p)
    
    return related[:count]

def build_related_section(slug):
    """Build the HTML for related calculators section."""
    related = get_related(slug, 5)
    cards = []
    for r in related:
        name, desc = CALC_INFO.get(r, (r, ''))
        cards.append(f'''    <a href="/{r}/" style="display:block;padding:1rem;border:1px solid #e2e8f0;border-radius:8px;text-decoration:none;color:inherit;transition:box-shadow .2s;">
      <strong style="color:#ea580c;">{name}</strong>
      <p style="font-size:.85rem;color:#64748b;margin:.4rem 0 0;">{desc}</p>
    </a>''')
    
    cards_html = '\n'.join(cards)
    return f'''
    <!-- Relaterte Kalkulatorer -->
    <section class="related-calculators" style="max-width:800px;margin:2rem auto;padding:0 1rem;">
      <h2 style="font-size:1.4rem;margin-bottom:1rem;color:#1e293b;">Relaterte kalkulatorer</h2>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:1rem;">
{cards_html}
      </div>
    </section>
'''

def add_contextual_links(html, slug):
    """Add contextual in-text links within article/section content.
    Only adds links if not already present. Targets 2-3 links."""
    related = get_related(slug, 6)
    links_added = 0
    
    for r in related:
        if links_added >= 3:
            break
        # Skip if already linked
        if f'/{r}/' in html:
            continue
        
        name, desc = CALC_INFO.get(r, (r, ''))
        # Try to find a mention of the concept in the text to link
        # Use simple keyword matching
        keywords = {
            'skatte-kalkulator': ['skatt', 'skatten', 'skatteberegning'],
            'timelonn-kalkulator': ['timelønn', 'lønn', 'timeløn'],
            'boliglan-kalkulator': ['boliglån', 'lån', 'lånet', 'boliglånet'],
            'studielan-kalkulator': ['studielån', 'studielånet'],
            'pensjon-kalkulator': ['pensjon', 'pensjonen'],
            'feriepenger-kalkulator': ['feriepenger', 'feriepengene'],
            'dagpenger-kalkulator': ['dagpenger', 'dagpengene', 'arbeidsledig'],
            'sykepenger-kalkulator': ['sykepenger', 'sykepengene', 'sykmelding'],
            'overtids-kalkulator': ['overtid', 'overtids'],
            'foreldrepenger-kalkulator': ['foreldrepenger', 'foreldrepermisjon'],
            'barnetrygd-kalkulator': ['barnetrygd'],
            'drivstoff-kalkulator': ['drivstoff', 'bensin', 'diesel'],
            'elbil-lading-kalkulator': ['elbil', 'lading', 'ladekostnad'],
            'bompenge-kalkulator': ['bompenger', 'bompenge', 'bomavgift'],
            'tilhengervekt-kalkulator': ['tilhenger', 'tilhengervekt'],
            'firmabil-kalkulator': ['firmabil'],
            'bmi-kalkulator': ['BMI', 'kroppsmasseindeks', 'vekt'],
            'protein-kalkulator': ['protein', 'proteinbehov'],
            'promille-kalkulator': ['promille', 'alkohol'],
            'alkoholprosent-kalkulator': ['alkoholprosent', 'hjemmebrygg'],
            'levealder-kalkulator': ['levealder', 'forventet levetid'],
            'energisparing-kalkulator': ['energisparing', 'strømsparing'],
            'strompris-kalkulator': ['strømpris', 'strømkostnad', 'strømregning'],
            'malings-kalkulator': ['maling', 'male'],
            'flyttekostnad-kalkulator': ['flytting', 'flyttekostnad'],
            'tv-storrelse-kalkulator': ['TV-størrelse', 'TV størrelse'],
            'reisebudsjett-kalkulator': ['reisebudsjett', 'reise'],
            'bompenge-kalkulator': ['bompenger', 'bompenge'],
        }
        
        kws = keywords.get(r, [])
        for kw in kws:
            # Look for the keyword in paragraph text (not in tags/attributes)
            # Simple: find <p>...</p> containing the keyword without an existing link around it
            pattern = re.compile(
                r'(<p[^>]*>(?:(?!</p>).)*?)(\b' + re.escape(kw) + r'\b)((?:(?!</p>).)*?</p>)',
                re.IGNORECASE | re.DOTALL
            )
            match = pattern.search(html)
            if match:
                before, word, after = match.group(1), match.group(2), match.group(3)
                # Check there's no <a> tag wrapping this
                context = match.group(0)
                # Simple check: no href= near the keyword
                word_pos = context.find(word)
                nearby = context[max(0,word_pos-50):word_pos+len(word)+50]
                if 'href=' not in nearby:
                    link = f'<a href="/{r}/">{word}</a>'
                    new_text = before + link + after
                    html = html[:match.start()] + new_text + html[match.end():]
                    links_added += 1
                    break
    
    return html

def process_page(slug):
    """Process a single calculator page."""
    filepath = os.path.join(slug, 'index.html')
    if not os.path.exists(filepath):
        print(f"  SKIP {slug} - no index.html")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Check if already has related section
    if 'related-calculators' in html:
        print(f"  SKIP {slug} - already has related section")
        return False
    
    # Add related calculators section before footer
    related_html = build_related_section(slug)
    
    # Find the footer
    footer_match = re.search(r'(\s*<footer\s+class="calculator-footer")', html)
    if footer_match:
        insert_pos = footer_match.start()
        html = html[:insert_pos] + related_html + html[insert_pos:]
    else:
        # Try generic footer
        footer_match = re.search(r'(\s*<footer)', html)
        if footer_match:
            insert_pos = footer_match.start()
            html = html[:insert_pos] + related_html + html[insert_pos:]
        else:
            print(f"  WARN {slug} - no footer found, appending before </body>")
            html = html.replace('</body>', related_html + '\n</body>')
    
    # Add contextual in-text links
    html = add_contextual_links(html, slug)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"  OK {slug}")
    return True

def main():
    os.chdir('/root/Norgeskalkulator')
    
    all_slugs = sorted(CALC_INFO.keys())
    updated = 0
    
    for slug in all_slugs:
        if process_page(slug):
            updated += 1
    
    print(f"\nDone: {updated}/{len(all_slugs)} pages updated")

if __name__ == '__main__':
    main()
