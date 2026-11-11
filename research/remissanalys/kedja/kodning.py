#!/usr/bin/env python3
"""Stöd för modellkodningen M1–M3 (Sprint 17 T2): deterministiska underlag till kodarna och sammanslagning av deras svar.
Kodarna följer research/remissanalys/kedja/KODINSTRUKTION.md. Underlag och råsvar ligger i reformer/<id>/kallor/kodning/
(cache inne i repot, checkas inte in). Sammanslagna kodfiler skrivs till reformer/<id>/kodning/ och checkas in.

Användning: python3 research/remissanalys/kedja/kodning.py <reform-id> <kommando>
  m1-underlag     passager.json → m1-batch-<n>.json (hela remissvar per batch, ~110 000 tecken) och
                  m1-dubbel.json (40 slumpvis valda passager ≥ 100 tecken, frö SEED_ID) för den oberoende identifieringen
  m1-ihop         m1-resultat-<n>.json → kodning/utmaningar.json (citaten kontrolleras som delsträng av passagen; uid i
                  passagernas ordning), m1-dubbel-resultat.json → kodning/dubbelidentifiering.json
  m2-underlag     (efter K7 utan typ) utmaningar utan dubbletter → m2-batch-<n>.json (~120 st per batch) och
                  m2-dubbel.json (40 slumpvis valda, frö SEED_TYP)
  m2-ihop         m2-resultat-<n>.json → kodning/utmaningstyp.json, m2-dubbel-resultat.json → kodning/dubbelkodning.json
  m2c-underlag    utmaningar med primär typ Otydlighet/Likvärdighet → m2c-underlag.json
  m2c-ihop        m2c-resultat.json → kodning/regelprovning.json
  m2d-underlag    (efter M2c) 80 slumpvis valda utmaningar (frö SEED_TYP_EFTER) för oberoende typning efter regelprövning
  m2d-ihop        m2d-resultat.json → kodning/dubbelkodning-efter-regelprovning.json (jämförs med primär typ efter M2c)
  m3-underlag     (efter K7 med typ) utmaningar utan egen hänvisning → m3-batch-1/2.json + m3-forslag.json
  m3-ihop         m3-resultat-<n>.json → kodning/tolkad-koppling.json
Samstämmighet för identifiering: andel av de 40 passagerna där M1-kodaren och den oberoende kodaren är överens om huruvida
passagen innehåller minst en utmaning. För typning: andel av de 40 utmaningarna med samma primära typ (stoppregler.py)."""
import glob, json, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from gemensamt import config, gemensamt, las, skriv, mapp

SEED_ID, SEED_TYP, N_STICKPROV = 20261201, 20261202, 40
SEED_TYP_EFTER, N_STICKPROV_EFTER = 20261203, 80   # Sprint 17 A4: typning efter regelprövning (betyg)
OT, LI = 'Otydlighet i förslaget', 'Likvärdighet och konsekvenser för elever'

def k(rid, namn): return mapp(rid, 'kallor', 'kodning', namn)
def ut(rid, namn, data):
    with open(k(rid, namn), 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=1)
    print('  skrev', os.path.relpath(k(rid, namn)))
def inn(rid, namn): return json.load(open(k(rid, namn), encoding='utf-8'))
def resultat(rid, prefix):
    fl = sorted(glob.glob(k(rid, prefix + '-*.json')), key=lambda p: int(p.rsplit('-', 1)[1][:-5]))
    if not fl: sys.exit(f'inga {prefix}-*.json i kallor/kodning/')
    return [(int(p.rsplit('-', 1)[1][:-5]), json.load(open(p, encoding='utf-8'))) for p in fl]
def lista(x): return x if isinstance(x, list) else next(v for v in x.values() if isinstance(v, list))

def m1_underlag(rid):
    P = las(rid, 'passager.json')['passager']
    per_dok = {}
    for p in P: per_dok.setdefault(p['dok'], []).append({'id': p['id'], 'avsandare': p['avsandare'], 'sida': p['sida'], 'rubrik': p['rubrik'], 'text': p['text']})
    batcher = [[]]; storlek = 0
    for dok, pp in per_dok.items():
        n = sum(len(p['text']) for p in pp)
        if batcher[-1] and storlek + n > 110000: batcher.append([]); storlek = 0
        batcher[-1] += pp; storlek += n
    for i, b in enumerate(batcher, 1): ut(rid, f'm1-batch-{i}.json', b)
    kand = sorted([p for p in P if len(p['text']) >= 100], key=lambda p: p['id'])
    urval = random.Random(SEED_ID).sample(kand, min(N_STICKPROV, len(kand)))
    ut(rid, 'm1-dubbel.json', [{'id': p['id'], 'avsandare': p['avsandare'], 'sida': p['sida'], 'rubrik': p['rubrik'], 'text': p['text']} for p in urval])
    print(f'{rid}: {len(P)} passager i {len(batcher)} batcher; stickprov {len(urval)}')

def kontrollera_m1(P, rader, var):
    fel = [r for r in rader if r['id'] not in P or r['citat'] not in P[r['id']]['text']]
    if fel: sys.exit(f'{var}: {len(fel)} citat är inte ordagranna delsträngar av passagen, t.ex. {fel[0]["id"]}: {fel[0]["citat"][:80]}')

def m1_ihop(rid):
    P = {p['id']: p for p in las(rid, 'passager.json')['passager']}; ordning = {pid: i for i, pid in enumerate(P)}
    rader = []
    for n, r in resultat(rid, 'm1-resultat'): r = lista(r); kontrollera_m1(P, r, f'm1-resultat-{n}'); rader += [dict(x, _kodare=n) for x in r]
    rader.sort(key=lambda r: (ordning[r['id']], P[r['id']]['text'].find(r['citat'])))
    utm = [{'uid': f'U{i:03d}', 'id': r['id'], 'citat': r['citat'], 'oppen_kod': r.get('oppen_kod'), 'beskrivning': r.get('beskrivning')} for i, r in enumerate(rader, 1)]
    nk = len({r['_kodare'] for r in rader})
    skriv(rid, 'kodning/utmaningar.json', {'_meta': {'steg': f'M1 identifiering av utmaningar (modellkodning, Sprint 17; {nk} parallella kodare, en per batch av passager, instruktion research/remissanalys/kedja/KODINSTRUKTION.md)',
                                                     'tolkning': True, 'falt': {'uid': 'utmaningens id', 'id': 'passage-id', 'citat': 'ordagrann delsträng ur passagen', 'oppen_kod': 'kodarens öppna kod (spårbarhet; visas aldrig)', 'beskrivning': 'kodarens beskrivning (spårbarhet; visas aldrig)'}},
                                           'utmaningar': utm})
    d = inn(rid, 'm1-dubbel.json'); b = lista(inn(rid, 'm1-dubbel-resultat.json')); kontrollera_m1(P, b, 'm1-dubbel-resultat')
    a_n = {}; b_n = {}
    for r in rader: a_n[r['id']] = a_n.get(r['id'], 0) + 1
    for r in b: b_n[r['id']] = b_n.get(r['id'], 0) + 1
    pp = [{'id': p['id'], 'kodare_a_antal': a_n.get(p['id'], 0), 'kodare_b_antal': b_n.get(p['id'], 0),
           'kodare_b': [{'citat': r['citat'], 'oppen_kod': r.get('oppen_kod')} for r in b if r['id'] == p['id']],
           'overens': (a_n.get(p['id'], 0) > 0) == (b_n.get(p['id'], 0) > 0)} for p in d]
    lika = sum(x['overens'] for x in pp)
    skriv(rid, 'kodning/dubbelidentifiering.json', {'_meta': {'steg': f'M1b oberoende identifiering av {len(pp)} slumpvis valda passager (≥ 100 tecken, frö {SEED_ID}) med samma instruktion; kodare A = M1',
                                                              'matt': 'överens = båda kodarna anger minst en utmaning, eller ingen av dem', 'overens': lika, 'antal': len(pp), 'tolkning': True}, 'passager': pp})
    print(f'{rid}: {len(utm)} utmaningar från {nk} kodare; identifiering överens {lika}/{len(pp)}')

def ej_dubbletter(rid):
    P = {p['id']: p for p in las(rid, 'passager.json')['passager']}
    return [{'id': u['id'], 'avsandare': u['avsandare'], 'citat': u['citat'], 'sammanhang': P[u['passage']]['text']}
            for u in las(rid, 'utmaningar.json')['utmaningar'] if not u['dublett_av']], P

def m2_underlag(rid):
    uu, _ = ej_dubbletter(rid)
    for i in range(0, len(uu), 120): ut(rid, f'm2-batch-{i // 120 + 1}.json', uu[i:i + 120])
    ut(rid, 'm2-dubbel.json', random.Random(SEED_TYP).sample(uu, min(N_STICKPROV, len(uu))))
    print(f'{rid}: {len(uu)} utmaningar att typa')

def kontrollera_typ(rader, ids, var, typer):
    sett = [r['id'] for r in rader]
    if sorted(sett) != sorted(ids): sys.exit(f'{var}: id stämmer inte (saknas {sorted(set(ids) - set(sett))[:5]}, dubbla/okända {sorted(set(x for x in sett if sett.count(x) > 1) | (set(sett) - set(ids)))[:5]})')
    fel = [r['id'] for r in rader if r['primar'] not in typer or (r.get('sekundar') not in typer and r.get('sekundar') is not None)]
    if fel: sys.exit(f'{var}: okända typnamn för {fel[:5]}')

def m2_ihop(rid):
    typer = {t[0] for t in gemensamt()['utmaningstyper']}; uu, _ = ej_dubbletter(rid)
    rader = []; batch_ids = []
    for n, r in resultat(rid, 'm2-resultat'):
        r = lista(r); ids = [x['id'] for x in inn(rid, f'm2-batch-{n}.json')]; kontrollera_typ(r, ids, f'm2-resultat-{n}', typer)
        rader += [{'id': x['id'], 'primar': x['primar'], 'sekundar': x.get('sekundar'), 'motivering': x['motivering'], 'kodare': n} for x in r]; batch_ids += ids
    if sorted(batch_ids) != sorted(u['id'] for u in uu): sys.exit('m2: batcherna täcker inte alla utmaningar (kör m2-underlag igen)')
    ordn = {u['id']: i for i, u in enumerate(uu)}; rader.sort(key=lambda x: ordn[x['id']])
    skriv(rid, 'kodning/utmaningstyp.json', {'_meta': {'steg': f'M2 utmaningstyp (modellkodning genom läsning, Sprint 17; {len(set(x["kodare"] for x in rader))} kodare med samma instruktion, KODINSTRUKTION.md)', 'tolkning': True}, 'kodning': rader})
    d = inn(rid, 'm2-dubbel.json'); b = lista(inn(rid, 'm2-dubbel-resultat.json')); kontrollera_typ(b, [x['id'] for x in d], 'm2-dubbel-resultat', typer)
    ordn = {x['id']: i for i, x in enumerate(d)}; b = sorted(b, key=lambda x: ordn[x['id']])
    skriv(rid, 'kodning/dubbelkodning.json', {'_meta': {'steg': f'M2b oberoende dubbelkodning av {len(b)} slumpvis valda utmaningar (frö {SEED_TYP}) för samstämmighet', 'tolkning': True},
                                              'kodning': [{'id': x['id'], 'primar': x['primar'], 'sekundar': x.get('sekundar'), 'motivering': x['motivering']} for x in b]})
    print(f'{rid}: {len(rader)} typade; dubbelkodade {len(b)}')

def m2c_underlag(rid):
    uu, _ = ej_dubbletter(rid); KOD = {x['id']: x for x in las(rid, 'kodning/utmaningstyp.json')['kodning']}
    sel = [dict(u, primar=KOD[u['id']]['primar']) for u in uu if KOD[u['id']]['primar'] in (OT, LI)]
    ut(rid, 'm2c-underlag.json', sel); print(f'{rid}: {len(sel)} utmaningar att regelpröva')

def m2c_ihop(rid):
    d = inn(rid, 'm2c-underlag.json'); r = lista(inn(rid, 'm2c-resultat.json')); kontrollera_typ(r, [x['id'] for x in d], 'm2c-resultat', {OT, LI})
    gammal = {x['id']: x['primar'] for x in d}; R = {x['id']: x for x in r}
    andr = [{'id': x['id'], 'gammal': gammal[x['id']], 'ny': R[x['id']]['primar'], 'motivering': R[x['id']]['motivering']} for x in d if R[x['id']]['primar'] != gammal[x['id']]]
    regel = gemensamt()['avgorande_regel']
    skriv(rid, 'kodning/regelprovning.json', {'_meta': {'steg': 'M2c regelprövning av primär utmaningstyp mot den avgörande regeln (en kodare, KODINSTRUKTION.md).', 'regel': regel,
                                                        'antal_provade': len(d), 'antal_andrade': len(andr), 'tolkning': True},
                                              'provade_id': [x['id'] for x in d], 'andringar': andr})
    print(f'{rid}: prövade {len(d)}, ändrade {len(andr)}')

def m3_underlag(rid):
    uu, _ = ej_dubbletter(rid); U = {u['id']: u for u in las(rid, 'utmaningar.json')['utmaningar']}
    if any(U[u['id']]['utmaningstyp'] is None for u in uu): sys.exit('kör M2 och K7 före m3-underlag')
    sel = [dict(u, rubrik_i_remissvaret=None) for u in uu if U[u['id']]['koppling']['niva'] is None]
    P = {p['id']: p for p in las(rid, 'passager.json')['passager']}
    sel = [{'uid': u['id'], 'avsandare': u['avsandare'], 'rubrik_i_remissvaret': P[U[u['id']]['passage']]['rubrik'], 'citat': u['citat'], 'passage': u['sammanhang']} for u in sel]
    h = (len(sel) + 1) // 2
    ut(rid, 'm3-batch-1.json', sel[:h]); ut(rid, 'm3-batch-2.json', sel[h:])
    ut(rid, 'm3-forslag.json', [{'id': b['id'], 'sou_avsnitt': b['avsnitt'], 'rubrik': b['avsnittsrubrik'], 'text': b['text']} for b in las(rid, 'sou-forslag.json')['forslag']])
    print(f'{rid}: {len(sel)} utmaningar utan egen hänvisning')

def m3_ihop(rid):
    F = {b['id'] for b in las(rid, 'sou-forslag.json')['forslag']}; rader = []
    for n, r in resultat(rid, 'm3-resultat'):
        r = lista(r); ids = [x['uid'] for x in inn(rid, f'm3-batch-{n}.json')]
        if sorted(x['uid'] for x in r) != sorted(ids): sys.exit(f'm3-resultat-{n}: uid stämmer inte med batchen')
        fel = [x['uid'] for x in r if any(f not in F for f in (x.get('forslag') or []))]
        if fel: sys.exit(f'm3-resultat-{n}: okända förslags-id för {fel[:5]}')
        rader += [{'uid': x['uid'], 'forslag': x.get('forslag') or None, 'motivering': x['motivering']} for x in r]
    rader.sort(key=lambda x: x['uid'])
    skriv(rid, 'kodning/tolkad-koppling.json', {'_meta': {'steg': 'M3 tolkad koppling till utredningsförslag för utmaningar utan egen hänvisning (modellkodning, Sprint 17; två kodare, KODINSTRUKTION.md)', 'tolkning': True}, 'kopplingar': rader})
    print(f'{rid}: {len(rader)} kopplingar, varav null {sum(1 for x in rader if not x["forslag"])}')

def m2d_underlag(rid):
    uu, _ = ej_dubbletter(rid)
    ut(rid, 'm2d-underlag.json', random.Random(SEED_TYP_EFTER).sample(uu, min(N_STICKPROV_EFTER, len(uu))))
    print(f'{rid}: {min(N_STICKPROV_EFTER, len(uu))} utmaningar för typning efter regelprövning')

def m2d_ihop(rid):
    typer = {t[0] for t in gemensamt()['utmaningstyper']}
    d = inn(rid, 'm2d-underlag.json'); b = lista(inn(rid, 'm2d-resultat.json')); kontrollera_typ(b, [x['id'] for x in d], 'm2d-resultat', typer)
    KOD = {x['id']: x['primar'] for x in las(rid, 'kodning/utmaningstyp.json')['kodning']}
    LOGG = {x['id']: x['ny'] for x in las(rid, 'kodning/regelprovning.json')['andringar']}
    ordn = {x['id']: i for i, x in enumerate(d)}; b = sorted(b, key=lambda x: ordn[x['id']])
    lika = sum(1 for x in b if LOGG.get(x['id'], KOD[x['id']]) == x['primar'])
    skriv(rid, 'kodning/dubbelkodning-efter-regelprovning.json', {'_meta': {'steg': f'M2d oberoende typning av {len(b)} slumpvis valda utmaningar (frö {SEED_TYP_EFTER}) jämförd med primär typ efter regelprövning (Sprint 17 A4)',
        'overens': lika, 'antal': len(b), 'tolkning': True}, 'kodning': [{'id': x['id'], 'primar': x['primar'], 'sekundar': x.get('sekundar'), 'motivering': x['motivering'],
        'efter_regelprovning': LOGG.get(x['id'], KOD[x['id']])} for x in b]})
    print(f'{rid}: typning efter regelprövning överens {lika}/{len(b)}')

KOM = {'m1-underlag': m1_underlag, 'm1-ihop': m1_ihop, 'm2-underlag': m2_underlag, 'm2-ihop': m2_ihop, 'm2c-underlag': m2c_underlag,
       'm2c-ihop': m2c_ihop, 'm2d-underlag': m2d_underlag, 'm2d-ihop': m2d_ihop, 'm3-underlag': m3_underlag, 'm3-ihop': m3_ihop}
if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[2] not in KOM: sys.exit(__doc__)
    config(sys.argv[1]); os.makedirs(mapp(sys.argv[1], 'kallor', 'kodning'), exist_ok=True); KOM[sys.argv[2]](sys.argv[1])
