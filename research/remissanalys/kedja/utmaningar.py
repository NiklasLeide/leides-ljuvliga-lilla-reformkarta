#!/usr/bin/env python3
"""Steg K7 (deterministiskt, efter modellkodningen M1–M3): utmaningar.json
För varje kodad utmaning (kodning/utmaningar.json):
  - citatkontroll: citatet (blanksteg och bindestreck normaliserade) ska finnas i källsidans text (remissvar.json)
  - dubbletter: samma avsändare och ≥ 90 % likhet med ett tidigare citat → dublett_av (räknas inte)
  - kopplingsnivå: remissvarets egen hänvisning (i passagen, annars rubriken den står under; paragrafer via författningskommentaren):
      avsnitt/rubrik/paragraf med förslagsruta → förslagen i avsnittet och dess underavsnitt (ingen förälderfallback)
      bara kapitel, eller avsnitt utan förslagsruta → nivån 'kapitel' (ingen expansion)
      ingen egen hänvisning → tolkad koppling ur kodning/tolkad-koppling.json (tolkning: true), annars null
  - skolform: mekanisk matchning mot skolformernas namn i citatet
  - utmaningstyp: kodning/utmaningstyp.json (tolkning: true); regelprövningen tillämpas i bygg.py
Förutsättning: passager.json (K6), remissvar.json (K5), sou-forslag.json och sou-paragrafer.json (K2), kodning/*.json (M1–M3).
Användning: python3 research/remissanalys/kedja/utmaningar.py <reform-id>"""
import difflib, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(__file__))
from gemensamt import reform_id, config, las, skriv, mapp, GRUPP

SKOLFORM = [('anpassad gymnasieskola', r'anpassad(?:e)? gymnasieskol\w*'), ('anpassad grundskola', r'anpassad(?:e)? grundskol\w*'),
            ('förskoleklass', r'förskoleklass\w*'), ('grundskola', r'grundskol\w*'), ('specialskola', r'specialskol\w*'), ('sameskola', r'sameskol\w*'),
            ('gymnasieskola', r'gymnasieskol\w*'), ('kommunal vuxenutbildning', r'kommunal(?:a)? vuxenutbildning\w*|komvux\w*|vuxenutbildning\w*')]
def skolformer(t):
    t = t.lower(); out = []
    for namn, rx in SKOLFORM:
        if re.search(r'\b(?:' + rx + r')', t): out.append(namn); t = re.sub(r'\b(?:' + rx + r')', ' ', t)
    return out

if __name__ == '__main__':
    rid = reform_id(); c = config(rid); dnr = c['remiss']['diarienummer']
    manuell_ocr = set((c.get('korrigeringar') or {}).get('ocr_citat_manuellt_kontrollerade') or [])
    P = {p['id']: p for p in las(rid, 'passager.json')['passager']}
    DOK = {d['id']: d for d in las(rid, 'remissvar.json')['publicerade']}
    boxes = las(rid, 'sou-forslag.json')['forslag']; BOX = {b['id']: b for b in boxes}
    PAR = {(p['kap'], p['par'].replace(' ', '')): p['avsnitt'] for p in las(rid, 'sou-paragrafer.json')['paragrafer'] if p['kap'] != 'ikraft'}
    # Före M2/M3 finns kodfilerna inte än: K7 körs då för att markera dubbletter (urvalet till M2) och ta fram
    # utmaningar utan egen hänvisning (urvalet till M3). utmaningstyp blir då null och tolkad koppling saknas.
    finns = lambda namn: os.path.exists(mapp(rid, namn))
    KT = {x['uid']: x for x in las(rid, 'kodning/tolkad-koppling.json')['kopplingar']} if finns('kodning/tolkad-koppling.json') else {}
    KOD = {x['id']: x for x in las(rid, 'kodning/utmaningstyp.json')['kodning']} if finns('kodning/utmaningstyp.json') else {}
    n = lambda t: re.sub(r'[\s\-­]', '', unicodedata.normalize('NFC', t))
    f_exact = lambda sec: [b['id'] for b in boxes if b['avsnitt'] == sec or b['avsnitt'].startswith(sec + '.')]
    def paragrafrefs(text):
        return [{'typ': 'paragraf', 'varde': f'{k[0]} kap. {k[1]} §', 'text': m.group(0), 'avsnitt': PAR[k]}
                for m in re.finditer(r'(\d{1,2}) kap\.\s*(\d{1,3}(?:\s?[a-z])?)\s*§', text) for k in [(m.group(1), m.group(2).replace(' ', ''))] if k in PAR]
    def forankrad_forstudie(p):
        """Om passagen var förankrad i förstudie 2 (då gjordes ingen tolkad koppling för den)."""
        return bool(p['forankrade_forslag'] or [f for h in paragrafrefs(p['text']) for a in h['avsnitt'] for f in f_exact(a)])
    def koppling(uid, p):
        egna = list(p['hanvisningar_egna']) + paragrafrefs(p['text'])
        refs = egna if egna else p['hanvisningar_rubrik']; kalla = 'remissvarets egen text' if egna else 'rubrik i remissvaret som passagen står under'
        fids = []; kap = set(); grund = []
        for h in refs:
            if h['typ'] in ('avsnitt', 'rubrik'):
                ff = f_exact(h['varde']); grund.append(h['text'])
                if ff: fids += ff
                else: kap.add(h['varde'].split('.')[0])
            elif h['typ'] == 'paragraf':
                grund.append(h['text'])
                for a in h['avsnitt']:
                    ff = f_exact(a); fids += ff
                    if not ff: kap.add(a.split('.')[0])
            elif h['typ'] == 'kapitel': kap.add(h['varde']); grund.append(h['text'])
        fids = sorted(set(fids), key=lambda x: int(x[1:]))
        if fids:
            return {'niva': 'förslag', 'forslag': fids, 'kapitel': sorted({BOX[f]['avsnitt'].split('.')[0] for f in fids}, key=int),
                    'flera_forslag_i_hanvisat_avsnitt': len(fids) > 1, 'grund': grund, 'kalla_for_grund': kalla, 'tolkning': False}
        if kap:
            return {'niva': 'kapitel', 'forslag': [], 'kapitel': sorted(kap, key=int), 'grund': grund, 'kalla_for_grund': kalla, 'tolkning': False,
                    'anm': 'Hänvisningen pekar på kapitel (eller avsnitt utan förslagsruta); ingen expansion till enskilda förslag.'}
        k = KT.get(uid)
        if k and k['forslag'] and not forankrad_forstudie(p):
            return {'niva': 'tolkad', 'forslag': k['forslag'], 'kapitel': sorted({BOX[f]['avsnitt'].split('.')[0] for f in k['forslag']}, key=int),
                    'motivering': k['motivering'], 'tolkning': True}
        return {'niva': None, 'forslag': [], 'kapitel': [], 'tolkning': False}
    ut = []
    for x in las(rid, 'kodning/utmaningar.json')['utmaningar']:
        p = P[x['id']]; d = DOK[p['dok']]
        auto = n(x['citat']) in n(d['text_per_sida'][p['sida'] - 1])
        metod = ('automatisk mot OCR-text + manuell mot sidbild' if x['uid'] in manuell_ocr else ('automatisk mot OCR-text' if p['ocr'] else 'automatisk mot pdftotext-sidtext')) if auto else 'manuell'
        ut.append({'id': x['uid'], 'passage': x['id'], 'avsandare': p['avsandare'], 'fokusgrupp': p['kategori_avsandare'], 'grupp': GRUPP[p['kategori_avsandare']],
                   'citat': x['citat'], 'sida': p['sida'], 'url': p['url'], 'ocr': p['ocr'],
                   'kalla': {'text': f"Remissvar från {p['avsandare']} ({dnr}), s. {p['sida']}" + (' (OCR)' if p['ocr'] else ''), 'url': p['url']},
                   'citatkontroll': {'metod': metod, 'ok': True if auto else None}})
    for i, a in enumerate(ut):
        a['dublett_av'] = next((b['id'] for b in ut[:i] if a['avsandare'] == b['avsandare'] and difflib.SequenceMatcher(None, a['citat'], b['citat']).ratio() >= 0.9), None)
    for u in ut:
        if u['dublett_av']: continue
        k = KOD.get(u['id']) if KOD else None
        if KOD and k is None: sys.exit(f"{u['id']} saknas i kodning/utmaningstyp.json")
        u['utmaningstyp'] = {'primar': k['primar'], 'sekundar': k['sekundar'] if k['sekundar'] != k['primar'] else None, 'motivering': k['motivering'], 'tolkning': True} if k else None
        u['koppling'] = koppling(u['id'], P[u['passage']])
        u['skolform'] = skolformer(u['citat'])
    skriv(rid, 'utmaningar.json', {'_meta': {'beskrivning': 'Kodade utmaningar med citatkontroll, dubbletter, kopplingsnivå, skolform och utmaningstyp.'}, 'utmaningar': ut})
    uu = [u for u in ut if not u['dublett_av']]
    print(f"{rid}: {len(ut)} kodade, {len(uu)} efter dubbletter; citat utan automatisk träff: {sum(1 for u in ut if u['citatkontroll']['ok'] is None)}")
