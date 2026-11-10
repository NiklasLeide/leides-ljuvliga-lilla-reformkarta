#!/usr/bin/env python3
"""Bygger research/remissanalys/v2/granskning/granskning-betyg.csv (Sprint 16 T5).

Del 1, träffsäkerhet: 40 utmaningar ur pilot/utmaningar/data/utmaningar-betyg.json, 5 per utmaningstyp:
  2 med kopplingsnivå "tolkad" + 3 med annan nivå per typ (alla typer har minst 2 tolkade) => 16 tolkade.
Del 2, missade utmaningar: 20 passager ur förstudie 2:s 714 passager som inte kodades som utmaning,
  minst 200 tecken, och inte passager som bara återger utredningens förslag (regler nedan).

Användning (från repo-roten):
  python3 research/remissanalys/skript/v2/bygg-granskning.py            (läser research/remissanalys/arbetsfiler/passager-forstudie2.json)
  python3 research/remissanalys/skript/v2/bygg-granskning.py <passagefil>
Slumpfrö: SEED nedan (anges även i granskning/README.md). CSV: semikolon, UTF-8 med BOM."""
import csv, json, os, random, re, sys, urllib.parse

SEED = 20261112
ROT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
UT = os.path.join(ROT, 'research/remissanalys/v2/granskning/granskning-betyg.csv')
PILOT = 'https://reformer.leide.se/dev/utmaningar-pilot/'

D = json.load(open(os.path.join(ROT, 'pilot/utmaningar/data/utmaningar-betyg.json'), encoding='utf-8'))
V1 = json.load(open(os.path.join(ROT, 'research/remissanalys/utmaningar-betyg.json'), encoding='utf-8'))
# Passagefilen från förstudie 2 är incheckad (Sprint 16 T7); en annan sökväg kan anges som argument.
_pf = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROT, 'research/remissanalys/arbetsfiler/passager-forstudie2.json')
PASSAGER = json.load(open(_pf, encoding='utf-8'))
if isinstance(PASSAGER, dict): PASSAGER = PASSAGER['passager']
assert len(PASSAGER) == 714, f'väntade 714 passager, fick {len(PASSAGER)}'
rng = random.Random(SEED)

# ---------- del 1 ----------
def vy(u):
    sak = u['sakomrade'][0]['kapitel'] if u['sakomrade'] else 'utan'
    return PILOT + '#typ=' + urllib.parse.quote(u['utmaningstyp']['primar']) + '&sak=' + sak
del1 = []
for t in [x['namn'] for x in D['utmaningstyper']]:
    tolk = sorted([u for u in D['utmaningar'] if u['utmaningstyp']['primar'] == t and u['koppling']['niva'] == 'tolkad'], key=lambda u: u['id'])
    ovr = sorted([u for u in D['utmaningar'] if u['utmaningstyp']['primar'] == t and u['koppling']['niva'] != 'tolkad'], key=lambda u: u['id'])
    assert len(tolk) >= 2 and len(ovr) >= 3, t
    del1 += rng.sample(tolk, 2) + rng.sample(ovr, 3)
rng.shuffle(del1)

# ---------- del 2 ----------
kodade = {u['passage'] for u in V1['utmaningar']}          # alla 456 kodade (även dubbletter)
boxar = [f['text'] for f in D['utredningsforslag']]
def ord_(t): return set(re.findall(r'[a-zåäöé]{4,}', t.lower()))
BOXORD = [ord_(b) for b in boxar]
ATERGIVER = re.compile(r'^\s*(utredningens förslag|utredningen föreslår|utredningens bedömning|utredningen bedömer|förslag i korthet|förslag:|sammanfattning av utredningens)', re.I)
def bara_atergivning(p):
    """Mekaniska regler för passager som bara återger utredningens förslag:
    (a) passagen eller rubriken den står under börjar med 'Utredningens förslag', 'Utredningen föreslår', 'Förslag i korthet' m.fl.;
    (b) "Utredningens förslag" står bland passagens första 200 tecken (efter en avsnittsrubrik) och passagen saknar "Synpunkter";
    (c) minst 60 % av passagens ord (≥ 4 bokstäver) finns i en och samma förslagsruta i SOU 2025:18."""
    if ATERGIVER.match(p['text']) or ATERGIVER.match(p.get('rubrik') or ''): return True
    if re.search(r'utredningens förslag', p['text'][:200], re.I) and not re.search(r'synpunkter', p['text'], re.I): return True
    w = ord_(p['text'])
    return bool(w) and max(len(w & b) / len(w) for b in BOXORD) >= 0.6
kand = [p for p in PASSAGER if p['id'] not in kodade and len(p['text']) >= 200 and not re.search(r'\.{5,}', p['text']) and not bara_atergivning(p)]
del2 = rng.sample(sorted(kand, key=lambda p: p['id']), 20)

# ---------- skriv CSV ----------
H1 = ['id', 'avsändare', 'citat', 'sida', 'länk till remissvaret', 'utmaningstyp', 'kopplingsnivå', 'sakområde', 'länk till vyn på pilotsidan',
      'Är det en utmaning? (ja/nej)', 'Rätt utmaningstyp? (ja/nej)', 'Rätt koppling? (ja/nej/går ej att bedöma)', 'Kommentar']
H2 = ['passage-id', 'avsändare', 'passagens text', 'sida', 'länk till remissvaret',
      'Innehåller passagen en utmaning som borde ha kommit med? (ja/nej)', 'Kommentar']
os.makedirs(os.path.dirname(UT), exist_ok=True)
with open(UT, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, delimiter=';', quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')
    w.writerow(['Del 1: Träffsäkerhet (40 utmaningar)'])
    w.writerow(H1)
    for u in del1:
        w.writerow([u['id'], u['avsandare'], u['citat'], u['sida'], u['url'], u['utmaningstyp']['primar'],
                    u['koppling']['niva'] or 'ingen koppling', ' | '.join(s['rubrik'] for s in (u['sakomrade'] or [])) or 'Utan koppling till sakområde',
                    vy(u), '', '', '', ''])
    w.writerow([])
    w.writerow(['Del 2: Missade utmaningar (20 passager som inte kodades som utmaning)'])
    w.writerow(H2)
    for p in del2:
        w.writerow([p['id'], p['avsandare'], p['text'], p['sida'], p['url'], '', ''])
print(f'skrev {os.path.relpath(UT, ROT)}: del 1 {len(del1)} rader ({sum(u["koppling"]["niva"] == "tolkad" for u in del1)} tolkade), '
      f'del 2 {len(del2)} rader (av {len(kand)} kandidater)')
