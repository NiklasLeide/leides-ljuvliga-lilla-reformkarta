#!/usr/bin/env python3
"""Steg K6 (deterministiskt): remissvar.json → passager.json
Delar varje publicerat remissvar i passager (stycken) och hittar remissvarets egna hänvisningar till utredningen:
avsnittsnummer, kapitel och SOU-rubriker (ur innehållsförteckningen) i passagen eller i rubriken den står under.
Sidhuvuden/sidfötter (block som upprepas ≥ 3 gånger i samma dokument) tas bort.
Konfiguration: sou.forslagskapitel. Förutsättning: remissvar.json (K5), sou-innehall.json och sou-forslag.json (K2).
Användning: python3 research/remissanalys/kedja/segmentera.py <reform-id>"""
import collections, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from gemensamt import reform_id, config, las, skriv, kravs

if __name__ == '__main__':
    rid = reform_id(); c = config(rid)
    kmin, kmax = kravs(c, 'sou', 'forslagskapitel')
    K = las(rid, 'remissvar.json'); toc = las(rid, 'sou-innehall.json')['lista']; boxes = las(rid, 'sou-forslag.json')['forslag']
    TOC = {t['avsnitt']: t['rubrik'] for t in toc if kmin <= int(t['avsnitt'].split('.')[0]) <= kmax}
    norm = lambda s: re.sub(r'\s+', ' ', s.replace('­', '')).strip()
    low = lambda s: re.sub(r'[^a-zåäöé0-9 ]', '', norm(s).lower())
    RUBRIK = {low(v): k for k, v in TOC.items() if len(v) >= 12}
    def f_for(sec):
        """Förslag som en hänvisning pekar på (som i förstudie 2): kapitel → alla förslag i kapitlet; avsnitt → avsnittet och dess
        underavsnitt, annars förälderavsnittet. Används för passagens 'forankrade_forslag' (urvalet till SFS-jämförelsen)."""
        if '.' not in sec: return [b['id'] for b in boxes if b['avsnitt'].split('.')[0] == sec]
        ids = [b['id'] for b in boxes if b['avsnitt'] == sec or b['avsnitt'].startswith(sec + '.')]
        if not ids and '.' in sec:
            par = sec.rsplit('.', 1)[0]; ids = [b['id'] for b in boxes if b['avsnitt'] == par]
        return ids
    KAP = '|'.join(str(k) for k in range(kmin, kmax + 1))
    SECRX = re.compile(r'(?<![\d.,§:/])(?:avsnitt(?:en)?|kapitel|kap\.?)?\s*(\d{1,2}(?:\.\d{1,2}){1,3})(?![\d,]|\s*§|\s*kap)', re.I)
    CHAPRX = re.compile(r'\b(?:kapitel|kap\.)\s+((?:' + KAP + r')(?:(?:,\s*|\s+och\s+)(?:' + KAP + r'))*)\b(?!\s*(?:§|kap|\.\d))', re.I)
    def hanvisningar(t):
        h = [{'typ': 'avsnitt', 'varde': m.group(1), 'text': norm(m.group(0))} for m in SECRX.finditer(t) if m.group(1) in TOC]
        for m in CHAPRX.finditer(t):
            for k in re.findall(r'\d+', m.group(1)): h.append({'typ': 'kapitel', 'varde': k, 'text': norm(m.group(0))})
        lt = low(t)
        for r, sec in RUBRIK.items():
            if r and r in lt and len(lt) < len(r) + 40: h.append({'typ': 'rubrik', 'varde': sec, 'text': norm(t)[:120]})
        return h
    def is_heading(t):
        t = norm(t); return 0 < len(t) < 130 and not re.search(r'[.:;]\s*$', t) and not re.search(r'\b(och|att|som|för|med|är)$', t)
    HEADSPLIT = re.compile(r'(?<=[.!?”"\)])\s+(?=(?:Kapitel\s+\d{1,2}\b|\d{1,2}(?:\.\d{1,2}){1,3}\s+[A-ZÅÄÖ]))')
    def split_heading(t):
        m = re.match(r'(?:\d+\(\d+\)\s*)?(?:Kapitel\s+\d{1,2}[:.]?\s*[^.]*?\s+)?(\d{1,2}(?:\.\d{1,2}){1,3})\s+(.*)$', t)
        if m and m.group(1) in TOC:
            title = TOC[m.group(1)]; rest = m.group(2)
            if low(rest).startswith(low(title)[:max(10, len(low(title)) - 3)]):
                n = len(title.split()); words = rest.split()
                return t[:len(t) - len(' '.join(words[n:]))].strip() if words[n:] else t, ' '.join(words[n:])
        return None, None
    passager = []
    for d in K['publicerade']:
        allblocks = [norm(re.sub(r'(\w)-\n(\w)', r'\1\2', bl).replace('\n', ' ')) for pg in d['text_per_sida'] for bl in re.split(r'\n\s*\n', pg)]
        rep = {b for b, n_ in collections.Counter(re.sub(r'\d+', '#', x) for x in allblocks).items() if n_ >= 3 and len(b) < 200}
        rub = None; rub_h = []; n = 0
        for si, page in enumerate(d['text_per_sida'], start=1):
            for bl in re.split(r'\n\s*\n', page.replace('\r', '')):
                t0 = norm(re.sub(r'(\w)-\n(\w)', r'\1\2', bl).replace('\n', ' '))
                if len(t0) < 3 or re.fullmatch(r'[\d\s()/]+', t0) or re.sub(r'\d+', '#', t0) in rep: continue
                for t in HEADSPLIT.split(t0):
                    h_t, body = split_heading(t)
                    if h_t:
                        rub = h_t; rub_h = hanvisningar(h_t)
                        if not body or len(body) < 25: continue
                        t = body
                    h = hanvisningar(t)
                    if is_heading(t):
                        rub = t; rub_h = h
                        if len(t) < 25: continue
                    n += 1
                    egna = h; arvda = [] if h else rub_h
                    secs = [x['varde'] for x in egna + arvda if x['typ'] in ('avsnitt', 'rubrik', 'kapitel')]
                    fids = sorted({f for s_ in secs for f in f_for(s_)}, key=lambda x: int(x[1:]))
                    passager.append({'id': f"{d['id']}#{n}", 'dok': d['id'], 'avsandare': d['avsandare'], 'kategori_avsandare': d['kategori'], 'url': d['url'],
                                     'sida': si, 'ocr': d['ocr'], 'text': t, 'rubrik': rub, 'hanvisningar_egna': egna, 'hanvisningar_rubrik': arvda, 'forankrade_forslag': fids})
    skriv(rid, 'passager.json', {'_meta': {'beskrivning': 'Remissvaren segmenterade i passager med remissvarets egna hänvisningar.', 'antal': len(passager)}, 'passager': passager})
    print(f'{rid}: {len(passager)} passager')
