#!/usr/bin/env python3
"""Bygger pilot/utmaningar/data/oversikt.json ur de sju reformfilerna (Sprint 17 del B).

Översikten driver pilotsidans startvy (jämförelsetabell reform × utmaningstyp) så att sidan
inte behöver läsa alla sju fullständiga datafiler vid start. Den fullständiga filen läses
först när en reform öppnas.

Deterministisk: inga tidsstämplar, fast reformordning, utmaningstyper i datafilernas ordning.
Kör från repo-roten:  python3 research/remissanalys/kedja/oversikt.py
"""
import json
import os
import sys

ROT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
DATA = os.path.join(ROT, 'pilot', 'utmaningar', 'data')
REFORMER = ['betyg', 'studiero', 'stod', 'tid', 'laroplaner', 'spraklig', 'tioarig']   # fast ordning


def fil_for(rid):
    return 'utmaningar-%s.json' % rid


def main():
    reformer = []
    typer = None
    for rid in REFORMER:
        with open(os.path.join(DATA, fil_for(rid)), encoding='utf-8') as f:
            d = json.load(f)
        if d['meta']['reform']['id'] != rid:
            sys.exit('Fel: %s har meta.reform.id %r' % (fil_for(rid), d['meta']['reform']['id']))
        namn = [t['namn'] for t in d['utmaningstyper']]
        if typer is None:
            typer = namn
        elif namn != typer:
            # Startvyns tabell förutsätter samma typer i samma ordning i alla filer.
            sys.exit('Fel: utmaningstyperna i %s skiljer sig från %s' % (fil_for(rid), fil_for(REFORMER[0])))
        rak = d['avsandarrakning']
        reformer.append({
            'id': rid,
            'namn': d['meta']['reform']['namn'],
            'sou': d['meta']['kedja']['utredningsbetankande']['nr'],
            'fil': fil_for(rid),
            'totalt_avsandare': rak['totalt']['antal_avsandare'],
            'utmaningar': len(d['utmaningar']),
            'per_utmaningstyp': {t: rak['per_utmaningstyp'][t]['antal_avsandare'] for t in typer},
        })
    ut = {
        '_meta': {
            'beskrivning': 'Översikt för pilotsidans startvy: per reform antal avsändare totalt och per primär '
                           'utmaningstyp (ur avsandarrakning) samt antal utmaningar. Byggd av '
                           'research/remissanalys/kedja/oversikt.py.',
            'källa': ['pilot/utmaningar/data/' + fil_for(r) for r in REFORMER],
        },
        'reformer': reformer,
        'utmaningstyper': typer,
    }
    with open(os.path.join(DATA, 'oversikt.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(ut, indent=1, ensure_ascii=False) + '\n')
    print('Skrev pilot/utmaningar/data/oversikt.json (%d reformer, %d utmaningstyper)' % (len(reformer), len(typer)))


if __name__ == '__main__':
    main()
