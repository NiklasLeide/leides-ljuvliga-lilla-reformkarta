#!/usr/bin/env python3
"""Räknar ifyllda granskningsfiler för Utmaningskartan (Sprint 17 task 9), per reform och totalt.

Användning:  python3 research/remissanalys/granskning/rakna-granskning.py [fil.csv ...]
             (utan argument: alla granskning-*.csv i samma mapp som skriptet)
Per fil (reform) och totalt över alla filer:
  Del 1: andel "ja" per fråga (av raderna besvarade med ja eller nej; "går ej att bedöma", tomma och ogiltiga redovisas separat),
         per fråga även per utmaningstyp och per kopplingsnivå för totalen
  Del 2: andel passager där granskaren svarat ja (missad utmaning)
Läser semikolonseparerad UTF-8 (med eller utan BOM). Svar tolkas skiftlägesokänsligt: ja / nej / går ej att bedöma."""
import collections, csv, glob, os, re, sys

MAPP = os.path.dirname(os.path.abspath(__file__))
FILER = sys.argv[1:] or sorted(glob.glob(os.path.join(MAPP, 'granskning-*.csv')))

def block(rader, rubrik_borjar):
    """Raderna i blocket som inleds med en rubrikrad 'Del N…' följd av kolumnrubriker."""
    start = next((i for i, r in enumerate(rader) if r and r[0].startswith(rubrik_borjar)), None)
    if start is None: return [], []
    hdr = rader[start + 1]; ut = []
    for r in rader[start + 2:]:
        if not r or not any(c.strip() for c in r) or r[0].startswith('Del '): break
        ut.append(dict(zip(hdr, r + [''] * (len(hdr) - len(r)))))
    return hdr, ut

def svar(v):
    v = (v or '').strip().lower()
    if v in ('ja', 'j', 'yes'): return 'ja'
    if v in ('nej', 'n', 'no'): return 'nej'
    if v.startswith('går ej') or v.startswith('gar ej') or v == 'vet ej': return 'går ej'
    return 'tomt' if not v else 'ogiltigt'

def andel(rows, fraga):
    c = collections.Counter(svar(r.get(fraga)) for r in rows)
    besv = c['ja'] + c['nej']
    pct = f'{100 * c["ja"] / besv:5.1f} %' if besv else '    – '
    extra = ', '.join(f'{k} {v}' for k, v in (('går ej att bedöma', c['går ej']), ('tomma', c['tomt']), ('ogiltiga', c['ogiltigt'])) if v)
    return f'{pct} ja ({c["ja"]} av {besv} besvarade)' + (f'; {extra}' if extra else '')

alla1, alla2, fragor1, fraga2 = [], [], None, None
for fil in FILER:
    rader = list(csv.reader(open(fil, encoding='utf-8-sig', newline=''), delimiter=';'))
    h1, d1 = block(rader, 'Del 1'); h2, d2 = block(rader, 'Del 2')
    reform = re.sub(r'^granskning-|\.csv$', '', os.path.basename(fil))
    fragor1 = fragor1 or [h for h in h1 if h.endswith(')') and 'ja/nej' in h]
    fraga2 = fraga2 or next((h for h in h2 if h.startswith('Innehåller passagen')), None)
    print(f'=== {reform} ({os.path.relpath(fil)}): del 1 {len(d1)} utmaningar, del 2 {len(d2)} passager')
    for f in fragor1: print(f'  {f}: {andel(d1, f)}')
    if fraga2: print(f'  {fraga2}: {andel(d2, fraga2)}')
    alla1 += [dict(r, reform=reform) for r in d1]; alla2 += d2

print(f'\n=== TOTALT ({len(FILER)} filer): del 1 {len(alla1)} utmaningar, del 2 {len(alla2)} passager')
for f in fragor1 or []:
    print(f'\n  {f}\n    Totalt: {andel(alla1, f)}')
    for gruppnamn, kol in (('reform', 'reform'), ('utmaningstyp', 'utmaningstyp'), ('kopplingsnivå', 'kopplingsnivå')):
        print(f'    Per {gruppnamn}:')
        for v in sorted({r[kol] for r in alla1}):
            sel = [r for r in alla1 if r[kol] == v]
            print(f'      {v:<45} n={len(sel):<3} {andel(sel, f)}')
if fraga2: print(f'\n  {fraga2}\n    Totalt: {andel(alla2, fraga2)}  (andel ja = andel passager med missad utmaning)')
