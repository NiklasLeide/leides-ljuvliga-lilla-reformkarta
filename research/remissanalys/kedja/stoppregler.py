#!/usr/bin/env python3
"""Steg K11 (deterministiskt): stoppreglerna för en reform, ur de incheckade kodningsfilerna.
  1. Andel Övrigt (primär typ efter regelprövning, dubbletter borträknade) får vara högst gemensamt.json stoppregler.ovrigt_max_andel.
  2. Samstämmighet: andel av dubbelkodningens stickprov där den oberoende kodaren gav samma primära typ som ordinarie kodning
     (före regelprövning) ska vara minst stoppregler.samstammighet_min_andel.
  3. Typnamnen ska vara exakt de åtta i gemensamt.json.
Flaggas men stoppar inte (Sprint 17): samstämmighet för identifiering under gränsen (kodning/dubbelidentifiering.json,
saknas för betyg före omkodningen) och färre än fem publicerade remissvar från fokusgrupperna (remissvar.json).
Avslutar med kod 1 om en regel bryts: reformen stoppas och rapporteras (Sprint 17 stoppvillkor).
Förutsättning: utmaningar.json (K7), kodning/utmaningstyp.json, kodning/dubbelkodning.json, kodning/regelprovning.json.
Användning: python3 research/remissanalys/kedja/stoppregler.py <reform-id>"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from gemensamt import reform_id, gemensamt, las

if __name__ == '__main__':
    rid = reform_id(); g0 = gemensamt(); sr = g0['stoppregler']; TYPER = {t[0] for t in g0['utmaningstyper']}
    uu = [u for u in las(rid, 'utmaningar.json')['utmaningar'] if not u['dublett_av']]
    logg = {x['id']: x['ny'] for x in las(rid, 'kodning/regelprovning.json')['andringar']}
    KOD = {x['id']: x for x in las(rid, 'kodning/utmaningstyp.json')['kodning']}
    dubbel = las(rid, 'kodning/dubbelkodning.json')['kodning']
    fel = []
    okanda = sorted({t for x in list(KOD.values()) + dubbel for t in (x['primar'], x.get('sekundar')) if t and t not in TYPER})
    if okanda: fel.append(f'okända typnamn: {okanda}')
    prim = [logg.get(u['id'], u['utmaningstyp']['primar']) for u in uu]
    ovr = prim.count('Övrigt') / len(prim) if prim else 0
    lika = sum(1 for d in dubbel if KOD[d['id']]['primar'] == d['primar'])
    sam = lika / len(dubbel) if dubbel else None
    print(f"{rid}: Övrigt {prim.count('Övrigt')}/{len(prim)} = {ovr:.1%} (max {sr['ovrigt_max_andel']:.0%}); "
          f"samstämmighet {lika}/{len(dubbel)} = " + (f"{sam:.1%}" if sam is not None else 'saknas') + f" (min {sr['samstammighet_min_andel']:.0%})")
    if ovr > sr['ovrigt_max_andel']: fel.append('andelen Övrigt överstiger gränsen')
    if sam is None: fel.append('dubbelkodning saknas')
    elif sam < sr['samstammighet_min_andel']: fel.append('samstämmigheten understiger gränsen')
    pid = os.path.join(os.path.dirname(__file__), '..', 'reformer', rid, 'kodning', 'dubbelidentifiering.json')
    if os.path.exists(pid):
        di = las(rid, 'kodning/dubbelidentifiering.json')['passager']; li = sum(x['overens'] for x in di)
        print(f"{rid}: samstämmighet identifiering {li}/{len(di)} = {li / len(di):.1%}" + ('  FLAGGA: under gränsen' if li / len(di) < sr['samstammighet_min_andel'] else ''))
    else: print(f'{rid}: samstämmighet identifiering: ingen dubbelidentifiering')
    npub = len(las(rid, 'remissvar.json')['publicerade'])
    print(f'{rid}: publicerade remissvar från fokusgrupperna {npub}' + ('  FLAGGA: färre än fem' if npub < 5 else ''))
    if fel: print('STOPP:', '; '.join(fel)); sys.exit(1)
    print('stoppregler: OK')
