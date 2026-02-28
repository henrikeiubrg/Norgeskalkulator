#!/usr/bin/env python3
"""
Optimize title tags (<60 chars) and meta descriptions (<155 chars)
for all norgeskalkulator.no calculator pages.
"""
import os
import re

# Optimized title tags - all under 60 chars
# Format varies by intent for natural diversity
TITLES = {
    "algebra-kalkulator": "Algebrakalkulator – Løs Ligninger Gratis | Norgeskalkulator",
    "alkoholprosent-kalkulator": "Alkoholprosent Kalkulator – Konverter til Baking",
    "barnetrygd-kalkulator": "Barnetrygdkalkulator 2026 – Beregn Barnetrygd",
    "bmi-kalkulator": "BMI Kalkulator – Er Vekten Din Normal? | Gratis",
    "boliglan-kalkulator": "Boliglånkalkulator 2026 – Beregn Låneevne og Kostnad",
    "bompenge-kalkulator": "Bompengekalkulator 2026 – Beregn Årlige Bomkostnader",
    "bryllupsbudsjett-kalkulator": "Bryllupsbudsjett Kalkulator 2026 – Planlegg Bryllup",
    "dagpenger-kalkulator": "Dagpengekalkulator 2026 – Beregn NAV Dagpenger",
    "distanse-kalkulator": "Sjøavstandskalkulator – Beregn Nautiske Mil og Reisetid",
    "drivstoff-kalkulator": "Drivstoffkalkulator 2026 – Beregn Bensin- og Dieselkostnad",
    "elbil-lading-kalkulator": "Elbil Ladekalkulator 2026 – Beregn Ladekostnader",
    "energisparing-kalkulator": "Energisparekalkulator 2026 – Beregn Strømbesparelse",
    "feriepenger-kalkulator": "Feriepengekalkulator 2026 – Beregn Feriepenger",
    "firmabil-kalkulator": "Firmabilkalkulator 2026 – Beregn Fordelsbeskatning",
    "fly-informasjon": "Flyinformasjon Norge – Avganger og Ankomster i Sanntid",
    "flyttekostnad-kalkulator": "Flyttekostnad Kalkulator 2026 – Beregn Pris på Flytting",
    "foreldrepenger-kalkulator": "Foreldrepengekalkulator 2026 – Beregn fra NAV",
    "levealder-kalkulator": "Levealder Kalkulator – Beregn Forventet Levealder",
    "lonn-over-under-snittet": "Tjener Du Over Snittet? | Lønnskalkulator 2026",
    "malings-kalkulator": "Malingskalkulator – Beregn Hvor Mye Maling Du Trenger",
    "overtids-kalkulator": "Overtidskalkulator 2026 – Beregn 40%, 50% og 100% Tillegg",
    "pensjon-kalkulator": "Pensjonskalkulator 2026 – Beregn Alderspensjon fra NAV",
    "promille-kalkulator": "Promillekalkulator 2026 – Beregn Alkoholpromille",
    "protein-kalkulator": "Proteinkalkulator – Beregn Daglig Proteinbehov",
    "quiz-generator-alder": "Quiz Generator – Spørsmål Tilpasset Alder | Gratis",
    "reisebudsjett-kalkulator": "Reisebudsjettkalkulator 2026 – Planlegg Feriebudsjettet",
    "ruter-tabell": "Ruter Sanntid – Avgangstavle Oslo og Akershus 2026",
    "skatte-kalkulator": "Skattekalkulator 2026 – Beregn Lønn Etter Skatt | Gratis",
    "sparing-over-under-snittet": "Sparer Du Nok? | Sparekalkulator 2026",
    "strompris-kalkulator": "Strømpris i Dag – Se Dagens Strømpriser | Norgeskalkulator",
    "studielan-kalkulator": "Studielånkalkulator 2026 – Beregn Nedbetaling og Renter",
    "sykepenger-kalkulator": "Sykepengekalkulator 2026 – Beregn Sykepenger fra NAV",
    "tilhengervekt-kalkulator": "Tilhengervekt Kalkulator – Beregn Lovlig Hengervekt",
    "timelonn-kalkulator": "Timelønnskalkulator 2026 – Regn Ut Timelønn fra Årslønn",
    "tv-storrelse-kalkulator": "TV Størrelse Kalkulator – Beregn Skjermens Lengde og Høyde",
}

# Optimized meta descriptions - all under 155 chars
DESCRIPTIONS = {
    "algebra-kalkulator": "Gratis algebrakalkulator som løser ligninger, plotter grafer og beregner uttrykk. Faktorisering, derivasjon og mer.",
    "alkoholprosent-kalkulator": "Beregn alkoholprosent for baking. Konverter mellom rom, konjakk og annen alkohol når oppskriften krever ulik styrke. Gratis.",
    "barnetrygd-kalkulator": "Beregn barnetrygd for 2026. Se ordinær barnetrygd, utvidet barnetrygd og småbarnstillegg basert på antall barn og alder.",
    "bmi-kalkulator": "Gratis BMI-kalkulator. Beregn kroppsmasseindeks og se om vekten din er normal, under- eller overvektig. For voksne og barn.",
    "boliglan-kalkulator": "Boliglånkalkulator for 2026. Beregn låneevne, månedlige kostnader og totalrente basert på inntekt, gjeld og egenkapital.",
    "bompenge-kalkulator": "Beregn årlige bomkostnader i 2026. Se bompenger for din daglige kjørerute med oppdaterte satser for hele Norge.",
    "bryllupsbudsjett-kalkulator": "Planlegg bryllupsbudsjettet ditt for 2026. Beregn kostnader for lokale, mat, fotograf, blomster og mer.",
    "dagpenger-kalkulator": "Beregn dagpenger fra NAV for 2026. Se beløp, varighet og barnetillegg basert på din inntekt. Oppdatert med siste G-satser.",
    "distanse-kalkulator": "Beregn sjøavstand i nautiske mil mellom havner verden over. Se reisetid og sjøruter. Gratis og nøyaktig.",
    "drivstoff-kalkulator": "Beregn bensin- og dieselkostnader for 2026. Se forbruk per km, total reisekostnad og sammenlign drivstoffpriser.",
    "elbil-lading-kalkulator": "Beregn elbil-ladekostnader for 2026. Sammenlign hjemmelading vs. offentlig hurtiglader. Se kostnad per km og ladetid.",
    "energisparing-kalkulator": "Beregn strømbesparelse med varmepumpe, solceller og isolasjon. Se årlig sparing for ditt norske hjem i 2026.",
    "feriepenger-kalkulator": "Beregn feriepenger for 2026. Se feriepengesats, opptjening og utbetaling basert på lønn og alder. Gratis kalkulator.",
    "firmabil-kalkulator": "Beregn fordelsbeskatning av firmabil i 2026. Se skattepliktig fordel, listepris-effekt og faktisk kostnad.",
    "fly-informasjon": "Se flyavganger og ankomster i sanntid for alle norske flyplasser. Oppdatert flyinformasjon for Avinor-flyplasser.",
    "flyttekostnad-kalkulator": "Beregn hva det koster å flytte i 2026. Se pris for flyttebyrå, leiebil, pakking og andre flyttekostnader.",
    "foreldrepenger-kalkulator": "Beregn foreldrepenger fra NAV for 2026. Velg 100% eller 80% sats og se månedlig utbetaling basert på din lønn.",
    "levealder-kalkulator": "Beregn din forventede levealder basert på livsstil, helse og vaner. Gratis kalkulator med personlige tips.",
    "lonn-over-under-snittet": "Sammenlign lønnen din med gjennomsnittet i Norge for 2026. Se om du tjener over eller under medianlønnen.",
    "malings-kalkulator": "Beregn hvor mye maling du trenger. Oppgi rommets mål og få eksakt antall liter og bokser. Gratis kalkulator.",
    "overtids-kalkulator": "Beregn overtidstillegg for 2026. Se utbetaling med 40%, 50% og 100% tillegg basert på din timelønn.",
    "pensjon-kalkulator": "Beregn alderspensjon fra NAV for 2026. Se estimert pensjon basert på inntekt, alder og opptjening.",
    "promille-kalkulator": "Beregn alkoholpromille basert på drikke, vekt, kjønn og tid. Se når du er edru og trygg å kjøre. Gratis.",
    "protein-kalkulator": "Beregn daglig proteinbehov basert på vekt, aktivitetsnivå og treningsmål. Tilpasset norske kostholdsråd.",
    "quiz-generator-alder": "Generer quizspørsmål tilpasset alder. Perfekt for bursdager, skoler og sammenkomster. Gratis og morsomt.",
    "reisebudsjett-kalkulator": "Planlegg feriebudsjettet for 2026. Beregn kostnader for fly, hotell, mat og aktiviteter per reisemål.",
    "ruter-tabell": "Se Ruter-avganger i sanntid for Oslo og Akershus. Buss, t-bane, trikk og tog fra din lokasjon. Oppdatert 2026.",
    "skatte-kalkulator": "Beregn lønn etter skatt for 2026. Oppdatert med trinnskatt, fradrag og formueskatt. Også tilgjengelig for 2025.",
    "sparing-over-under-snittet": "Sammenlign sparingen din med gjennomsnittet i Norge. Se om du sparer nok for alder og livssituasjon.",
    "strompris-kalkulator": "Se dagens og morgendagens strømpriser i Norge. Finn når strømmen er billigst. Alle prisområder oppdatert.",
    "studielan-kalkulator": "Beregn nedbetaling av studielån for 2026. Se månedlig betaling, renter og total kostnad over nedbetalingstiden.",
    "sykepenger-kalkulator": "Beregn sykepenger fra NAV og arbeidsgiver for 2026. Se utbetaling basert på lønn og sykmeldingsperiode.",
    "tilhengervekt-kalkulator": "Beregn lovlig tilhengervekt for din bil. Se maks vekt for tilhenger med og uten bremser. Oppdatert 2026.",
    "timelonn-kalkulator": "Regn ut timelønn fra årslønn eller månedslønn for 2026. Se netto timelønn etter skatt. Gratis kalkulator.",
    "tv-storrelse-kalkulator": "Beregn TV-skjermens lengde og høyde i cm fra tommer. Se anbefalt avstand og finn riktig TV-størrelse.",
}

def update_page(directory):
    filepath = os.path.join(directory, 'index.html')
    if not os.path.isfile(filepath):
        return False
    
    slug = directory.rstrip('/')
    if slug not in TITLES:
        return False
    
    html = open(filepath, 'r').read()
    original = html
    
    new_title = TITLES[slug]
    new_desc = DESCRIPTIONS[slug]
    
    # Validate lengths
    assert len(new_title) <= 60, f"{slug}: title too long ({len(new_title)}): {new_title}"
    assert len(new_desc) <= 155, f"{slug}: desc too long ({len(new_desc)}): {new_desc}"
    
    # Replace title
    html = re.sub(r'<title>.*?</title>', f'<title>{new_title}</title>', html, flags=re.DOTALL)
    
    # Replace meta description (handles multiline)
    html = re.sub(
        r'<meta\s+name="description"\s*\n?\s*content="[^"]*">',
        f'<meta name="description"\n    content="{new_desc}">',
        html
    )
    
    if html != original:
        open(filepath, 'w').write(html)
        print(f"  ✅ {slug}: title={len(new_title)}c, desc={len(new_desc)}c")
        return True
    else:
        print(f"  ⏭️  {slug}: no changes needed")
        return False

# Validate all specs first
print("Validating specs...")
for slug, title in TITLES.items():
    tlen = len(title)
    dlen = len(DESCRIPTIONS[slug])
    status = "✅" if tlen <= 60 and dlen <= 155 else "❌"
    if tlen > 60 or dlen > 155:
        print(f"  {status} {slug}: title={tlen}c, desc={dlen}c")

print("\nApplying changes...")
changed = 0
for d in sorted(os.listdir('.')):
    if os.path.isdir(d) and os.path.isfile(os.path.join(d, 'index.html')):
        if update_page(d):
            changed += 1

print(f"\nDone! Updated {changed} pages.")
