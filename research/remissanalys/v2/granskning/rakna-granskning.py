#!/usr/bin/env python3
"""Räknar en ifylld granskning-betyg.csv (Sprint 16 T5).

Användning:  python3 rakna-granskning.py <ifylld csv>   (standard: granskning-betyg.csv i samma mapp)
Skriver ut:
  Del 1: andel "ja" per fråga, totalt, per utmaningstyp och per kopplingsnivå
         (andel ja av de rader där frågan besvarats med ja eller nej; "går ej att bedöma" och tomma rader redovisas separat)
  Del 2: andel passager där granskaren svarat ja (missad utmaning)
Läser semikolonseparerad UTF-8 (med eller utan BOM). Svar tolkas skiftlägesokänsligt: ja / nej / går ej att bedöma."""
import csv, os, sys, collections

FIL = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'granskning-betyg.csv')
rader = list(csv.reader(open(FIL, encoding='utf-8-sig', newline=''), delimiter=';'))

def block(rubrik_borjar):
    """Rader i blocket som inleds med en rubrikrad 'Del N…' följd av kolumnrubriker."""
    start = next(i for i, r in enumerate(rader) if r and r[0].startswith(rubrik_borjar))
    hdr = rader[start + 1]; ut = []
    for r in rader[start + 2:]:
        if not r or not any(c.strip() for c in r): break
        if r[0].startswith('Del '): break
        ut.append(dict(zip(hdr, r + [''] * (len(hdr) - len(r)))))
    return hdr, ut

def svar(v):
    v = (v or '').strip().lower()
    if v in ('ja', 'j', 'yes'): return 'ja'
    if v in ('nej', 'n', 'no'): return 'nej'
    if v.startswith('går ej') or v.startswith('gar ej') or v == 'vet ej': return 'går ej'
    return 'tomt' if not v else 'ogiltigt'

def andel(rows, fraga):
    c = collections.Counter(svar(r[fraga]) for r in rows)
    besv = c['ja'] + c['nej']
    pct = f'{100 * c["ja"] / besv:5.1f} %' if besv else '    – '
    extra = ', '.join(f'{k} {v}' for k, v in (('går ej att bedöma', c['går ej']), ('tomma', c['tomt']), ('ogiltiga', c['ogiltigt'])) if v)
    return f'{pct} ja ({c["ja"]} av {besv} besvarade)' + (f'; {extra}' if extra else '')

h1, d1 = block('Del 1')
FRAGOR = [h for h in h1 if h.endswith(')') and ('ja/nej' in h)]
print(f'Fil: {FIL}\n')
print(f'DEL 1 — träffsäkerhet ({len(d1)} utmaningar)')
for f in FRAGOR:
    print(f'\n  {f}')
    print(f'    Totalt: {andel(d1, f)}')
    for gruppnamn, kol in (('utmaningstyp', 'utmaningstyp'), ('kopplingsnivå', 'kopplingsnivå')):
        print(f'    Per {gruppnamn}:')
        for v in sorted({r[kol] for r in d1}):
            sel = [r for r in d1 if r[kol] == v]
            print(f'      {v:<45} n={len(sel):<3} {andel(sel, f)}')

try:
    h2, d2 = block('Del 2')
    f2 = next(h for h in h2 if h.startswith('Innehåller passagen'))
    print(f'\nDEL 2 — missade utmaningar ({len(d2)} passager)')
    print(f'  {f2}\n    {andel(d2, f2)}  (andel ja = andel passager med missad utmaning)')
except StopIteration:
    print('\nDEL 2 saknas i filen.')
