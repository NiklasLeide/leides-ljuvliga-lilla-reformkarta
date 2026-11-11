#!/usr/bin/env python3
"""Granskningsunderlag per reform (Sprint 17 task 9): research/remissanalys/granskning/granskning-<id>.csv

Samma kolumner och format som Sprint 16:s granskning-betyg.csv (semikolon, UTF-8 med BOM, CRLF):
  Del 1, träffsäkerhet: utmaningar ur aktuell datafil pilot/utmaningar/data/utmaningar-<id>.json, jämnt fördelade över
         utmaningstyperna (kvot per typ, tak = antal i typen, överskott till nästa typ i typordning); inom typen ungefär 40 %
         med kopplingsnivån "tolkad" när sådana finns.
  Del 2, missade utmaningar: passager (passager.json) som inte kodades som utmaning, minst 200 tecken, inte innehållsförteckning
         och inte passager som bara återger utredningens förslag (samma mekaniska regler som Sprint 16).
Antal: betyg 40 + 20, övriga 15 + 5. Fasta slumpfrön per reform (FRO). Länk till rätt vy på pilotsidan (VY).
Användning: python3 research/remissanalys/kedja/granskning.py <reform-id>   (eller "alla")"""
import csv, json, os, random, re, sys, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
from gemensamt import ROT, las

PILOT = 'https://reformer.leide.se/dev/utmaningar-pilot/'
REFORMER = ['betyg', 'studiero', 'stod', 'tid', 'laroplaner', 'spraklig', 'tioarig']
FRO = {'betyg': 20261112, 'studiero': 20261121, 'stod': 20261122, 'tid': 20261123, 'laroplaner': 20261124, 'spraklig': 20261125, 'tioarig': 20261126}
ANTAL = {'betyg': (40, 20)}; STANDARD = (15, 5)
UTDIR = os.path.join(ROT, 'research/remissanalys/granskning')
ATERGIVER = re.compile(r'^\s*(utredningens förslag|utredningen föreslår|utredningens bedömning|utredningen bedömer|förslag i korthet|förslag:|sammanfattning av utredningens)', re.I)

def vy(rid, u):
    """Vyn på pilotsidan där utmaningen visas: reform, primär typ och första sakområde (eller "utan")."""
    sak = u['sakomrade'][0]['kapitel'] if u['sakomrade'] else 'utan'
    return PILOT + '#reform=' + rid + '&typ=' + urllib.parse.quote(u['utmaningstyp']['primar']) + '&sak=' + sak

def del1(D, n, rng):
    typer = [t['namn'] for t in D['utmaningstyper']]
    per = {t: [u for u in D['utmaningar'] if u['utmaningstyp']['primar'] == t] for t in typer}
    kvot = {t: 0 for t in typer}; kvar = n
    while kvar:   # jämn fördelning med tak per typ
        bar = [t for t in typer if kvot[t] < len(per[t])]
        if not bar: break
        for t in bar:
            if kvar and kvot[t] < len(per[t]): kvot[t] += 1; kvar -= 1
    ut = []
    for t in typer:
        if not kvot[t]: continue
        tolk = sorted([u for u in per[t] if u['koppling']['niva'] == 'tolkad'], key=lambda u: u['id'])
        ovr = sorted([u for u in per[t] if u['koppling']['niva'] != 'tolkad'], key=lambda u: u['id'])
        nt = min(len(tolk), round(kvot[t] * 0.4)); no = min(len(ovr), kvot[t] - nt); nt = kvot[t] - no
        ut += rng.sample(tolk, nt) + rng.sample(ovr, no)
    rng.shuffle(ut)
    return ut

def del2(rid, D, n, rng):
    kodade = {u['id'] for u in las(rid, 'kodning/utmaningar.json')['utmaningar']}
    BOXORD = [set(re.findall(r'[a-zåäöé]{4,}', f['text'].lower())) for f in D['utredningsforslag']]
    def bara_atergivning(p):
        if ATERGIVER.match(p['text']) or ATERGIVER.match(p.get('rubrik') or ''): return True
        if re.search(r'utredningens förslag', p['text'][:200], re.I) and not re.search(r'synpunkter', p['text'], re.I): return True
        w = set(re.findall(r'[a-zåäöé]{4,}', p['text'].lower()))
        return bool(w) and max(len(w & b) / len(w) for b in BOXORD) >= 0.6
    kand = [p for p in las(rid, 'passager.json')['passager']
            if p['id'] not in kodade and len(p['text']) >= 200 and not re.search(r'\.{5,}', p['text']) and not bara_atergivning(p)]
    return rng.sample(sorted(kand, key=lambda p: p['id']), min(n, len(kand))), len(kand)

def bygg(rid):
    D = json.load(open(os.path.join(ROT, f'pilot/utmaningar/data/utmaningar-{rid}.json'), encoding='utf-8'))
    n1, n2 = ANTAL.get(rid, STANDARD); rng = random.Random(FRO[rid])
    d1 = del1(D, n1, rng); d2, nkand = del2(rid, D, n2, rng)
    H1 = ['id', 'avsändare', 'citat', 'sida', 'länk till remissvaret', 'utmaningstyp', 'kopplingsnivå', 'sakområde', 'länk till vyn på pilotsidan',
          'Är det en utmaning? (ja/nej)', 'Rätt utmaningstyp? (ja/nej)', 'Rätt koppling? (ja/nej/går ej att bedöma)', 'Kommentar']
    H2 = ['passage-id', 'avsändare', 'passagens text', 'sida', 'länk till remissvaret', 'Innehåller passagen en utmaning som borde ha kommit med? (ja/nej)', 'Kommentar']
    os.makedirs(UTDIR, exist_ok=True); ut = os.path.join(UTDIR, f'granskning-{rid}.csv')
    with open(ut, 'w', encoding='utf-8-sig', newline='') as fh:
        w = csv.writer(fh, delimiter=';', quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')
        w.writerow([f'Del 1: Träffsäkerhet ({len(d1)} utmaningar)']); w.writerow(H1)
        for u in d1:
            w.writerow([u['id'], u['avsandare'], u['citat'], u['sida'], u['url'], u['utmaningstyp']['primar'], u['koppling']['niva'] or 'ingen koppling',
                        ' | '.join(s['rubrik'] for s in (u['sakomrade'] or [])) or 'Utan koppling till sakområde', vy(rid, u), '', '', '', ''])
        w.writerow([]); w.writerow([f'Del 2: Missade utmaningar ({len(d2)} passager som inte kodades som utmaning)']); w.writerow(H2)
        for p in d2: w.writerow([p['id'], p['avsandare'], p['text'], p['sida'], p['url'], '', ''])
    print(f"{rid}: del 1 {len(d1)} rader ({sum(u['koppling']['niva'] == 'tolkad' for u in d1)} tolkade), del 2 {len(d2)} rader (av {nkand} kandidater) -> {os.path.relpath(ut, ROT)}")

if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(__doc__)
    for r in (REFORMER if sys.argv[1] == 'alla' else [sys.argv[1]]): bygg(r)
